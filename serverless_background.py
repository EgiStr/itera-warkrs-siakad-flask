"""
Background WAR Process for Serverless Environment
Handles WAR KRS automation with scheduling and persistence
"""

import json
import time
import asyncio
from datetime import datetime, timedelta
from flask import jsonify
import threading
import schedule
from concurrent.futures import ThreadPoolExecutor

def schedule_war_process(user_id, session_id, app, db, interval_minutes=5):
    """
    Schedule WAR process to run at intervals using background threads
    This works around serverless limitations by using persistent scheduling
    """
    
    with app.app_context():
        try:
            from app import User, WarSession, log_activity
            
            # Get user and session
            user = User.query.get(user_id)
            war_session = WarSession.query.get(session_id)
            
            if not user or not war_session:
                return {"error": "User or session not found"}
            
            # Update session to scheduled
            war_session.status = 'scheduled'
            war_session.started_at = datetime.utcnow()
            war_session.last_activity = datetime.utcnow()
            db.session.commit()
            
            log_activity(user_id, f"WAR process scheduled to run every {interval_minutes} minutes", "INFO", session_id)
            
            # Create scheduled job
            def run_war_cycle():
                try:
                    result = run_war_process_serverless_single(user_id, session_id, app, db)
                    
                    # Check if we should stop
                    with app.app_context():
                        session = WarSession.query.get(session_id)
                        if session and session.status in ['stopped', 'completed']:
                            return schedule.CancelJob
                        
                        # If successful courses found, mark as completed
                        if result.get('successful_courses'):
                            session.status = 'completed'
                            db.session.commit()
                            return schedule.CancelJob
                            
                except Exception as e:
                    log_activity(user_id, f"Scheduled WAR error: {e}", "ERROR", session_id)
            
            # Schedule the job
            schedule.every(interval_minutes).minutes.do(run_war_cycle)
            
            # Run scheduler in background thread
            def run_scheduler():
                while True:
                    schedule.run_pending()
                    time.sleep(1)
                    
                    # Check if session should stop
                    with app.app_context():
                        session = WarSession.query.get(session_id)
                        if not session or session.status in ['stopped', 'completed', 'failed']:
                            break
            
            # Start background thread
            scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
            scheduler_thread.start()
            
            return {
                "success": True,
                "message": f"WAR process scheduled every {interval_minutes} minutes",
                "status": "scheduled"
            }
            
        except Exception as e:
            return {"error": str(e)}

def run_war_process_webhook(user_id, session_id, app, db):
    """
    Run WAR process via external webhook/cron service
    This approach uses external services like GitHub Actions or Vercel Cron
    """
    
    with app.app_context():
        try:
            from app import User, WarSession, log_activity
            
            # Get session
            war_session = WarSession.query.get(session_id)
            if not war_session:
                return {"error": "Session not found"}
            
            # Check if session should continue
            if war_session.status not in ['active', 'scheduled']:
                return {"message": "Session not active", "status": war_session.status}
            
            # Update last activity
            war_session.last_activity = datetime.utcnow()
            db.session.commit()
            
            # Run single WAR attempt
            result = run_war_process_serverless_single(user_id, session_id, app, db)
            
            # Check if we got successful courses
            if result.get('successful_courses'):
                war_session.status = 'completed'
                war_session.stopped_at = datetime.utcnow()
                db.session.commit()
                log_activity(user_id, "WAR process completed successfully via webhook", "SUCCESS", session_id)
            
            return result
            
        except Exception as e:
            log_activity(user_id, f"Webhook WAR error: {e}", "ERROR", session_id)
            return {"error": str(e)}

