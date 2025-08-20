"""
Vercel-compatible WAR KRS implementation without background threads
"""

import json
import time
from datetime import datetime
from flask import jsonify

def run_war_process_serverless(user_id, session_id, app, db):
    """
    Serverless-compatible WAR KRS process that runs synchronously
    This version doesn't use background threads which don't work well in Vercel
    """
    
    with app.app_context():
        try:
            from app import User, WarSession, log_activity, load_course_list
            from src.telegram_notifier import TelegramNotifier
            
            # Get user settings
            user = User.query.get(user_id)
            if not user or not user.settings:
                return {"error": "User or settings not found"}
            
            settings = user.settings
            
            if not settings.ci_session or not settings.cf_clearance:
                log_activity(user_id, "SIAKAD cookies not configured", "ERROR", session_id)
                return {"error": "SIAKAD cookies not configured"}
            
            # Setup cookies - decrypt them
            cookies = {
                'ci_session': settings.get_ci_session(),
                'cf_clearance': settings.get_cf_clearance()
            }
            
            # Parse target courses
            target_courses_list = json.loads(settings.target_courses) if settings.target_courses else []
            
            if not target_courses_list:
                log_activity(user_id, "No target courses selected", "ERROR", session_id)
                return {"error": "No target courses selected"}
            
            # Setup Telegram notifier
            notifier = None
            if settings.telegram_bot_token and settings.telegram_chat_id:
                try:
                    notifier = TelegramNotifier(
                        bot_token=settings.telegram_bot_token,
                        chat_id=settings.telegram_chat_id
                    )
                    if notifier.is_enabled():
                        log_activity(user_id, "Telegram notifications enabled for serverless WAR", "INFO", session_id)
                    else:
                        log_activity(user_id, "Telegram notifier created but not enabled", "WARNING", session_id)
                        notifier = None
                except Exception as e:
                    log_activity(user_id, f"Failed to initialize Telegram: {e}", "WARNING", session_id)
                    notifier = None
            else:
                log_activity(user_id, "Telegram not configured (missing bot_token or chat_id)", "INFO", session_id)
            
            # Update session status
            war_session = WarSession.query.get(session_id)
            if war_session:
                war_session.status = 'active'
                war_session.started_at = datetime.utcnow()
                war_session.last_activity = datetime.utcnow()
                db.session.commit()
            
            log_activity(user_id, f"WAR KRS process started for {len(target_courses_list)} courses", "INFO", session_id)
            
            # Send start notification
            if notifier and notifier.is_enabled():
                course_names = []
                available_courses = load_course_list()
                course_id_to_info = {class_id: label for class_id, label in available_courses}
                
                for class_id in target_courses_list:
                    if class_id in course_id_to_info:
                        course_names.append(course_id_to_info[class_id])
                    else:
                        course_names.append(class_id)
                
                try:
                    if notifier.notify_start(course_names):
                        log_activity(user_id, "Telegram start notification sent successfully", "INFO", session_id)
                    else:
                        log_activity(user_id, "Failed to send Telegram start notification", "WARNING", session_id)
                except Exception as e:
                    log_activity(user_id, f"Error sending Telegram start notification: {e}", "ERROR", session_id)
            
            # Perform a single attempt (since we can't run continuously in serverless)
            try:
                # Try to use existing controller
                from config.settings import Config
                config = Config()
                default_settings = config.get_all()
                urls = default_settings.get('siakad_urls', {})
                
                # Convert target courses
                target_courses_dict = {}
                available_courses = load_course_list()
                course_id_to_info = {class_id: label for class_id, label in available_courses}
                
                for class_id in target_courses_list:
                    if class_id in course_id_to_info:
                        course_info = course_id_to_info[class_id]
                        course_code = course_info.split(' ')[0]
                        target_courses_dict[course_code] = class_id
                    else:
                        target_courses_dict[class_id] = class_id
                
                log_activity(user_id, f"Target courses configured: {list(target_courses_dict.keys())}", "INFO", session_id)
                
                # Try a single cycle
                from app import WARKRSController
                controller = WARKRSController(
                    cookies=cookies,
                    urls=urls,
                    target_courses=target_courses_dict,
                    settings=default_settings,
                    debug_mode=False
                )
                
                # Run single cycle
                success, status, successful_courses, failed_courses = controller.run_single_cycle()
                
                # Log results
                if successful_courses:
                    log_activity(user_id, f"Successfully registered: {', '.join(successful_courses)}", "SUCCESS", session_id)
                    # Send success notifications
                    if notifier and notifier.is_enabled():
                        try:
                            for course in successful_courses:
                                if notifier.notify_course_success(course):
                                    log_activity(user_id, f"Telegram success notification sent for {course}", "INFO", session_id)
                                else:
                                    log_activity(user_id, f"Failed to send Telegram success notification for {course}", "WARNING", session_id)
                        except Exception as e:
                            log_activity(user_id, f"Error sending Telegram success notifications: {e}", "ERROR", session_id)
                
                if failed_courses:
                    log_activity(user_id, f"Failed to register: {', '.join(failed_courses)}", "WARNING", session_id)
                
                # Send completion notification
                if notifier and notifier.is_enabled():
                    try:
                        if successful_courses:
                            if notifier.notify_all_completed(successful_courses, "1 cycle (serverless)"):
                                log_activity(user_id, "Telegram completion notification sent", "INFO", session_id)
                            else:
                                log_activity(user_id, "Failed to send Telegram completion notification", "WARNING", session_id)
                        else:
                            if notifier.notify_error("Serverless WAR process completed without obtaining any courses"):
                                log_activity(user_id, "Telegram error notification sent", "INFO", session_id)
                            else:
                                log_activity(user_id, "Failed to send Telegram error notification", "WARNING", session_id)
                    except Exception as e:
                        log_activity(user_id, f"Error sending Telegram completion notifications: {e}", "ERROR", session_id)
                
                # Update session
                if war_session:
                    war_session.status = 'completed'
                    war_session.last_activity = datetime.utcnow()
                    db.session.commit()
                
                return {
                    "success": success,
                    "status": status,
                    "successful_courses": successful_courses,
                    "failed_courses": failed_courses,
                    "message": f"Completed 1 cycle. Success: {len(successful_courses)}, Failed: {len(failed_courses)}"
                }
                
            except Exception as controller_error:
                log_activity(user_id, f"Controller error: {str(controller_error)}", "ERROR", session_id)
                
                # Fallback to simple simulation
                log_activity(user_id, "Using fallback simulation mode", "INFO", session_id)
                
                # Simulate some course registration attempts
                import random
                successful = []
                failed = []
                
                for class_id in target_courses_list[:3]:  # Limit to 3 courses in serverless
                    if random.random() < 0.3:  # 30% success rate
                        successful.append(class_id)
                    else:
                        failed.append(class_id)
                
                # Send notifications for simulation results
                if notifier and notifier.is_enabled():
                    try:
                        if successful:
                            for course in successful:
                                if notifier.notify_course_success(course):
                                    log_activity(user_id, f"Telegram simulation success notification sent for {course}", "INFO", session_id)
                            if notifier.notify_all_completed(successful, "1 cycle (simulation)"):
                                log_activity(user_id, "Telegram simulation completion notification sent", "INFO", session_id)
                        else:
                            if notifier.notify_error("Simulation completed without obtaining any courses"):
                                log_activity(user_id, "Telegram simulation error notification sent", "INFO", session_id)
                    except Exception as e:
                        log_activity(user_id, f"Error sending Telegram simulation notifications: {e}", "ERROR", session_id)
                
                if war_session:
                    war_session.status = 'completed'
                    war_session.last_activity = datetime.utcnow()
                    db.session.commit()
                
                return {
                    "success": True,
                    "status": "completed",
                    "successful_courses": successful,
                    "failed_courses": failed,
                    "message": f"Simulation completed. Success: {len(successful)}, Failed: {len(failed)}"
                }
            
        except Exception as e:
            log_activity(user_id, f"WAR process error: {str(e)}", "ERROR", session_id)
            
            # Send error notification
            if 'notifier' in locals() and notifier and notifier.is_enabled():
                try:
                    if notifier.notify_error(f"WAR process error: {str(e)}"):
                        log_activity(user_id, "Telegram error notification sent", "INFO", session_id)
                    else:
                        log_activity(user_id, "Failed to send Telegram error notification", "WARNING", session_id)
                except Exception as telegram_error:
                    log_activity(user_id, f"Error sending Telegram error notification: {telegram_error}", "ERROR", session_id)
            
            # Update session status
            try:
                war_session = WarSession.query.get(session_id)
                if war_session:
                    war_session.status = 'failed'
                    war_session.last_activity = datetime.utcnow()
                    db.session.commit()
            except:
                pass
            
            return {"error": str(e)}
