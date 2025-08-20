"""
Telegram Notification Service
Handles sending notifications via Telegram Bot API
"""

import asyncio
import logging
import requests
from typing import Optional, List
from datetime import datetime
import os
import threading
import concurrent.futures

try:
    from telegram import Bot
    from telegram.error import TelegramError
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Telegram notification service for WAR KRS automation
    Follows Single Responsibility Principle
    """
    
    def __init__(self, bot_token: Optional[str] = None, chat_id: Optional[str] = None):
        """
        Initialize Telegram notifier
        
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID to send messages to
        """
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.bot = None
        self.enabled = False
        
        if not TELEGRAM_AVAILABLE:
            logger.warning("python-telegram-bot not installed. Telegram notifications disabled.")
            return
        
        if self.bot_token and self.chat_id:
            try:
                self.bot = Bot(token=self.bot_token)
                self.enabled = True
                logger.info("Telegram notifications enabled")
            except Exception as e:
                logger.error(f"Failed to initialize Telegram bot: {e}")
        else:
            logger.info("Telegram credentials not configured. Notifications disabled.")
    
    def is_enabled(self) -> bool:
        """Check if Telegram notifications are enabled"""
        return self.enabled and self.bot is not None
    
    async def _send_message_async(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message asynchronously
        
        Args:
            message: Message to send
            parse_mode: Telegram parse mode (HTML, Markdown, etc.)
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_enabled():
            return False
        
        try:
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=message,
                parse_mode=parse_mode
            )
            return True
        except TelegramError as e:
            logger.error(f"Failed to send Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message synchronously (wrapper for async function)
        
        Args:
            message: Message to send
            parse_mode: Telegram parse mode
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.is_enabled():
            logger.debug("Telegram notifications disabled, skipping message")
            return False
        
        # Use requests-based approach as fallback for asyncio issues
        return self._send_message_requests(message, parse_mode)
    
    def _send_message_requests(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message using requests library (synchronous, no asyncio issues)
        
        Args:
            message: Message to send
            parse_mode: Telegram parse mode
            
        Returns:
            True if message sent successfully, False otherwise
        """
        if not self.bot_token or not self.chat_id:
            return False
            
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': message,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                logger.debug("Telegram message sent successfully")
                return True
            else:
                logger.error(f"Failed to send Telegram message: HTTP {response.status_code} - {response.text}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error sending Telegram message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending Telegram message: {e}")
            return False
    
    def _send_message_async_safe(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send message with safe asyncio handling (backup method)
        
        Args:
            message: Message to send
            parse_mode: Telegram parse mode
            
        Returns:
            True if message sent successfully, False otherwise
        """
        try:
            # Check if there's already an event loop running
            try:
                loop = asyncio.get_running_loop()
                # If there's already a loop, we can't use run_until_complete
                # So we'll run it in a thread
                
                def run_in_thread():
                    new_loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(new_loop)
                    try:
                        result = new_loop.run_until_complete(self._send_message_async(message, parse_mode))
                        return result
                    finally:
                        new_loop.close()
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(run_in_thread)
                    return future.result(timeout=30)  # 30 second timeout
                    
            except RuntimeError:
                # No event loop running, safe to create one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    result = loop.run_until_complete(self._send_message_async(message, parse_mode))
                    return result
                finally:
                    loop.close()
                    
        except Exception as e:
            logger.error(f"Failed to send Telegram message via async: {e}")
            # Fallback to requests method
            return self._send_message_requests(message, parse_mode)
    
    def notify_start(self, target_courses: List[str]) -> bool:
        """
        Notify that WAR KRS automation has started
        
        Args:
            target_courses: List of target course codes
            
        Returns:
            True if notification sent successfully
        """
        courses_list = "\n".join([f"• <code>{code}</code>" for code in target_courses])
        message = f"""
🚀 <b>WAR KRS DIMULAI</b>

📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎯 <b>Target Mata Kuliah:</b>
{courses_list}

⏳ Sistem akan terus mencoba mendaftarkan mata kuliah hingga berhasil...
        """.strip()
        
        return self.send_message(message)
    
    def notify_course_success(self, course_code: str, course_name: str = None) -> bool:
        """
        Notify successful course registration
        
        Args:
            course_code: Course code that was registered
            course_name: Optional course name
            
        Returns:
            True if notification sent successfully
        """
        name_text = f" - {course_name}" if course_name else ""
        message = f"""
✅ <b>MATA KULIAH BERHASIL DITAMBAHKAN!</b>

📚 <b>Mata Kuliah:</b> <code>{course_code}</code>{name_text}
📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎉 Selamat! Mata kuliah berhasil masuk ke KRS Anda.
        """.strip()
        
        return self.send_message(message)
    
    def notify_cycle_summary(self, cycle_number: int, attempted_courses: List[str], 
                           successful_courses: List[str], failed_courses: List[str],
                           elapsed_time: str, next_attempt_in: int = None) -> bool:
        """
        Send cycle summary notification
        
        Args:
            cycle_number: Current cycle number
            attempted_courses: Courses attempted in this cycle
            successful_courses: Courses successfully registered in this cycle
            failed_courses: Courses that failed in this cycle
            elapsed_time: Total elapsed time
            next_attempt_in: Seconds until next attempt
            
        Returns:
            True if notification sent successfully
        """
        if not attempted_courses:
            return False  # Don't send empty cycle notifications
            
        # Build status summary
        status_lines = []
        if successful_courses:
            success_list = "\n".join([f"✅ <code>{code}</code>" for code in successful_courses])
            status_lines.append(f"<b>Berhasil:</b>\n{success_list}")
        
        if failed_courses:
            failed_list = "\n".join([f"❌ <code>{code}</code>" for code in failed_courses])
            status_lines.append(f"<b>Gagal:</b>\n{failed_list}")
        
        status_text = "\n\n".join(status_lines) if status_lines else "Tidak ada perubahan"
        
        next_text = f"\n⏰ <b>Percobaan berikutnya:</b> {next_attempt_in} detik" if next_attempt_in else ""
        
        message = f"""
🔄 <b>CYCLE #{cycle_number} SUMMARY</b>

⏱️ <b>Total Waktu:</b> {elapsed_time}
🎯 <b>Dicoba:</b> {len(attempted_courses)} mata kuliah

{status_text}{next_text}

💡 Sistem tetap berjalan dan memantau...
        """.strip()
        
        return self.send_message(message)
    
    def notify_session_warning(self, session_status: dict, cycle_number: int = None) -> bool:
        """
        Notify about session/authentication issues
        
        Args:
            session_status: Session status dictionary from parser
            cycle_number: Optional current cycle number
            
        Returns:
            True if notification sent successfully
        """
        confidence = session_status.get('confidence_score', 0)
        action = session_status.get('recommended_action', 'unknown')
        errors = session_status.get('error_indicators', [])
        
        cycle_text = f" (Cycle #{cycle_number})" if cycle_number else ""
        
        if action == 'stop_and_reauth':
            icon = "🚨"
            title = "CRITICAL: SESSION EXPIRED"
            action_text = """
🔧 <b>ACTION REQUIRED:</b>
1. Login ulang ke SIAKAD ITERA
2. Update cookies di file .env
3. Restart aplikasi WAR KRS

⚠️ Program akan berhenti untuk menghindari error."""
        elif action == 'warn_and_continue':
            icon = "⚠️"
            title = "WARNING: Possible Session Issues"
            action_text = """
💡 <b>RECOMMENDED:</b>
- Monitor aplikasi closely
- Siapkan cookies baru jika diperlukan
- Program akan continue tapi waspada"""
        else:
            icon = "🔍"
            title = "Session Monitoring Alert"
            action_text = "Program akan continue dengan monitoring ketat"
        
        error_list = "\n".join([f"• {error}" for error in errors[:5]])  # Limit to 5 errors
        
        message = f"""
{icon} <b>{title}</b>{cycle_text}

🔒 <b>Confidence:</b> {confidence}%
📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🐛 <b>Indicators:</b>
{error_list}

{action_text}
        """.strip()
        
        return self.send_message(message)
    
    def notify_heartbeat(self, cycles_completed: int, total_time: str, 
                        remaining_courses: List[str], last_activity: str = None) -> bool:
        """
        Send heartbeat notification to show system is still running
        
        Args:
            cycles_completed: Number of cycles completed
            total_time: Total elapsed time
            remaining_courses: Courses still being attempted
            last_activity: Last significant activity
            
        Returns:
            True if notification sent successfully
        """
        remaining_list = "\n".join([f"🎯 <code>{code}</code>" for code in remaining_courses])
        activity_text = f"\n📝 <b>Last Activity:</b> {last_activity}" if last_activity else ""
        
        message = f"""
💓 <b>HEARTBEAT - System Running</b>

⏱️ <b>Runtime:</b> {total_time}
🔄 <b>Cycles:</b> {cycles_completed}
📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

🎯 <b>Still Targeting:</b>
{remaining_list}{activity_text}

✅ System healthy and continuing...
        """.strip()
        
        return self.send_message(message)
    
    def notify_all_completed(self, successful_courses: List[str], total_time: str = None) -> bool:
        """
        Notify that all target courses have been completed
        
        Args:
            successful_courses: List of successfully registered courses
            total_time: Optional total execution time
            
        Returns:
            True if notification sent successfully
        """
        courses_list = "\n".join([f"✅ <code>{code}</code>" for code in successful_courses])
        time_text = f"\n⏱️ <b>Total Waktu:</b> {total_time}" if total_time else ""
        
        message = f"""
🎉 <b>WAR KRS SELESAI - SEMUA TARGET BERHASIL!</b>

📅 <b>Waktu Selesai:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{time_text}

📚 <b>Mata Kuliah yang Berhasil:</b>
{courses_list}

🏆 Selamat! Semua mata kuliah target telah berhasil didaftarkan ke KRS Anda.
        """.strip()
        
        return self.send_message(message)
    
    def notify_error(self, error_message: str, course_code: str = None) -> bool:
        """
        Notify about errors
        
        Args:
            error_message: Error message to send
            course_code: Optional course code related to error
            
        Returns:
            True if notification sent successfully
        """
        course_text = f"\n📚 <b>Mata Kuliah:</b> <code>{course_code}</code>" if course_code else ""
        message = f"""
❌ <b>WAR KRS ERROR</b>

📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}{course_text}

