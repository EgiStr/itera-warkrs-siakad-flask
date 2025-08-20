"""
API endpoints for serverless background WAR processing
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
import json

# Create blueprint for WAR API
war_api = Blueprint('war_api', __name__, url_prefix='/api/war')

@war_api.route('/start-cron', methods=['POST'])
def start_cron_war():
    """Start WAR process that will be handled by Vercel Cron"""
    
    try:
        from app import db, current_user, User, WarSession, log_activity
        from flask import current_app
        
        data = request.get_json()
        user_id = data.get('user_id') or (current_user.id if current_user.is_authenticated else None)
        interval_minutes = data.get('interval_minutes', 5)
        
        if not user_id:
            return jsonify({"error": "User ID required"}), 400
        
        # Check if user exists and has proper settings
        user = User.query.get(user_id)
        if not user or not user.settings:
            return jsonify({"error": "User or settings not found"}), 400
        
        settings = user.settings
        if not settings.ci_session or not settings.cf_clearance:
            return jsonify({"error": "SIAKAD cookies not configured"}), 400
        
        if not settings.target_courses:
            return jsonify({"error": "No target courses selected"}), 400
        
        # Get or create WAR session
        active_session = WarSession.query.filter(
            WarSession.user_id == user_id,
            WarSession.status.in_(['active', 'scheduled'])
        ).first()
        
        if active_session:
            return jsonify({
                "message": "WAR process already running",
                "session_id": active_session.id,
                "status": active_session.status
            }), 200
        
        # Create new session
        new_session = WarSession(
            user_id=user_id,
            status='scheduled',
            started_at=datetime.utcnow()
        )
        db.session.add(new_session)
        db.session.commit()
        
        log_activity(user_id, f"WAR scheduled for Vercel Cron (interval: {interval_minutes}min)", "INFO", new_session.id)
        
        return jsonify({
            "success": True,
            "session_id": new_session.id,
            "message": f"WAR scheduled for Vercel Cron every {interval_minutes} minutes",
            "status": "scheduled",
            "user_id": user_id
        })
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/cron', methods=['POST'])
def vercel_cron():
    """Vercel Cron endpoint - processes all active WAR sessions"""
    
    try:
        from app import db, WarSession, log_activity
        from vercel_war import run_war_process_serverless
        from flask import current_app
        import os
        
        # Validate cron secret for security
        cron_secret = request.headers.get('Authorization', '').replace('Bearer ', '')
        expected_secret = os.getenv('WAR_CRON_SECRET')
        
        if expected_secret and cron_secret != expected_secret:
            return jsonify({"error": "Invalid cron secret"}), 401
        
        # Get all active sessions
        active_sessions = WarSession.query.filter(
            WarSession.status.in_(['active', 'scheduled'])
        ).all()
        
        if not active_sessions:
            return jsonify({
                "message": "No active WAR sessions found",
                "processed": 0
            })
        
        results = []
        processed_count = 0
        
        for session in active_sessions:
            try:
                # Run WAR for this session
                result = run_war_process_serverless(
                    session.user_id, 
                    session.id, 
                    current_app, 
                    db, 
                    mode="webhook"
                )
                
                processed_count += 1
                
                # Check if WAR completed
                if result.get('successful_courses'):
                    session.status = 'completed'
                    session.stopped_at = datetime.utcnow()
                    db.session.commit()
                    
                    results.append({
                        "user_id": session.user_id,
                        "session_id": session.id,
                        "status": "completed",
                        "successful_courses": result.get('successful_courses', [])
                    })
                elif result.get('error'):
                    session.status = 'failed'
                    session.stopped_at = datetime.utcnow() 
                    db.session.commit()
                    
                    results.append({
                        "user_id": session.user_id,
                        "session_id": session.id,
                        "status": "failed",
                        "error": result.get('error')
                    })
                else:
                    # Update last activity
                    session.last_activity = datetime.utcnow()
                    db.session.commit()
                    
                    results.append({
                        "user_id": session.user_id,
                        "session_id": session.id,
                        "status": "continuing",
                        "message": result.get('message', 'WAR attempt completed')
                    })
                    
            except Exception as e:
                results.append({
                    "user_id": session.user_id,
                    "session_id": session.id,
                    "status": "error",
                    "error": str(e)
                })
        
        return jsonify({
            "success": True,
            "processed": processed_count,
            "results": results,
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/trigger', methods=['POST'])
def trigger_war():
    """Manual trigger for WAR process"""
    
    try:
        from app import db, User, WarSession
        from vercel_war import run_war_process_serverless
        from flask import current_app
        
        data = request.get_json()
        user_id = data.get('user_id')
        session_id = data.get('session_id')
        
        if not user_id:
            return jsonify({"error": "user_id required"}), 400
        
        # Get or create session
        if session_id:
            session = WarSession.query.get(session_id)
            if not session:
                return jsonify({"error": "Session not found"}), 404
        else:
            # Create new session
            session = WarSession(
                user_id=user_id,
                status='active',
                started_at=datetime.utcnow()
            )
            db.session.add(session)
            db.session.commit()
            session_id = session.id
        
        # Run WAR process
        result = run_war_process_serverless(user_id, session_id, current_app, db, mode="single")
        
        return jsonify({
            "session_id": session_id,
            **result
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/status/<int:session_id>', methods=['GET'])
def get_war_status(session_id):
    """Get status of WAR session"""
    
    try:
        from app import WarSession, ActivityLog
        
        session = WarSession.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        # Get recent activity logs
        recent_logs = ActivityLog.query.filter_by(
            session_id=session_id
        ).order_by(ActivityLog.timestamp.desc()).limit(10).all()
        
        return jsonify({
            "session_id": session.id,
            "status": session.status,
            "started_at": session.started_at.isoformat() if session.started_at else None,
            "stopped_at": session.stopped_at.isoformat() if session.stopped_at else None,
            "last_activity": session.last_activity.isoformat() if session.last_activity else None,
            "courses_obtained": json.loads(session.courses_obtained) if session.courses_obtained else [],
            "total_attempts": session.total_attempts,
            "successful_attempts": session.successful_attempts,
            "recent_logs": [
                {
                    "timestamp": log.timestamp.isoformat(),
                    "level": log.level,
                    "message": log.message
                } for log in recent_logs
            ]
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/stop/<int:session_id>', methods=['POST'])
def stop_war(session_id):
    """Stop WAR session"""
    
    try:
        from app import db, WarSession, log_activity
        
        session = WarSession.query.get(session_id)
        if not session:
            return jsonify({"error": "Session not found"}), 404
        
        if session.status in ['stopped', 'completed', 'failed']:
            return jsonify({"message": "Session already stopped", "status": session.status})
        
        # Update session status
        session.status = 'stopped'
        session.stopped_at = datetime.utcnow()
        session.last_activity = datetime.utcnow()
        db.session.commit()
        
        log_activity(session.user_id, "WAR process stopped by user", "INFO", session_id)
        
        return jsonify({
            "success": True,
            "message": "WAR process stopped",
            "session_id": session_id
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/config/webhook', methods=['GET'])
def get_webhook_config():
    """Get webhook configuration for external services"""
    
    try:
        from serverless_background import create_external_webhook_config
        
        user_id = request.args.get('user_id')
        session_id = request.args.get('session_id')
        base_url = request.host_url.rstrip('/')
        
        if not user_id or not session_id:
            return jsonify({"error": "user_id and session_id required"}), 400
        
        config = create_external_webhook_config(user_id, session_id, base_url)
        
        return jsonify(config)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@war_api.route('/active-sessions', methods=['GET'])
def get_active_sessions():
    """Get list of active WAR sessions for external cron processing"""
    
    try:
        from app import WarSession
        
        # Get all active or scheduled sessions
        active_sessions = WarSession.query.filter(
            WarSession.status.in_(['active', 'scheduled'])
        ).all()
        
        sessions_list = []
        for session in active_sessions:
            sessions_list.append({
                "user_id": session.user_id,
                "session_id": session.id,
                "status": session.status,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "last_activity": session.last_activity.isoformat() if session.last_activity else None
            })
        
        return jsonify(sessions_list)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Register the blueprint in your main app
# app.register_blueprint(war_api)
