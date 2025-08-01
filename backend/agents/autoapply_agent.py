"""
Auto-Apply Agent - Automated Job Application
Automatically fills out job applications and generates personalized cover letters
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import json
import requests
import time

# Optional Playwright imports for future use
try:
    from playwright.async_api import async_playwright, Page, Browser
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    Page = Browser = None

from database.db_connection import database
from utils.prompt_templates import CoverLetterGenerator
from utils.scraper_helpers import wait_random_delay

logger = logging.getLogger(__name__)


class AutoApplyAgent:
    """Autonomous agent for automatically applying to jobs"""
    
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.cover_letter_generator = CoverLetterGenerator()
        self.applications_today = 0
        self.max_applications_per_day = int(os.getenv("MAX_APPLICATIONS_PER_DAY", 10))
        
        # Application methods
        self.application_handlers = {
            'linkedin': self._apply_linkedin,
            'indeed': self._apply_indeed,
            'internshala': self._apply_internshala,
            'email': self._apply_via_email,
            'form': self._apply_via_form,
            'http_form': self._apply_http_form
        }
    
    async def initialize(self):
        """Initialize the auto-apply agent"""
        try:
            # For Windows compatibility, use a simple HTTP-based approach
            import platform
            
            # Create an HTTP session for making requests
            self.session = requests.Session()
            self.session.headers.update({
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            })
            self.browser = "http_session"  # Mark as using HTTP session
            
            await self.cover_letter_generator.initialize()
            
            # Get today's application count
            self.applications_today = await self._get_applications_today()
            
            logger.info("Auto-apply agent initialized successfully with HTTP session")
            
        except Exception as e:
            logger.error(f"Failed to initialize auto-apply agent: {e}")
            # Don't raise the exception, allow graceful degradation
            self.browser = None
    
    async def _init_playwright(self):
        """Initialize Playwright browser"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=True,
                args=['--no-sandbox', '--disable-dev-shm-usage', '--disable-gpu', '--disable-web-security']
            )
        except NotImplementedError as e:
            logger.error(f"Playwright subprocess creation failed (likely Windows compatibility issue): {e}")
            logger.warning("Auto-apply functionality will be disabled")
            self.browser = None
        except Exception as e:
            logger.error(f"Playwright initialization failed: {e}")
            self.browser = None
    
    async def cleanup(self):
        """Clean up resources"""
        if hasattr(self, 'session') and self.session:
            # For requests.Session, just close it (non-async)
            self.session.close()
        if self.page and PLAYWRIGHT_AVAILABLE:
            await self.page.close()
        if self.browser and self.browser != "http_session" and PLAYWRIGHT_AVAILABLE:
            await self.browser.close()
    
    async def auto_apply_to_jobs(self, user_id: int, job_ids: List[int]) -> List[Dict]:
        """
        Automatically apply to a list of jobs for a user
        
        Args:
            user_id: User ID
            job_ids: List of job IDs to apply to
            
        Returns:
            List of application results
        """
        results = []
        
        # Check if auto-apply is available (browser or HTTP session initialized)
        if not self.browser:
            logger.error("Auto-apply functionality not available - neither browser nor HTTP session initialized")
            return [{"job_id": job_id, "success": False, "status": "failed", "reason": "Auto-apply not available"} for job_id in job_ids]
        
        # Check daily limit
        if self.applications_today >= self.max_applications_per_day:
            logger.warning(f"Daily application limit reached ({self.max_applications_per_day})")
            return results
        
        # Get user profile
        user_profile = await self._get_user_profile(user_id)
        if not user_profile:
            raise ValueError(f"User profile not found for user_id: {user_id}")
        
        logger.info(f"Starting auto-apply for {len(job_ids)} jobs for user {user_id}")
        
        await database.log_system_activity(
            agent_name="autoapply_agent",
            action="auto_apply_start",
            message=f"Starting auto-apply for {len(job_ids)} jobs",
            metadata={"user_id": user_id, "job_count": len(job_ids)}
        )
        
        for job_id in job_ids:
            try:
                # Check daily limit
                if self.applications_today >= self.max_applications_per_day:
                    logger.info("Daily application limit reached, stopping")
                    break
                
                # Get job details
                job = await self._get_job_details(job_id)
                if not job:
                    logger.warning(f"Job {job_id} not found")
                    continue
                
                # Check if already applied
                existing_application = await self._check_existing_application(user_id, job_id)
                if existing_application:
                    logger.info(f"Already applied to job {job_id}")
                    continue
                
                # Apply to the job
                application_result = await self._apply_to_job(user_profile, job)
                results.append(application_result)
                
                # Record application in database
                if application_result['success']:
                    await self._record_application(user_id, job_id, application_result)
                    self.applications_today += 1
                
                # Delay between applications
                await wait_random_delay(30, 60)  # 30-60 seconds
                
            except Exception as e:
                logger.error(f"Error applying to job {job_id}: {e}")
                results.append({
                    'job_id': job_id,
                    'success': False,
                    'error': str(e),
                    'method': 'unknown'
                })
        
        await database.log_system_activity(
            agent_name="autoapply_agent",
            action="auto_apply_complete",
            message=f"Completed auto-apply: {len([r for r in results if r['success']])} successful applications",
            metadata={
                "user_id": user_id,
                "total_jobs": len(job_ids),
                "successful_applications": len([r for r in results if r['success']]),
                "failed_applications": len([r for r in results if not r['success']])
            }
        )
        
        return results
    
    async def _apply_to_job(self, user_profile: Dict, job) -> Dict:
        """Apply to a single job using the appropriate method"""
        
        # Determine application method
        application_method = self._determine_application_method(job)
        
        # Generate cover letter
        cover_letter = await self.cover_letter_generator.generate_cover_letter(
            user_profile, job
        )
        
        try:
            # Apply using the determined method
            if application_method in self.application_handlers:
                result = await self.application_handlers[application_method](
                    user_profile, job, cover_letter
                )
            else:
                result = await self._apply_generic(user_profile, job, cover_letter)
            
            result['cover_letter'] = cover_letter
            return result
            
        except Exception as e:
            logger.error(f"Error in application method {application_method}: {e}")
            return {
                'job_id': job.id,
                'success': False,
                'error': str(e),
                'method': application_method,
                'cover_letter': cover_letter
            }
    
    def _determine_application_method(self, job) -> str:
        """Determine the best application method for a job"""
        source = getattr(job, 'source', 'unknown')
        apply_url = getattr(job, 'apply_url', '')
        
        # If using HTTP session (not browser), use HTTP-based methods
        if self.browser == "http_session":
            if 'mailto:' in apply_url:
                return 'email'
            else:
                return 'http_form'  # New HTTP-based form submission
        
        # Browser-based methods
        if source in ['linkedin', 'indeed', 'internshala']:
            return source
        elif 'mailto:' in apply_url:
            return 'email'
        elif apply_url:
            return 'form'
        else:
            return 'manual'
    
    async def _apply_http_form(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to job using HTTP requests instead of browser automation"""
        try:
            apply_url = getattr(job, 'apply_url', '')
            if not apply_url or 'mailto:' in apply_url:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'No valid application URL found',
                    'method': 'http_form'
                }
            
            # Get the application page to analyze the form
            response = self.session.get(apply_url)
            if response.status_code != 200:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': f'Failed to access application page: {response.status_code}',
                    'method': 'http_form'
                }
            
            page_content = response.text
            
            # For now, we'll analyze if it's a known job portal and provide specific handling
            if 'linkedin.com' in apply_url:
                return await self._apply_http_linkedin(user_profile, job, cover_letter)
            elif 'indeed.com' in apply_url:
                return await self._apply_http_indeed(user_profile, job, cover_letter)
            else:
                # Generic HTTP form handling
                return await self._apply_http_generic(user_profile, job, cover_letter, page_content)
                    
        except Exception as e:
            logger.error(f"HTTP form application failed for job {job.id}: {e}")
            return {
                'job_id': job.id,
                'success': False,
                'error': f'HTTP request failed: {str(e)}',
                'method': 'http_form'
            }
    
    async def _apply_http_linkedin(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to LinkedIn job via HTTP (requires LinkedIn session)"""
        return {
            'job_id': job.id,
            'success': False,
            'error': 'LinkedIn applications require manual login - please apply manually',
            'method': 'http_linkedin',
            'manual_application_required': True
        }
    
    async def _apply_http_indeed(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to Indeed job via HTTP"""
        return {
            'job_id': job.id,
            'success': False,
            'error': 'Indeed applications require browser automation - please apply manually',
            'method': 'http_indeed',
            'manual_application_required': True
        }
    
    async def _apply_http_generic(self, user_profile: Dict, job, cover_letter: str, page_content: str) -> Dict:
        """Apply to generic job form via HTTP"""
        # For now, this is a placeholder that suggests manual application
        # In the future, we could add form parsing and submission logic
        return {
            'job_id': job.id,
            'success': False,
            'error': 'Generic form applications require manual submission - please apply manually',
            'method': 'http_generic',
            'manual_application_required': True,
            'message': f'Please visit the application URL to apply: {getattr(job, "apply_url", "")}'
        }
    
    async def _apply_linkedin(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to LinkedIn job"""
        try:
            if not self.page:
                self.page = await self.browser.new_page()
            
            # Navigate to job application page
            apply_url = job.apply_url
            if not apply_url:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'No application URL found',
                    'method': 'linkedin'
                }
            
            await self.page.goto(apply_url)
            await wait_random_delay(3, 5)
            
            # Check if login is required
            if '/login' in self.page.url or await self.page.query_selector('input[name="session_key"]'):
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'LinkedIn login required',
                    'method': 'linkedin'
                }
            
            # Look for Easy Apply button
            easy_apply_button = await self.page.query_selector('.jobs-apply-button')
            if not easy_apply_button:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'Easy Apply button not found',
                    'method': 'linkedin'
                }
            
            # Click Easy Apply
            await easy_apply_button.click()
            await wait_random_delay(2, 3)
            
            # Fill out application form
            await self._fill_linkedin_application_form(user_profile, cover_letter)
            
            return {
                'job_id': job.id,
                'success': True,
                'method': 'linkedin',
                'message': 'Applied via LinkedIn Easy Apply'
            }
            
        except Exception as e:
            return {
                'job_id': job.id,
                'success': False,
                'error': str(e),
                'method': 'linkedin'
            }
    
    async def _fill_linkedin_application_form(self, user_profile: Dict, cover_letter: str):
        """Fill out LinkedIn application form"""
        try:
            # Fill basic information
            name_field = await self.page.query_selector('input[name="name"]')
            if name_field:
                await name_field.fill(user_profile.get('name', ''))
            
            email_field = await self.page.query_selector('input[name="email"]')
            if email_field:
                await email_field.fill(user_profile.get('email', ''))
            
            phone_field = await self.page.query_selector('input[name="phone"]')
            if phone_field:
                await phone_field.fill(user_profile.get('phone', ''))
            
            # Fill cover letter if there's a text area
            cover_letter_field = await self.page.query_selector('textarea')
            if cover_letter_field:
                await cover_letter_field.fill(cover_letter)
            
            # Upload resume if file input exists
            resume_upload = await self.page.query_selector('input[type="file"]')
            if resume_upload and user_profile.get('resume_path'):
                await resume_upload.set_input_files(user_profile['resume_path'])
            
            # Submit application
            submit_button = await self.page.query_selector('button[type="submit"]')
            if submit_button:
                await submit_button.click()
                await wait_random_delay(2, 3)
            
        except Exception as e:
            logger.warning(f"Error filling LinkedIn form: {e}")
    
    async def _apply_indeed(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to Indeed job"""
        try:
            if not self.page:
                self.page = await self.browser.new_page()
            
            apply_url = job.apply_url
            if not apply_url:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'No application URL found',
                    'method': 'indeed'
                }
            
            await self.page.goto(apply_url)
            await wait_random_delay(3, 5)
            
            # Look for apply button
            apply_button = await self.page.query_selector('.np-button, .indeed-apply-button')
            if not apply_button:
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'Apply button not found',
                    'method': 'indeed'
                }
            
            await apply_button.click()
            await wait_random_delay(2, 3)
            
            # Fill application form
            await self._fill_indeed_application_form(user_profile, cover_letter)
            
            return {
                'job_id': job.id,
                'success': True,
                'method': 'indeed',
                'message': 'Applied via Indeed'
            }
            
        except Exception as e:
            return {
                'job_id': job.id,
                'success': False,
                'error': str(e),
                'method': 'indeed'
            }
    
    async def _fill_indeed_application_form(self, user_profile: Dict, cover_letter: str):
        """Fill out Indeed application form"""
        try:
            # Fill contact information
            fields_mapping = {
                'input[name*="name"]': user_profile.get('name', ''),
                'input[name*="email"]': user_profile.get('email', ''),
                'input[name*="phone"]': user_profile.get('phone', ''),
                'textarea[name*="cover"]': cover_letter,
                'textarea[name*="message"]': cover_letter
            }
            
            for selector, value in fields_mapping.items():
                field = await self.page.query_selector(selector)
                if field and value:
                    await field.fill(value)
            
            # Upload resume
            resume_upload = await self.page.query_selector('input[type="file"]')
            if resume_upload and user_profile.get('resume_path'):
                await resume_upload.set_input_files(user_profile['resume_path'])
            
            # Submit
            submit_button = await self.page.query_selector('button[type="submit"], input[type="submit"]')
            if submit_button:
                await submit_button.click()
                await wait_random_delay(2, 3)
            
        except Exception as e:
            logger.warning(f"Error filling Indeed form: {e}")
    
    async def _apply_internshala(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply to Internshala job"""
        # Similar implementation to LinkedIn/Indeed
        return {
            'job_id': job.id,
            'success': False,
            'error': 'Internshala application not implemented',
            'method': 'internshala'
        }
    
    async def _apply_via_email(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply via email"""
        try:
            # Extract email from apply_url (mailto: links)
            apply_url = job.apply_url
            if not apply_url.startswith('mailto:'):
                return {
                    'job_id': job.id,
                    'success': False,
                    'error': 'Not a valid email application URL',
                    'method': 'email'
                }
            
            recipient_email = apply_url.replace('mailto:', '').split('?')[0]
            
            # Create email
            subject = f"Application for {job.title} at {job.company}"
            
            # Send email
            await self._send_application_email(
                recipient_email,
                subject,
                cover_letter,
                user_profile
            )
            
            return {
                'job_id': job.id,
                'success': True,
                'method': 'email',
                'message': f'Application sent via email to {recipient_email}'
            }
            
        except Exception as e:
            return {
                'job_id': job.id,
                'success': False,
                'error': str(e),
                'method': 'email'
            }
    
    async def _send_application_email(self, recipient: str, subject: str, 
                                    cover_letter: str, user_profile: Dict):
        """Send application email"""
        
        # Email configuration
        smtp_host = os.getenv("EMAIL_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("EMAIL_PORT", 587))
        email_user = os.getenv("EMAIL_USERNAME")
        email_password = os.getenv("EMAIL_PASSWORD")
        
        if not email_user or not email_password:
            raise ValueError("Email credentials not configured")
        
        # Create message
        message = MIMEMultipart()
        message["From"] = email_user
        message["To"] = recipient
        message["Subject"] = subject
        
        # Add cover letter as body
        message.attach(MIMEText(cover_letter, "plain"))
        
        # Attach resume if available
        if user_profile.get('resume_path'):
            try:
                with open(user_profile['resume_path'], 'rb') as f:
                    resume_attachment = MIMEText(f.read(), 'base64', 'utf-8')
                    resume_attachment.add_header(
                        'Content-Disposition',
                        f'attachment; filename="{user_profile.get("name", "resume")}_resume.pdf"'
                    )
                    message.attach(resume_attachment)
            except Exception as e:
                logger.warning(f"Could not attach resume: {e}")
        
        # Send email
        try:
            await aiosmtplib.send(
                message,
                hostname=smtp_host,
                port=smtp_port,
                start_tls=True,
                username=email_user,
                password=email_password
            )
            logger.info(f"Application email sent to {recipient}")
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            raise
    
    async def _apply_via_form(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Apply via web form"""
        try:
            if not self.page:
                self.page = await self.browser.new_page()
            
            apply_url = job.apply_url
            await self.page.goto(apply_url)
            await wait_random_delay(3, 5)
            
            # Generic form filling
            await self._fill_generic_application_form(user_profile, cover_letter)
            
            return {
                'job_id': job.id,
                'success': True,
                'method': 'form',
                'message': 'Applied via web form'
            }
            
        except Exception as e:
            return {
                'job_id': job.id,
                'success': False,
                'error': str(e),
                'method': 'form'
            }
    
    async def _fill_generic_application_form(self, user_profile: Dict, cover_letter: str):
        """Fill generic application form"""
        try:
            # Common field patterns
            field_patterns = {
                'name': ['input[name*="name"]', 'input[id*="name"]'],
                'email': ['input[name*="email"]', 'input[id*="email"]'],
                'phone': ['input[name*="phone"]', 'input[id*="phone"]'],
                'cover_letter': ['textarea[name*="cover"]', 'textarea[name*="message"]', 'textarea']
            }
            
            # Fill fields
            for field_type, selectors in field_patterns.items():
                for selector in selectors:
                    field = await self.page.query_selector(selector)
                    if field:
                        value = user_profile.get(field_type, '')
                        if field_type == 'cover_letter':
                            value = cover_letter
                        if value:
                            await field.fill(value)
                        break
            
            # Upload resume
            file_input = await self.page.query_selector('input[type="file"]')
            if file_input and user_profile.get('resume_path'):
                await file_input.set_input_files(user_profile['resume_path'])
            
            # Submit form
            submit_selectors = [
                'button[type="submit"]',
                'input[type="submit"]',
                'button:has-text("Submit")',
                'button:has-text("Apply")'
            ]
            
            for selector in submit_selectors:
                submit_button = await self.page.query_selector(selector)
                if submit_button:
                    await submit_button.click()
                    await wait_random_delay(2, 3)
                    break
            
        except Exception as e:
            logger.warning(f"Error filling generic form: {e}")
    
    async def _apply_generic(self, user_profile: Dict, job, cover_letter: str) -> Dict:
        """Generic application method"""
        return {
            'job_id': job.id,
            'success': False,
            'error': 'Manual application required',
            'method': 'manual',
            'message': 'This job requires manual application'
        }
    
    async def _get_user_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile for applications"""
        user = await database.get_user_by_id(user_id)
        if not user:
            return None
        
        return {
            'user_id': user_id,
            'name': user.name,
            'email': user.email,
            'phone': user.get_preferences().get('phone', ''),
            'resume_path': user.resume_path,
            'skills': user.get_skills(),
            'experience_years': user.experience_years,
            'location': user.location,
            **user.get_preferences()
        }
    
    async def _get_job_details(self, job_id: int):
        """Get job details from database"""
        try:
            from database.db_connection import database
            job = await database.get_job_by_id(job_id)
            return job
        except Exception as e:
            logger.error(f"Error fetching job {job_id}: {e}")
            return None
    
    async def _check_existing_application(self, user_id: int, job_id: int) -> bool:
        """Check if user has already applied to this job"""
        # This would check the database for existing applications
        # For now, return False
        return False
    
    async def _record_application(self, user_id: int, job_id: int, application_result: Dict):
        """Record application in database"""
        application_data = {
            'user_id': user_id,
            'job_id': job_id,
            'applied_at': datetime.utcnow(),
            'status': 'applied',
            'cover_letter': application_result.get('cover_letter', ''),
            'auto_applied': True,
            'application_method': application_result.get('method', 'unknown'),
            'notes': application_result.get('message', '')
        }
        
        # This would save to database
        logger.info(f"Recorded application for user {user_id} to job {job_id}")
    
    async def _get_applications_today(self) -> int:
        """Get number of applications made today"""
        # This would query the database for today's applications
        # For now, return 0
        return 0
    
    def is_healthy(self) -> bool:
        """Check if the auto-apply agent is healthy"""
        return self.browser is not None and self.cover_letter_generator is not None
