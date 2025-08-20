"""
WAR KRS Controller
Main controller orchestrating the WAR KRS process
"""

import time
import os
from typing import Dict, Set, List
import logging
from datetime import datetime

from .session import SiakadSession
from .krs_service import KRSService
from .telegram_notifier import TelegramNotifier

logger = logging.getLogger(__name__)


class WARKRSController:
    """
    Main controller for WAR KRS automation
    Follows SOLID principles and implements the main business logic
    """
    
    def __init__(self, cookies: Dict[str, str], urls: Dict[str, str], 
                 target_courses: Dict[str, str], settings: Dict, telegram_config: Dict = None,
                 debug_mode: bool = False):
        """
        Initialize WAR KRS controller
        
        Args:
            cookies: Authentication cookies
            urls: SIAKAD URLs
            target_courses: Target courses mapping (code -> class_id)
            settings: Configuration settings
            telegram_config: Telegram configuration (optional)
            debug_mode: Enable debug mode for troubleshooting
        """
        self.target_courses = target_courses.copy()
        self.settings = settings
        self.debug_mode = debug_mode
        self.start_time = datetime.now()
        self.successful_courses = []
        
        # Initialize session and service
        self.session = SiakadSession(cookies, settings.get('request_timeout', 20))
        self.krs_service = KRSService(self.session, urls)
        
        # Initialize Telegram notifier
        if telegram_config and telegram_config.get('bot_token') and telegram_config.get('chat_id'):
            self.telegram = TelegramNotifier(
                bot_token=telegram_config['bot_token'],
                chat_id=telegram_config['chat_id']
            )
        else:
            self.telegram = None
        
        # Track remaining targets and cycle metrics
        self.remaining_targets = set(target_courses.keys())
        self.cycle_count = 0
        self.last_activity = None
        self.session_warnings_count = 0
        self.last_heartbeat_cycle = 0
    
    def clear_screen(self) -> None:
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def display_status(self) -> tuple[bool, dict]:
        """
        Display current status of WAR KRS process
        
        Returns:
            Tuple of (session_valid, session_status)
        """
        self.clear_screen()
        print("=" * 50)
        print("    WAR KRS OTOMATIS SIAKAD ITERA")
        print("=" * 50)
        print(f"Cycle: #{self.cycle_count} | Target Tersisa: {', '.join(sorted(self.remaining_targets))}")
        print("=" * 50)
        print()
        
        # Show currently enrolled courses with session validation
        enrolled, session_status = self.krs_service.get_enrolled_courses(debug_mode=self.debug_mode)
        enrolled_str = ', '.join(sorted(enrolled)) if enrolled else 'Tidak ada'
        print(f"MK Terdaftar Saat Ini: {enrolled_str}")
        
        # Show session status
        if not session_status['session_valid']:
            print(f"⚠️  Session Status: INVALID (Confidence: {session_status['confidence_score']}%)")
            print(f"    Action: {session_status['recommended_action']}")
        else:
            print("✅ Session Status: VALID")
        
        if self.debug_mode:
            print("🔍 DEBUG MODE: HTML content saved to debug_enrolled_courses.html")
        
        # Show Telegram status
        if self.telegram and self.telegram.is_enabled():
            print("📱 Telegram notifications: ENABLED")
        else:
            print("📱 Telegram notifications: DISABLED")
        print()
        
        return session_status['session_valid'], session_status
    
    def process_single_course(self, course_code: str) -> tuple[bool, dict]:
        """
        Process registration for a single course
        
        Args:
            course_code: Course code to process
            
        Returns:
            Tuple of (success, session_status)
        """
        class_id = self.target_courses[course_code]
        
        # Check if already enrolled with session validation
        is_enrolled, session_status = self.krs_service.is_course_enrolled(course_code)
        
        if not session_status['session_valid']:
            return False, session_status
        
        if is_enrolled:
            print(f"✔️  [{course_code}] sudah ada di KRS. Menghapus dari target.")
            self.remaining_targets.discard(course_code)
            self.successful_courses.append(course_code)
            self.last_activity = f"Course {course_code} already enrolled"
            return True, session_status
        
        print(f"⏳  Mencoba mendaftarkan [{course_code}] dengan ID Kelas: {class_id}...")
        
        try:
            # Attempt registration and verification
            success = self.krs_service.register_and_verify(
                course_code, 
                class_id, 
                self.settings.get('verification_delay', 2)
            )
            
            if success:
                print(f"✅  BERHASIL! [{course_code}] telah ditambahkan ke KRS.")
                self.remaining_targets.discard(course_code)
                self.successful_courses.append(course_code)
                self.last_activity = f"Successfully registered {course_code}"
                
                # Send immediate success notification
                if self.telegram and self.telegram.is_enabled():
                    self.telegram.notify_course_success(course_code)
                
                return True, session_status
            else:
                print(f"❌  GAGAL. [{course_code}] belum masuk KRS. (Kemungkinan kuota penuh atau sudah diambil).")
                self.last_activity = f"Failed to register {course_code}"
                return False, session_status
                
        except Exception as e:
            print(f"[ERROR] Terjadi kesalahan jaringan saat mencoba mendaftar [{course_code}]: {e}")
            self.last_activity = f"Error registering {course_code}: {str(e)}"
            logger.error(f"Error processing course {course_code}: {e}")
            return False, session_status
    
    def run_single_cycle(self) -> tuple[bool, dict, List[str], List[str]]:
        """
        Run a single cycle of course registration attempts
        
        Returns:
            Tuple of (session_valid, session_status, successful_courses, failed_courses)
        """
        self.cycle_count += 1
        session_valid, session_status = self.display_status()
        
        # If session is invalid, handle appropriately
        if not session_valid:
            return self.handle_session_error(session_status)
        
        attempted_courses = list(self.remaining_targets)
        successful_this_cycle = []
        failed_this_cycle = []
        
        for course_code in attempted_courses:
            success, updated_session_status = self.process_single_course(course_code)
            
            # Update session status if it changed
            if not updated_session_status['session_valid']:
                return self.handle_session_error(updated_session_status)
            
            if success:
                successful_this_cycle.append(course_code)
            else:
                failed_this_cycle.append(course_code)
            
            # Short delay between requests in the same cycle
            inter_delay = self.settings.get('inter_request_delay', 2)
            if inter_delay > 0 and course_code != attempted_courses[-1]:  # No delay after last course
                time.sleep(inter_delay)
        
        return True, session_status, successful_this_cycle, failed_this_cycle
    
    def handle_session_error(self, session_status: dict) -> tuple[bool, dict, List[str], List[str]]:
        """
        Handle session expiration or authentication errors
        
        Args:
            session_status: Session status dictionary
            
        Returns:
            Tuple indicating session error
        """
        action = session_status.get('recommended_action', 'unknown')
        
        # Send warning notification
        if self.telegram and self.telegram.is_enabled():
            self.telegram.notify_session_warning(session_status, self.cycle_count)
        
        if action == 'stop_and_reauth':
            print("\n🚨 CRITICAL: Session expired detected!")
            print("   Program akan dihentikan untuk menghindari error.")
            print("   Silakan:")
            print("   1. Login ulang ke SIAKAD ITERA")
            print("   2. Update cookies di file .env")  
            print("   3. Restart aplikasi")
            return False, session_status, [], []
        elif action == 'warn_and_continue':
            print("\n⚠️  WARNING: Possible session issues detected")
            print("   Program akan continue tapi perlu monitoring")
            self.session_warnings_count += 1
            
            # If too many warnings, escalate to stop
            if self.session_warnings_count >= 3:
                print("   Too many session warnings - stopping for safety")
                return False, session_status, [], []
                
            return True, session_status, [], []
        else:
            # Continue with increased monitoring
            return True, session_status, [], []
    
    def should_send_cycle_notification(self, successful_this_cycle: List[str], 
                                     failed_this_cycle: List[str]) -> bool:
        """
        Determine if cycle notification should be sent
        
        Args:
            successful_this_cycle: Courses that succeeded this cycle
            failed_this_cycle: Courses that failed this cycle
            
        Returns:
            True if notification should be sent
        """
        # Always send if there were successes
        if successful_this_cycle:
            return True
            
        # Send summary every 5 cycles if there are failures
        if failed_this_cycle and self.cycle_count % 5 == 0:
            return True
            
        # Send heartbeat every 10 cycles to show system is alive
        if self.cycle_count % 10 == 0:
            return True
            
        return False
    
    def should_send_heartbeat(self) -> bool:
        """
        Determine if heartbeat notification should be sent
        
        Returns:
            True if heartbeat should be sent
        """
        # Send heartbeat every 20 cycles (roughly every 15-20 minutes)
        return self.cycle_count % 20 == 0 and self.cycle_count > self.last_heartbeat_cycle
    
    def run_single_cycle_old(self) -> None:
        """Run a single cycle of course registration attempts"""
        self.display_status()
        
        for course_code in list(self.remaining_targets):
            self.process_single_course(course_code)
            
            # Short delay between requests in the same cycle
            inter_delay = self.settings.get('inter_request_delay', 2)
            if inter_delay > 0:
                time.sleep(inter_delay)
    
    def run(self) -> None:
        """
        Main execution method for WAR KRS automation with enhanced monitoring
        Runs continuously until all target courses are obtained
        """
        logger.info("Starting WAR KRS automation")
        
        if not self.remaining_targets:
            print("❌ Tidak ada mata kuliah target yang dikonfigurasi.")
            return
        
        # Send start notification
        if self.telegram and self.telegram.is_enabled():
            self.telegram.notify_start(list(self.remaining_targets))
        
        delay_seconds = self.settings.get('delay_seconds', 45)
        
        try:
            while self.remaining_targets:
                try:
                    # Run single cycle with enhanced monitoring
                    session_valid, session_status, successful_this_cycle, failed_this_cycle = self.run_single_cycle()
                    
                    # Handle session errors
                    if not session_valid:
                        logger.warning("Session invalid - stopping automation")
                        break
                    
                    # Calculate elapsed time
                    elapsed = datetime.now() - self.start_time
                    elapsed_str = str(elapsed).split('.')[0]  # Remove microseconds
                    
                    # Send cycle notifications if appropriate
                    if self.telegram and self.telegram.is_enabled():
                        if self.should_send_cycle_notification(successful_this_cycle, failed_this_cycle):
                            self.telegram.notify_cycle_summary(
                                cycle_number=self.cycle_count,
                                attempted_courses=successful_this_cycle + failed_this_cycle,
                                successful_courses=successful_this_cycle,
                                failed_courses=failed_this_cycle,
                                elapsed_time=elapsed_str,
                                next_attempt_in=delay_seconds if self.remaining_targets else None
                            )
                        elif self.should_send_heartbeat():
                            self.telegram.notify_heartbeat(
                                cycles_completed=self.cycle_count,
                                total_time=elapsed_str,
                                remaining_courses=list(self.remaining_targets),
                                last_activity=self.last_activity
                            )
                            self.last_heartbeat_cycle = self.cycle_count
                    
                    # Break if all courses completed
                    if not self.remaining_targets:
                        break
                    
                    print(f"\\n--- Cycle #{self.cycle_count} selesai. Menunggu {delay_seconds} detik "
                          "sebelum memulai siklus berikutnya ---")
                    time.sleep(delay_seconds)
                    
                except KeyboardInterrupt:
                    print("\\n\\n⏹️  Proses dihentikan oleh user.")
                    logger.info("Process interrupted by user")
                    if self.telegram and self.telegram.is_enabled():
                        self.telegram.notify_error("Proses dihentikan oleh user")
                    break
                except Exception as e:
                    logger.error(f"Error in main cycle: {e}")
                    print(f"\\n❌ Error dalam siklus utama: {e}")
                    
                    # Send error notification
                    if self.telegram and self.telegram.is_enabled():
                        self.telegram.notify_error(str(e))
                    
                    # Wait a bit before retrying
                    time.sleep(min(delay_seconds, 60))  # Max 60 seconds wait on error
            
            # Success completion
            if not self.remaining_targets:
                elapsed = datetime.now() - self.start_time
                hours, remainder = divmod(int(elapsed.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                time_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
                
                print("\\n🎉 SELAMAT! Semua mata kuliah target telah berhasil diproses.")
                logger.info("All target courses successfully processed")
                
                # Send completion notification
                if self.telegram and self.telegram.is_enabled():
                    self.telegram.notify_all_completed(self.successful_courses, time_str)
            
        except Exception as e:
            logger.error(f"Fatal error in WAR KRS automation: {e}")
            print(f"\\n💥 Error fatal: {e}")
            
            # Send critical error notification
            if self.telegram and self.telegram.is_enabled():
                self.telegram.notify_error(f"Fatal error: {str(e)}")
            raise
        
        logger.info("WAR KRS automation finished")
