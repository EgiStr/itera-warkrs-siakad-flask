"""
KRS Parser Module
Handles parsing of KRS-related HTML content
"""

from bs4 import BeautifulSoup
from typing import Set, List, Dict
import logging

logger = logging.getLogger(__name__)


class KRSParser:
    """Parser for KRS-related HTML content following Single Responsibility Principle"""
    
    @staticmethod
    def parse_enrolled_courses(html_content: str) -> Set[str]:
        """
        Parse enrolled courses from KRS page HTML
        
        Args:
            html_content: HTML content of the KRS page
            
        Returns:
            Set of course codes that are currently enrolled
        """
        enrolled_codes = set()
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # First, check if this is a login page
            session_status = KRSParser.detect_session_status(html_content)
            if not session_status['session_valid']:
                logger.warning(f"Detected login/public page. Session status: {session_status['error_indicators']}")
                return enrolled_codes  # Return empty set for login page
            
            # Method 1: Find the KRS table by its unique ID 'tabelkrs'
            krs_table = soup.find('table', id='tabelkrs')
            
            if not krs_table:
                logger.warning("KRS table with id 'tabelkrs' not found, trying alternative methods")
                
                # Method 2: Look for any table that might contain KRS data
                # Try to find tables with common KRS indicators
                all_tables = soup.find_all('table')
                
                for table in all_tables:
                    # Check if table contains KRS-related content
                    table_text = table.get_text().lower()
                    if any(indicator in table_text for indicator in ['kode mata kuliah', 'mata kuliah', 'sks', 'kelas', 'semester']):
                        krs_table = table
                        logger.info("Found potential KRS table using alternative method")
                        break
                
                # Method 3: If still no table found, try looking for course patterns in the entire page
                if not krs_table:
                    logger.warning("No KRS table found, trying to parse course codes from page content")
                    # Look for course code patterns in the entire page content
                    page_text = soup.get_text()
                    import re
                    # Pattern to match course codes like SD25-40003, IF25-12345, etc.
                    course_pattern = r'[A-Z]{2,4}25-[0-9]{5}'
                    matches = re.findall(course_pattern, page_text)
                    for match in matches:
                        enrolled_codes.add(match)
                    
                    if enrolled_codes:
                        logger.info(f"Found {len(enrolled_codes)} course codes using pattern matching")
                    
                    return enrolled_codes
            
            # Process the found table
            if krs_table:
                # Find table body to avoid header/footer rows
                table_body = krs_table.find('tbody')
                
                # If no tbody, use the table directly
                if not table_body:
                    table_body = krs_table
                    logger.info("No tbody found, using table directly")
                
                rows = table_body.find_all('tr')
                
                for row in rows:
                    cols = row.find_all('td')
                    
                    # Ensure row has enough columns
                    if len(cols) > 1:
                        # Second column (index 1) typically contains 'CODE - COURSE_NAME'
                        full_course_text = cols[1].text.strip()
                        
                        # Handle different formats
                        if ' - ' in full_course_text:
                            course_code = full_course_text.split(' - ')[0].strip()
                        else:
                            # Try first column if second doesn't have the expected format
                            course_code = cols[0].text.strip()
                        
                        # Validate course code format (e.g., SD25-40003)
                        import re
                        if re.match(r'^[A-Z]{2,4}25-[0-9]{5}$', course_code):
                            enrolled_codes.add(course_code)
                            logger.debug(f"Found enrolled course: {course_code}")
                
                logger.info(f"Successfully parsed {len(enrolled_codes)} enrolled courses")
                        
        except Exception as e:
            logger.error(f"Failed to parse enrolled courses: {e}")
        
        return enrolled_codes
    
    @staticmethod
    def parse_course_options(html_content: str) -> List[Dict[str, str]]:
        """
        Parse available course options from selection page
        
        Args:
            html_content: HTML content of the course selection page
            
        Returns:
            List of dictionaries containing course information
        """
        courses = []
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Find course selection dropdown/options
            options = soup.find_all('option')
            
            for option in options:
                value = option.get('value', '').strip()
                text = option.text.strip()
                
                if value and text and '-' in text:
                    # Parse course code from text
                    parts = text.split(' - ')
                    if len(parts) >= 2:
                        course_code = parts[0].strip()
                        course_name = parts[1].strip()
                        
                        courses.append({
                            'code': course_code,
                            'name': course_name,
                            'value': value,
                            'full_text': text
                        })
                        
        except Exception as e:
            logger.error(f"Failed to parse course options: {e}")
        
        return courses
    
    @staticmethod
    def extract_alert_message(html_content: str) -> str:
        """
        Extract alert message from response HTML
        
        Args:
            html_content: HTML content that may contain alert messages
            
        Returns:
            Alert message if found, empty string otherwise
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Look for JavaScript alert in script tags
            scripts = soup.find_all('script')
            
            for script in scripts:
                if script.string and 'alert(' in script.string:
                    # Extract message from alert("message")
                    start = script.string.find('alert("') + 7
                    end = script.string.find('")', start)
                    
                    if start > 6 and end > start:
                        return script.string[start:end]
            
            # Also look for other common alert patterns
            alert_patterns = ['alert(\'', 'alert("']
            
            for pattern in alert_patterns:
                if pattern in html_content:
                    start_idx = html_content.find(pattern) + len(pattern)
                    end_char = pattern[-1]  # ' or "
                    end_idx = html_content.find(end_char + ')', start_idx)
                    
                    if end_idx > start_idx:
                        return html_content[start_idx:end_idx]
                        
        except Exception as e:
            logger.error(f"Failed to extract alert message: {e}")
        
        return ""

    @staticmethod
    def detect_session_status(html_content: str, response_url: str = None) -> dict:
        """
        Enhanced session status detection for SIAKAD ITERA
        
        Args:
            html_content: HTML content to analyze
            response_url: URL of the response (to detect redirects)
            
        Returns:
            Dictionary with session status information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            status = {
                'is_logged_in': True,
                'session_valid': True,
                'needs_login': False,
                'error_indicators': [],
                'confidence_score': 0,
                'recommended_action': 'continue'
            }
            
            page_text = soup.get_text().lower()
            title_text = soup.find('title')
            title_text = title_text.text.lower() if title_text else ""
            
            # CRITICAL: Check for SIAKAD login page specific indicators
            login_signals = 0
            
            # 2. Check for login navigation link presence
            login_nav_link = soup.find('a', href=lambda href: href and 'login/login' in href)
            if login_nav_link and 'login' in login_nav_link.get_text().lower():
                login_signals += 4
                status['error_indicators'].append("Found login navigation link - indicates public page")
            
            # 3. Check for absence of KRS table (most critical)
            krs_table = soup.find('table', id='tabelkrs')
            if not krs_table:
                # Also check for any table that might contain course data
                has_course_table = False
                all_tables = soup.find_all('table')
                for table in all_tables:
                    table_text = table.get_text().lower()
                    if any(indicator in table_text for indicator in ['kode mata kuliah', 'sks', 'semester', 'kelas']):
                        has_course_table = True
                        break
                
                if not has_course_table:
                    login_signals += 10
                    status['error_indicators'].append("No KRS or course data tables found")
       
            
            
            # 5. Check for news/public content (indicates public page)
            public_content_indicators = [
                'berita kemahasiswaan', 'berita ltpb', 'peraturan akademik',
                'kalender akademik'
            ]
            
            public_content_count = sum(1 for indicator in public_content_indicators if indicator in page_text)
            if public_content_count >= 3:
                login_signals += 3
                status['error_indicators'].append(f"Found {public_content_count} public content indicators")
            
            # 6. Check for specific login form elements
            login_form_elements = [
                'input[name="username"]',
                'input[name="password"]',
                'input[type="password"]',
                'form[action*="login"]'
            ]
            
            for selector in login_form_elements:
                if soup.select(selector):
                    login_signals += 2
                    status['error_indicators'].append(f"Found login form element: {selector}")
            
            # 8. Check for session timeout patterns
            session_timeout_patterns = [
                'session expired', 'sesi berakhir', 'timeout', 'login ulang',
                'akses ditolak', 'unauthorized', 'access denied', 'silakan login'
            ]
            
            for pattern in session_timeout_patterns:
                if pattern in page_text:
                    login_signals += 4
                    status['error_indicators'].append(f"Session timeout indicator: {pattern}")
            
            # 9. Check for absence of navigation that should be present when logged in
            logged_in_nav = [
                'krs', 'transkrip', 'jadwal', 'nilai', 'pembayaran', 'academic'
            ]
            
            nav_found = any(nav in page_text for nav in logged_in_nav)
            if not nav_found:
                login_signals += 1
                status['error_indicators'].append("No logged-in navigation elements found")
            
            # Calculate final status based on login signals
            if login_signals >= 8:
                status['is_logged_in'] = False
                status['session_valid'] = False
                status['needs_login'] = True
                status['confidence_score'] = min(100, login_signals * 8)
                status['recommended_action'] = 'stop_and_reauth'
            elif login_signals >= 5:
                status['is_logged_in'] = False
                status['session_valid'] = False
                status['needs_login'] = True
                status['confidence_score'] = min(95, login_signals * 12)
                status['recommended_action'] = 'warn_and_continue'
            elif login_signals >= 3:
                status['confidence_score'] = login_signals * 15
                status['recommended_action'] = 'monitor_closely'
                status['error_indicators'].append("Moderate session risk detected")
            elif login_signals >= 1:
                status['confidence_score'] = login_signals * 10
                status['recommended_action'] = 'continue'
                status['error_indicators'].append("Minor session indicators detected")
            
            logger.info(f"Session detection: {login_signals} login signals, confidence: {status['confidence_score']}%")
            return status
            
        except Exception as e:
            logger.error(f"Failed to detect session status: {e}")
            return {
                'is_logged_in': True,
                'session_valid': True,
                'needs_login': False,
                'error_indicators': [f"Detection error: {e}"],
                'confidence_score': 0,
                'recommended_action': 'continue'
            }

    @staticmethod
    def debug_html_structure(html_content: str, output_file: str = "debug_krs_page.html") -> None:
        """
        Save HTML content to file for debugging purposes
        
        Args:
            html_content: HTML content to save
            output_file: Output file name
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML content saved to {output_file} for debugging")
        except Exception as e:
            logger.error(f"Failed to save HTML debug file: {e}")
    
    @staticmethod
    def analyze_page_structure(html_content: str) -> Dict[str, any]:
        """
        Analyze the structure of the KRS page to understand its layout
        
        Args:
            html_content: HTML content to analyze
            
        Returns:
            Dictionary containing page structure information
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            analysis = {
                'tables': [],
                'forms': [],
                'course_patterns': [],
                'page_title': '',
                'has_krs_indicators': False
            }
            
            # Get page title
            title_tag = soup.find('title')
            if title_tag:
                analysis['page_title'] = title_tag.text.strip()
            
            # Analyze all tables
            tables = soup.find_all('table')
            for i, table in enumerate(tables):
                table_info = {
                    'index': i,
                    'id': table.get('id', ''),
                    'class': table.get('class', []),
                    'rows': len(table.find_all('tr')),
                    'has_tbody': bool(table.find('tbody')),
                    'text_preview': table.get_text()[:200] + '...' if len(table.get_text()) > 200 else table.get_text()
                }
                analysis['tables'].append(table_info)
            
            # Analyze forms
            forms = soup.find_all('form')
            for i, form in enumerate(forms):
                form_info = {
                    'index': i,
                    'action': form.get('action', ''),
                    'method': form.get('method', ''),
                    'inputs': len(form.find_all('input'))
                }
                analysis['forms'].append(form_info)
            
            # Look for course code patterns
            import re
            page_text = soup.get_text()
            course_pattern = r'[A-Z]{2,4}25-[0-9]{5}'
            matches = re.findall(course_pattern, page_text)
            analysis['course_patterns'] = list(set(matches))  # Remove duplicates
            
            # Check for KRS indicators
            krs_indicators = ['krs', 'kartu rencana studi', 'mata kuliah', 'course', 'daftar ulang']
            page_text_lower = page_text.lower()
            analysis['has_krs_indicators'] = any(indicator in page_text_lower for indicator in krs_indicators)
            
            logger.info(f"Page analysis complete: {len(analysis['tables'])} tables, {len(analysis['course_patterns'])} course patterns found")
            return analysis
            
        except Exception as e:
            logger.error(f"Failed to analyze page structure: {e}")
            return {}
