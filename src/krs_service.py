"""
KRS Service Module
Core business logic for KRS operations
"""

import time
from typing import Set, Dict, Optional
import logging

from .session import SiakadSession
from .parser import KRSParser

logger = logging.getLogger(__name__)


class KRSService:
    """
    Core KRS service handling all KRS-related operations
    Follows Single Responsibility and Open/Closed principles
    """
    
    def __init__(self, session: SiakadSession, urls: Dict[str, str]):
        """
        Initialize KRS service
        
        Args:
            session: Authenticated SIAKAD session
            urls: Dictionary containing required URLs
        """
        self.session = session
        self.urls = urls
        self.parser = KRSParser()
    
    def get_enrolled_courses(self, debug_mode: bool = False) -> tuple[Set[str], dict]:
        """
        Get currently enrolled courses with session validation
        
        Args:
            debug_mode: If True, save HTML content for debugging
            
        Returns:
            Tuple of (enrolled_courses_set, session_status_dict)
        """
        try:
            response = self.session.get(self.urls['pilih_mk'])
            
            # Check session status first
            session_status = self.parser.detect_session_status(response.text, response.url)
            
            if debug_mode:
                self.parser.debug_html_structure(response.text, "debug_enrolled_courses.html")
                analysis = self.parser.analyze_page_structure(response.text)
                logger.info(f"Page analysis: {analysis}")
                logger.info(f"Session status: {session_status}")
            
            # If session is invalid, return empty set but preserve status info
            if not session_status['session_valid']:
                logger.warning(f"Session validation failed: {session_status['error_indicators']}")
                return set(), session_status
            
            enrolled = self.parser.parse_enrolled_courses(response.text)
            logger.info(f"Found {len(enrolled)} enrolled courses: {', '.join(sorted(enrolled)) if enrolled else 'None'}")
            
            return enrolled, session_status
        except Exception as e:
            logger.error(f"Failed to get enrolled courses: {e}")
            return set(), {
                'is_logged_in': False,
                'session_valid': False, 
                'needs_login': True,
                'error_indicators': [f"Network error: {e}"],
                'confidence_score': 100,
                'recommended_action': 'stop_and_reauth'
            }
    
    def is_course_enrolled(self, course_code: str) -> tuple[bool, dict]:
        """
        Check if a specific course is already enrolled
        
        Args:
            course_code: Course code to check
            
        Returns:
            Tuple of (is_enrolled, session_status)
        """
        enrolled_courses, session_status = self.get_enrolled_courses()
        return course_code in enrolled_courses, session_status
    
    def register_course(self, class_id: str) -> bool:
        """
        Attempt to register for a course
        
        Args:
            class_id: ID of the class to register for
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            payload = {'idkelas': class_id}
            response = self.session.post(self.urls['simpan_krs'], data=payload)
            
            # Check response for success/failure indicators
            if response.status_code in [200, 303]:
                # Extract any alert messages from response
                alert_message = self.parser.extract_alert_message(response.text)
                if alert_message:
                    logger.info(f"Server response: {alert_message}")
                
                return True
            else:
                logger.warning(f"Unexpected status code: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to register course {class_id}: {e}")
            return False
    
    def verify_registration(self, course_code: str, delay: int = 2) -> bool:
        """
        Verify if course registration was successful
        
        Args:
            course_code: Course code to verify
            delay: Delay before verification in seconds
            
        Returns:
            True if course is now enrolled, False otherwise
        """
        if delay > 0:
            time.sleep(delay)
        
        enrolled_courses, session_status = self.get_enrolled_courses()
        return course_code in enrolled_courses
    
    def register_and_verify(self, course_code: str, class_id: str, 
                          verification_delay: int = 2) -> bool:
        """
        Register for a course and verify the registration
        
        Args:
            course_code: Course code for verification
            class_id: Class ID for registration
            verification_delay: Delay before verification
            
        Returns:
            True if registration was successful and verified
        """
        # Attempt registration
        registration_success = self.register_course(class_id)
        
        if not registration_success:
            return False
        
        # Verify registration
        return self.verify_registration(course_code, verification_delay)
    
    def is_course_enrolled_old(self, course_code: str) -> bool:
        """
        Legacy method - Check if a specific course is already enrolled
        Note: Use the new is_course_enrolled method that returns session status
        
        Args:
            course_code: Course code to check
            
        Returns:
            True if course is enrolled, False otherwise
        """
        enrolled_courses, session_status = self.get_enrolled_courses()
        return course_code in enrolled_courses
