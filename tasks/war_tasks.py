"""
WAR KRS Background Tasks using Celery
Implementation following existing business logic patterns
"""

import time
import json
import logging
import sys
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from celery import current_task
from celery.exceptions import Retry
from celery_app import celery_app

# Add parent directory to path for imports (fix for Celery worker)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import existing business logic
try:
    from src.controller import WARKRSController
    from src.telegram_notifier import TelegramNotifier
    CONTROLLER_AVAILABLE = True
    print("✅ Business logic imported successfully in Celery task")
except ImportError as e:
    print(f"⚠️  Warning: Could not import existing business logic: {e}")
    CONTROLLER_AVAILABLE = False

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, name='tasks.war_tasks.run_war_task')
def run_war_task(self, user_id: int, session_id: int, cookies: Dict[str, str], 
                 urls: Dict[str, str], target_courses: Dict[str, str], 
                 settings: Dict, telegram_config: Optional[Dict] = None):
    """
    Main WAR KRS background task using Celery
    Follows existing controller pattern with enhanced monitoring
    
    Args:
        user_id: User ID from database
        session_id: WAR session ID from database  
        cookies: SIAKAD authentication cookies
        urls: SIAKAD URLs configuration
        target_courses: Target courses mapping (code -> class_id)
        settings: WAR settings configuration
        telegram_config: Telegram notification configuration
    
    Returns:
        Dict with task results and statistics
    """
    
    if not CONTROLLER_AVAILABLE:
        logger.error("Controller not available - cannot run WAR task")
        return {'status': 'error', 'message': 'Controller not available'}
    
    try:
        # Update task state to PROGRESS
        self.update_state(
            state='PROGRESS',
            meta={
                'status': 'initializing',
                'user_id': user_id,
                'session_id': session_id,
                'cycle': 0,
                'successful_courses': [],
                'remaining_targets': list(target_courses.keys()),
                'started_at': datetime.utcnow().isoformat()
            }
        )
        
        logger.info(f"Starting WAR task for user {user_id}, session {session_id}")
        
        # Initialize controller with existing business logic
        controller = WARKRSController(
            cookies=cookies,
            urls=urls,
            target_courses=target_courses,
            settings=settings,
            telegram_config=telegram_config,
            debug_mode=False
        )
        
        # Log initial state
        logger.info(f"Controller initialized. Remaining targets: {len(controller.remaining_targets)}")
        
        # Update database status (import here to avoid circular imports)
        update_task_status(user_id, session_id, 'active', {
            'worker_id': self.request.id,
            'started_at': datetime.utcnow(),
            'target_count': len(controller.remaining_targets)
        })
        
        # Send start notification dengan enhanced debugging
        telegram_notification_sent = False
        telegram_debug_info = {}
        
        if telegram_config:
            telegram_debug_info['config_provided'] = True
            telegram_debug_info['bot_token_provided'] = bool(telegram_config.get('bot_token'))
            telegram_debug_info['chat_id_provided'] = bool(telegram_config.get('chat_id'))
            
            if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                try:
                    # Create direct TelegramNotifier instance for testing
                    direct_notifier = TelegramNotifier(
                        bot_token=telegram_config['bot_token'],
                        chat_id=telegram_config['chat_id']
                    )
                    
                    if direct_notifier.is_enabled():
                        # Send start notification directly
                        success = direct_notifier.notify_start(list(controller.remaining_targets))
                        telegram_notification_sent = success
                        telegram_debug_info['direct_notification_success'] = success
                        
                        if success:
                            logger.info(f"✅ Direct Telegram start notification sent for user {user_id}")
                        else:
                            logger.warning(f"❌ Direct Telegram start notification failed for user {user_id}")
                    else:
                        telegram_debug_info['notifier_enabled'] = False
                        logger.warning(f"📱 Direct TelegramNotifier not enabled for user {user_id}")
                        
                except Exception as direct_error:
                    telegram_debug_info['direct_error'] = str(direct_error)
                    logger.error(f"❌ Direct Telegram notification error: {direct_error}")
            
            # Also try via controller (original method)
            if controller.telegram and controller.telegram.is_enabled():
                try:
                    controller.telegram.notify_start(list(controller.remaining_targets))
                    telegram_debug_info['controller_notification_success'] = True
                    if not telegram_notification_sent:
                        telegram_notification_sent = True
                    logger.info(f"✅ Controller Telegram start notification sent for user {user_id}")
                except Exception as controller_error:
                    telegram_debug_info['controller_error'] = str(controller_error)
                    logger.warning(f"❌ Controller Telegram start notification failed: {controller_error}")
            else:
                telegram_debug_info['controller_telegram_enabled'] = False
                logger.info(f"📱 Controller Telegram not enabled for user {user_id}")
        else:
            telegram_debug_info['config_provided'] = False
            logger.info(f"📱 No Telegram config provided for user {user_id}")
        
        # Log comprehensive telegram debug info
        log_activity_celery(user_id, 
            f"Telegram start notification attempt: {'SUCCESS' if telegram_notification_sent else 'FAILED'}", 
            "INFO" if telegram_notification_sent else "WARNING", 
            session_id, telegram_debug_info)
        
        # Main WAR loop with enhanced monitoring
        cycle_delay = settings.get('cycle_delay', 45)  # Default 45 seconds as per requirement
        max_cycles = settings.get('max_cycles', 200)   # Safety limit
        
        successful_courses = []
        total_cycles = 0
        
        logger.info(f"Starting WAR loop for user {user_id} with cycle delay {cycle_delay}s")
        
        while (controller.remaining_targets and 
               total_cycles < max_cycles and 
               not task_should_stop(self.request.id)):
            
            try:
                # Check if task was revoked
                if self.request.called_directly is False:
                    # This is running in worker, check for revocation
                    pass
                
                # Run single cycle using existing controller logic
                logger.info(f"User {user_id}: Starting cycle {total_cycles + 1}")
                
                session_valid, session_status, successful_this_cycle, failed_this_cycle = controller.run_single_cycle()
                
                total_cycles += 1
                
                # Update progress
                if successful_this_cycle:
                    successful_courses.extend(successful_this_cycle)
                    logger.info(f"User {user_id}: Cycle {total_cycles} - Success: {successful_this_cycle}")
                
                if failed_this_cycle:
                    logger.info(f"User {user_id}: Cycle {total_cycles} - Failed: {failed_this_cycle}")
                
                # Reset consecutive error counters on successful cycle completion
                if hasattr(controller, 'consecutive_cycle_errors'):
                    controller.consecutive_cycle_errors = 0
                
                # Update task progress
                self.update_state(
                    state='PROGRESS',
                    meta={
                        'status': 'running',
                        'user_id': user_id,
                        'session_id': session_id,
                        'cycle': total_cycles,
                        'successful_courses': successful_courses,
                        'successful_this_cycle': successful_this_cycle or [],
                        'failed_this_cycle': failed_this_cycle or [],
                        'remaining_targets': list(controller.remaining_targets),
                        'session_valid': session_valid,
                        'last_activity': datetime.utcnow().isoformat()
                    }
                )
                
                # Update database progress
                update_task_progress(user_id, session_id, total_cycles, successful_courses, controller.remaining_targets)
                
                # Handle session errors - CRITICAL: Stop task immediately on session failure
                if not session_valid:
                    logger.error(f"User {user_id}: Session validation failed at cycle {total_cycles}")
                    
                    # Send session warning notification
                    if telegram_config and controller.telegram and controller.telegram.is_enabled():
                        try:
                            controller.telegram.notify_session_warning(session_status, total_cycles)
                            logger.info(f"✅ Session warning notification sent for user {user_id}")
                        except Exception as tg_error:
                            logger.warning(f"❌ Telegram session warning failed: {tg_error}")
                    
                    # Determine action based on session status
                    action = session_status.get('recommended_action', 'stop_and_reauth')
                    
                    if action == 'stop_and_reauth':
                        logger.error(f"User {user_id}: Critical session error - stopping task immediately")
                        
                        # Send immediate stop notification
                        if telegram_config:
                            try:
                                # Try direct notification
                                if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                                    direct_notifier = TelegramNotifier(
                                        bot_token=telegram_config['bot_token'],
                                        chat_id=telegram_config['chat_id']
                                    )
                                    if direct_notifier.is_enabled():
                                        direct_notifier.notify_error(
                                            f"🚨 TASK STOPPED: Session expired after {total_cycles} cycles. "
                                            f"Please login to SIAKAD again and restart the task."
                                        )
                                        logger.info(f"✅ Session stop notification sent for user {user_id}")
                                
                                # Also try controller method
                                if controller.telegram and controller.telegram.is_enabled():
                                    controller.telegram.notify_error(
                                        f"🚨 TASK STOPPED: Session expired. Please restart task after re-login."
                                    )
                            except Exception as tg_error:
                                logger.warning(f"❌ Failed to send stop notification: {tg_error}")
                        
                        # Force break to stop the main loop
                        break
                    elif action == 'warn_and_continue':
                        logger.warning(f"User {user_id}: Session warning but continuing with monitoring")
                        # Continue but with increased monitoring
                        
                        # If session keeps failing for multiple cycles, force stop
                        if hasattr(controller, 'consecutive_session_failures'):
                            controller.consecutive_session_failures += 1
                        else:
                            controller.consecutive_session_failures = 1
                            
                        if controller.consecutive_session_failures >= 3:
                            logger.error(f"User {user_id}: Too many consecutive session failures ({controller.consecutive_session_failures}) - forcing stop")
                            
                            # Send stop notification for consecutive failures
                            if telegram_config:
                                try:
                                    if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                                        direct_notifier = TelegramNotifier(
                                            bot_token=telegram_config['bot_token'],
                                            chat_id=telegram_config['chat_id']
                                        )
                                        if direct_notifier.is_enabled():
                                            direct_notifier.notify_error(
                                                f"🚨 TASK STOPPED: Too many session failures ({controller.consecutive_session_failures}). "
                                                f"Please check your login credentials and restart the task."
                                            )
                                            logger.info(f"✅ Session failure stop notification sent for user {user_id}")
                                except Exception as tg_error:
                                    logger.warning(f"❌ Failed to send session failure notification: {tg_error}")
                            
                            break
                else:
                    # Reset failure counter on successful session
                    if hasattr(controller, 'consecutive_session_failures'):
                        controller.consecutive_session_failures = 0
                
                # Break if all courses completed
                if not controller.remaining_targets:
                    logger.info(f"User {user_id}: All target courses completed after {total_cycles} cycles")
                    break
                
                # Send periodic notifications dengan enhanced debugging
                if (telegram_config and 
                    (successful_this_cycle or total_cycles % 5 == 0)):
                    
                    notification_sent = False
                    
                    # Try direct notification
                    if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                        try:
                            direct_notifier = TelegramNotifier(
                                bot_token=telegram_config['bot_token'],
                                chat_id=telegram_config['chat_id']
                            )
                            
                            if direct_notifier.is_enabled():
                                elapsed = datetime.utcnow() - controller.start_time
                                elapsed_str = str(elapsed).split('.')[0]
                                
                                success = direct_notifier.notify_cycle_summary(
                                    cycle_number=total_cycles,
                                    attempted_courses=(successful_this_cycle or []) + (failed_this_cycle or []),
                                    successful_courses=successful_this_cycle or [],
                                    failed_courses=failed_this_cycle or [],
                                    elapsed_time=elapsed_str,
                                    next_attempt_in=cycle_delay if controller.remaining_targets else None
                                )
                                
                                if success:
                                    notification_sent = True
                                    logger.info(f"✅ Direct Telegram cycle notification sent for user {user_id}, cycle {total_cycles}")
                                    
                        except Exception as direct_error:
                            logger.warning(f"❌ Direct Telegram cycle notification failed: {direct_error}")
                    
                    # Try controller notification as fallback
                    if not notification_sent and controller.telegram and controller.telegram.is_enabled():
                        try:
                            elapsed = datetime.utcnow() - controller.start_time
                            elapsed_str = str(elapsed).split('.')[0]
                            
                            controller.telegram.notify_cycle_summary(
                                cycle_number=total_cycles,
                                attempted_courses=(successful_this_cycle or []) + (failed_this_cycle or []),
                                successful_courses=successful_this_cycle or [],
                                failed_courses=failed_this_cycle or [],
                                elapsed_time=elapsed_str,
                                next_attempt_in=cycle_delay if controller.remaining_targets else None
                            )
                            
                            notification_sent = True
                            logger.info(f"✅ Controller Telegram cycle notification sent for user {user_id}, cycle {total_cycles}")
                            
                        except Exception as controller_error:
                            logger.warning(f"❌ Controller Telegram cycle notification failed: {controller_error}")
                    
                    # Log notification status
                    if notification_sent:
                        if successful_this_cycle:
                            log_activity_celery(user_id, f"Telegram success notification sent for courses: {', '.join(successful_this_cycle)}", "SUCCESS", session_id)
                        elif total_cycles % 5 == 0:
                            log_activity_celery(user_id, f"Telegram heartbeat notification sent for cycle {total_cycles}", "INFO", session_id)
                    else:
                        log_activity_celery(user_id, f"Telegram cycle notification failed for cycle {total_cycles}", "WARNING", session_id)
                
                # Sleep between cycles (non-blocking)
                if controller.remaining_targets and total_cycles < max_cycles:
                    logger.info(f"User {user_id}: Cycle {total_cycles} completed. Waiting {cycle_delay}s before next cycle")
                    time.sleep(cycle_delay)
                
            except Exception as cycle_error:
                logger.error(f"User {user_id}: Error in cycle {total_cycles + 1}: {cycle_error}")
                
                # Track consecutive errors
                if hasattr(controller, 'consecutive_cycle_errors'):
                    controller.consecutive_cycle_errors += 1
                else:
                    controller.consecutive_cycle_errors = 1
                
                # Send error notification
                if telegram_config and controller.telegram and controller.telegram.is_enabled():
                    try:
                        controller.telegram.notify_error(f"Cycle {total_cycles + 1} error: {str(cycle_error)}")
                        logger.info(f"✅ Error notification sent for user {user_id}, cycle {total_cycles + 1}")
                    except Exception as tg_error:
                        logger.warning(f"❌ Telegram error notification failed: {tg_error}")
                
                # Stop task if too many consecutive errors
                if controller.consecutive_cycle_errors >= 3:
                    logger.error(f"User {user_id}: Too many consecutive cycle errors ({controller.consecutive_cycle_errors}) - stopping task")
                    
                    # Send stop notification for cycle errors
                    if telegram_config:
                        try:
                            if telegram_config.get('bot_token') and telegram_config.get('chat_id'):
                                direct_notifier = TelegramNotifier(
                                    bot_token=telegram_config['bot_token'],
                                    chat_id=telegram_config['chat_id']
                                )
                                if direct_notifier.is_enabled():
                                    direct_notifier.notify_error(
                                        f"🚨 TASK STOPPED: Too many cycle errors ({controller.consecutive_cycle_errors}). "
                                        f"Please check your configuration and restart the task."
                                    )
                                    logger.info(f"✅ Cycle error stop notification sent for user {user_id}")
                        except Exception as tg_error:
                            logger.warning(f"❌ Failed to send cycle error notification: {tg_error}")
                    
                    break
                
                # Wait before retrying
                time.sleep(min(cycle_delay, 60))
        
        # Task completion - determine final status with clear error indication
        if hasattr(controller, 'consecutive_session_failures') and controller.consecutive_session_failures >= 3:
            final_status = 'error_session_failed'
            status_message = f"Task stopped: Too many session failures ({controller.consecutive_session_failures})"
        elif hasattr(controller, 'consecutive_cycle_errors') and controller.consecutive_cycle_errors >= 3:
            final_status = 'error_cycle_failed'
            status_message = f"Task stopped: Too many cycle errors ({controller.consecutive_cycle_errors})"
        elif not controller.remaining_targets:
            final_status = 'completed'
            status_message = "Task completed: All courses enrolled successfully"
        else:
            final_status = 'stopped'
            status_message = f"Task stopped after {total_cycles} cycles"
        
        # Calculate final statistics
        elapsed_time = datetime.utcnow() - controller.start_time
        hours, remainder = divmod(int(elapsed_time.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}h {minutes}m {seconds}s" if hours > 0 else f"{minutes}m {seconds}s"
        
        # Update final task state for user visibility
        self.update_state(
            state='SUCCESS' if final_status == 'completed' else 'FAILURE' if 'error' in final_status else 'SUCCESS',
            meta={
                'status': final_status,
                'user_id': user_id,
                'session_id': session_id,
                'total_cycles': total_cycles,
                'successful_courses': successful_courses,
                'remaining_targets': list(controller.remaining_targets),
                'elapsed_time': time_str,
                'completed_at': datetime.utcnow().isoformat(),
                'status_message': status_message,
                'error_type': final_status if 'error' in final_status else None
            }
        )
        
        result = {
            'status': final_status,
            'user_id': user_id,
            'session_id': session_id,
            'total_cycles': total_cycles,
            'successful_courses': successful_courses,
            'remaining_targets': list(controller.remaining_targets),
            'elapsed_time': time_str,
            'completed_at': datetime.utcnow().isoformat(),
            'status_message': status_message
        }
        
        logger.info(f"User {user_id}: {status_message} - {time_str}")
        
        # Update database with final status
        try:
            update_task_progress(user_id, session_id, total_cycles, successful_courses, 
                               controller.remaining_targets, final_status, status_message)
        except Exception as db_error:
            logger.error(f"Failed to update final task status in database: {db_error}")
        
        # Update database final status
        update_task_status(user_id, session_id, final_status, result)
        
        # Send completion notification dengan enhanced debugging
        completion_notification_sent = False
        
        if telegram_config and telegram_config.get('bot_token') and telegram_config.get('chat_id'):
            # Try direct notification first
            try:
                direct_notifier = TelegramNotifier(
                    bot_token=telegram_config['bot_token'],
                    chat_id=telegram_config['chat_id']
                )
                
                if direct_notifier.is_enabled():
                    if final_status == 'completed':
                        success = direct_notifier.notify_all_completed(successful_courses, time_str)
                    else:
                        success = direct_notifier.notify_error(f"Task stopped after {total_cycles} cycles")
                    
                    if success:
                        completion_notification_sent = True
                        logger.info(f"✅ Direct Telegram completion notification sent for user {user_id}")
                        
                        if final_status == 'completed':
                            log_activity_celery(user_id, f"All courses completed! Direct Telegram notification sent. Courses: {', '.join(successful_courses)}", "SUCCESS", session_id)
                        else:
                            log_activity_celery(user_id, f"Task stopped - Direct Telegram notification sent after {total_cycles} cycles", "INFO", session_id)
                    else:
                        logger.warning(f"❌ Direct Telegram completion notification failed for user {user_id}")
                        
            except Exception as direct_error:
                logger.warning(f"❌ Direct Telegram completion notification error: {direct_error}")
        
        # Try controller notification as fallback
        if not completion_notification_sent and telegram_config and controller.telegram and controller.telegram.is_enabled():
            try:
                if final_status == 'completed':
                    controller.telegram.notify_all_completed(successful_courses, time_str)
                    logger.info(f"✅ Controller Telegram completion notification sent for user {user_id}")
                    log_activity_celery(user_id, f"All courses completed! Controller Telegram notification sent. Courses: {', '.join(successful_courses)}", "SUCCESS", session_id)
                else:
                    controller.telegram.notify_error(f"Task stopped after {total_cycles} cycles")
                    logger.info(f"✅ Controller Telegram stop notification sent for user {user_id}")
                    log_activity_celery(user_id, f"Task stopped - Controller Telegram notification sent after {total_cycles} cycles", "INFO", session_id)
                    
                completion_notification_sent = True
                    
            except Exception as controller_error:
                logger.warning(f"❌ Controller Telegram completion notification failed: {controller_error}")
                log_activity_celery(user_id, f"Controller Telegram completion notification failed: {str(controller_error)}", "ERROR", session_id)
        
        # Log if no notification was sent
        if not completion_notification_sent:
            log_activity_celery(user_id, "No Telegram completion notification sent", "WARNING", session_id, {
                'telegram_config_provided': bool(telegram_config),
                'controller_telegram_available': bool(controller.telegram),
                'final_status': final_status
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Fatal error in WAR task for user {user_id}: {e}")
        
        # Update database error status
        error_result = {
            'status': 'error',
            'user_id': user_id,
            'session_id': session_id,
            'error': str(e),
            'failed_at': datetime.utcnow().isoformat()
        }
        
        update_task_status(user_id, session_id, 'error', error_result)
        
        # Send error notification
        if telegram_config:
            try:
                notifier = TelegramNotifier(
                    bot_token=telegram_config.get('bot_token'),
                    chat_id=telegram_config.get('chat_id')
                )
                if notifier.is_enabled():
                    notifier.notify_error(f"Fatal task error: {str(e)}")
            except Exception as tg_error:
                logger.warning(f"Telegram error notification failed: {tg_error}")
        
        # Re-raise for Celery retry mechanism
        raise self.retry(countdown=300, max_retries=3, exc=e)  # Retry after 5 minutes


@celery_app.task(name='tasks.war_tasks.stop_war_task')
def stop_war_task(user_id: int) -> Dict:
    """
    Stop WAR task for specific user
    
    Args:
        user_id: User ID to stop task for
        
    Returns:
        Dict with stop result
    """
    try:
        # Mark task for stopping in database
        result = mark_task_for_stop(user_id)
        
        logger.info(f"Stop signal sent for user {user_id}")
        
        return {
            'status': 'stop_signal_sent',
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat(),
            'result': result
        }
        
    except Exception as e:
        logger.error(f"Error stopping task for user {user_id}: {e}")
        return {
            'status': 'error',
            'user_id': user_id,
            'error': str(e)
        }


def task_should_stop(task_id: str) -> bool:
    """
    Check if task should stop based on database flag
    
    Args:
        task_id: Celery task ID
        
    Returns:
        True if task should stop
    """
    try:
        # This will be implemented to check database for stop signals
        # For now, return False to continue
        return False
    except Exception:
        return False


def update_task_status(user_id: int, session_id: int, status: str, metadata: Dict):
    """
    Update task status in database
    
    Args:
        user_id: User ID
        session_id: Session ID  
        status: New status
        metadata: Additional metadata
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import db, WarSession, ActivityLog
        from flask import Flask
        
        # Create minimal app context for database operations
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///warkrs.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Update WAR session
            war_session = WarSession.query.filter_by(user_id=user_id, id=session_id).first()
            if war_session:
                war_session.status = status
                war_session.last_activity = datetime.utcnow()
                if status == 'active' and 'started_at' in metadata:
                    war_session.started_at = metadata['started_at']
                elif status in ['completed', 'stopped', 'error']:
                    war_session.stopped_at = datetime.utcnow()
                    
                db.session.commit()
                
            # Log activity
            log_activity_celery(user_id, f"Task status updated to {status}", "INFO", session_id, metadata)
            
    except Exception as e:
        logger.error(f"Error updating task status: {e}")


def update_task_progress(user_id: int, session_id: int, cycle: int, 
                        successful_courses: List[str], remaining_targets: set,
                        final_status: str = None, status_message: str = None):
    """
    Update task progress in database
    
    Args:
        user_id: User ID
        session_id: Session ID
        cycle: Current cycle number
        successful_courses: List of successful courses
        remaining_targets: Set of remaining target courses
        final_status: Final status if task is completing (optional)
        status_message: Status message for user (optional)
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import db, WarSession
        from flask import Flask
        
        # Create minimal app context for database operations
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///warkrs.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Update WAR session progress
            war_session = WarSession.query.filter_by(user_id=user_id, id=session_id).first()
            if war_session:
                war_session.total_attempts = cycle
                war_session.successful_attempts = len(successful_courses)
                war_session.courses_obtained = json.dumps(successful_courses)
                war_session.last_activity = datetime.utcnow()
                
                # Update final status if provided
                if final_status:
                    war_session.status = final_status
                    war_session.stopped_at = datetime.utcnow()
                    
                    # Log final status message
                    if status_message:
                        log_activity_celery(user_id, status_message, 
                                          "SUCCESS" if final_status == 'completed' else "ERROR", 
                                          session_id)
                
                db.session.commit()
                
    except Exception as e:
        logger.error(f"Error updating task progress: {e}")


def mark_task_for_stop(user_id: int) -> bool:
    """
    Mark task for stopping in database
    
    Args:
        user_id: User ID
        
    Returns:
        True if marked successfully
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import db, WarSession
        from flask import Flask
        
        # Create minimal app context for database operations
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///warkrs.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Find active session for user
            war_session = WarSession.query.filter_by(user_id=user_id, status='active').first()
            if war_session:
                war_session.status = 'stopping'
                db.session.commit()
                return True
                
        return False
        
    except Exception as e:
        logger.error(f"Error marking task for stop: {e}")
        return False


def log_activity_celery(user_id: int, message: str, level: str, 
                       session_id: int = None, details: Dict = None):
    """
    Log activity from Celery task
    
    Args:
        user_id: User ID
        message: Activity message
        level: Level of activity (INFO, ERROR, SUCCESS, WARNING)
        session_id: Session ID (optional)
        details: Additional details (optional)
    """
    try:
        # Import here to avoid circular imports
        import sys
        import os
        
        # Add parent directory to path for imports
        sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        from app import db, ActivityLog
        from flask import Flask
        
        # Create minimal app context for database operations
        app = Flask(__name__)
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///warkrs.db')
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(app)
        
        with app.app_context():
            # Create log entry with correct field names
            log_entry = ActivityLog(
                user_id=user_id,
                session_id=session_id,
                level=level,  # Use 'level' instead of 'activity_type'
                message=message,
                timestamp=datetime.utcnow()
            )
            
            # Add details to message if provided
            if details:
                try:
                    # Handle datetime objects in details
                    serializable_details = {}
                    for k, v in details.items():
                        if isinstance(v, datetime):
                            serializable_details[k] = v.isoformat()
                        else:
                            serializable_details[k] = v
                    log_entry.message += f" | Details: {json.dumps(serializable_details)}"
                except (TypeError, AttributeError):
                    log_entry.message += f" | Details: {str(details)}"
            
            db.session.add(log_entry)
            db.session.commit()
            
    except Exception as e:
        logger.error(f"Error logging activity: {e}")