🚨 <b>Error:</b> {error_message}

💡 Silakan periksa aplikasi atau coba restart.
        """.strip()
        
        return self.send_message(message)
    
    def notify_session_expired(self) -> bool:
        """
        Notify that session has expired
        
        Returns:
            True if notification sent successfully
        """
        message = f"""
🔒 <b>SESSION EXPIRED</b>

📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

⚠️ Session SIAKAD Anda telah expired. Silakan:
1. Login ulang ke SIAKAD ITERA
2. Update cookies di file .env
3. Restart aplikasi WAR KRS

💡 Gunakan <code>python setup.py</code> untuk update cookies.
        """.strip()
        
        return self.send_message(message)
    
    def test_connection(self) -> bool:
        """
        Test Telegram connection with multiple methods
        
        Returns:
            True if connection test successful
        """
        if not self.bot_token or not self.chat_id:
            logger.error("Telegram credentials not configured")
            return False
        
        message = f"""
🧪 <b>TEST KONEKSI TELEGRAM</b>

📅 <b>Waktu:</b> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

✅ Koneksi Telegram berhasil! WAR KRS siap mengirim notifikasi.
        """.strip()
        
        # Try requests method first (most reliable)
        logger.info("Testing Telegram connection using requests method...")
        if self._send_message_requests(message):
            logger.info("Telegram test successful using requests method")
            return True
        
        # Fallback to async method if requests fails
        if TELEGRAM_AVAILABLE and self.bot:
            logger.info("Trying async method as fallback...")
            try:
                result = self._send_message_async_safe(message)
                if result:
                    logger.info("Telegram test successful using async method")
                    return True
            except Exception as e:
                logger.error(f"Async method also failed: {e}")
        
        logger.error("All Telegram test methods failed")
        return False
    
    def get_connection_status(self) -> dict:
        """
        Get detailed connection status for debugging
        
        Returns:
            Dictionary with connection status details
        """
        status = {
            'enabled': self.enabled,
            'telegram_available': TELEGRAM_AVAILABLE,
            'bot_token_configured': bool(self.bot_token),
            'chat_id_configured': bool(self.chat_id),
            'bot_initialized': self.bot is not None,
            'last_test_result': None,
            'api_endpoint': f"https://api.telegram.org/bot{self.bot_token[:10]}...{self.bot_token[-10:]}" if self.bot_token else None
        }
        
        # Quick test
        if self.is_enabled():
            try:
                test_message = "🔧 Connection status check"
                status['last_test_result'] = self._send_message_requests(test_message)
            except Exception as e:
                status['last_test_result'] = False
                status['last_error'] = str(e)
        
        return status