def run_war_process_serverless_single(user_id, session_id, app, db):
    """
    Run a single WAR attempt - extracted from main function for reuse
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
                    if not notifier.is_enabled():
                        notifier = None
                except Exception as e:
                    log_activity(user_id, f"Telegram setup error: {e}", "WARNING", session_id)
                    notifier = None
            
            # Try to use existing controller
            try:
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
                
                # Run single cycle
                from app import WARKRSController
                controller = WARKRSController(
                    cookies=cookies,
                    urls=urls,
                    target_courses=target_courses_dict,
                    settings=default_settings,
                    debug_mode=False
                )
                
                success, status, successful_courses, failed_courses = controller.run_single_cycle()
                
                # Send notifications
                if notifier and notifier.is_enabled():
                    try:
                        if successful_courses:
                            for course in successful_courses:
                                notifier.notify_course_success(course)
                            notifier.notify_all_completed(successful_courses, "background cycle")
                        elif len(failed_courses) > 0:
                            # Only notify if this is final attempt or significant failure
                            pass
                    except Exception as e:
                        log_activity(user_id, f"Notification error: {e}", "WARNING", session_id)
                
                return {
                    "success": success,
                    "status": status,
                    "successful_courses": successful_courses,
                    "failed_courses": failed_courses,
                    "message": f"Background cycle completed. Success: {len(successful_courses)}, Failed: {len(failed_courses)}"
                }
                
            except Exception as controller_error:
                log_activity(user_id, f"Controller error: {str(controller_error)}", "ERROR", session_id)
                return {"error": str(controller_error)}
            
        except Exception as e:
            log_activity(user_id, f"Background WAR error: {str(e)}", "ERROR", session_id)
            return {"error": str(e)}

def create_external_webhook_config(user_id, session_id, base_url):
    """
    Create configuration for external webhook services
    Returns GitHub Actions workflow and Vercel cron configuration
    """
    
    github_workflow = f"""
name: WAR KRS Background Process
on:
  schedule:
    # Run every 5 minutes during registration hours
    - cron: '*/5 8-17 * * 1-5'
  workflow_dispatch:

jobs:
  war-process:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger WAR Process
        run: |
          curl -X POST "{base_url}/api/war/webhook" \\
            -H "Content-Type: application/json" \\
            -H "Authorization: Bearer ${{{{ secrets.WAR_API_KEY }}}}" \\
            -d '{{"user_id": {user_id}, "session_id": {session_id}}}'
    """
    
    vercel_cron = {
        "crons": [
            {
                "path": "/api/war/webhook",
                "schedule": "*/5 8-17 * * 1-5"
            }
        ]
    }
    
    return {
        "github_workflow": github_workflow,
        "vercel_cron": vercel_cron,
        "webhook_url": f"{base_url}/api/war/webhook"
    }

def run_war_process_async(user_id, session_id, app, db):
    """
    Run WAR process using asyncio for better concurrency
    Works better in some serverless environments
    """
    
    async def async_war_worker():
        while True:
            try:
                with app.app_context():
                    # Check session status
                    war_session = WarSession.query.get(session_id)
                    if not war_session or war_session.status not in ['active', 'scheduled']:
                        break
                    
                    # Run single attempt
                    result = run_war_process_serverless_single(user_id, session_id, app, db)
                    
                    # Check if successful
                    if result.get('successful_courses'):
                        war_session.status = 'completed'
                        db.session.commit()
                        break
                    
                    # Wait before next attempt
                    await asyncio.sleep(300)  # 5 minutes
                    
            except Exception as e:
                with app.app_context():
                    log_activity(user_id, f"Async WAR error: {e}", "ERROR", session_id)
                break
    
    # Run async worker
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(async_war_worker())
    except Exception as e:
        return {"error": str(e)}
    
    return {"success": True, "message": "Async WAR process completed"}

# Main enhanced serverless function
def run_war_process_serverless_enhanced(user_id, session_id, app, db, mode="single"):
    """
    Enhanced serverless WAR process with multiple background modes
    
    Modes:
    - single: Run once (original behavior)
    - scheduled: Use background threading with schedule
    - webhook: Prepare for external webhook calls
    - async: Use asyncio for background processing
    """
    
    if mode == "single":
        return run_war_process_serverless_single(user_id, session_id, app, db)
    elif mode == "scheduled":
        return schedule_war_process(user_id, session_id, app, db)
    elif mode == "webhook":
        return run_war_process_webhook(user_id, session_id, app, db)
    elif mode == "async":
        return run_war_process_async(user_id, session_id, app, db)
    else:
        return {"error": f"Unknown mode: {mode}"}
