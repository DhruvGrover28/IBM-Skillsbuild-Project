"""
Simple Supervisor Agent - Windows Compatible Version
Uses the simple scraper instead of Playwright-based scraper
"""

import asyncio
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from .simple_scraper_agent import SimpleScraperAgent, JobListing
from database.db_connection import Database
from .autoapply_agent import AutoApplyAgent
# from .scoring_agent import ScoringAgent  # Temporarily disabled due to PyTorch memory issues

logger = logging.getLogger(__name__)

class SimpleSupervisorAgent:
    """
    A simplified supervisor agent that coordinates job search activities
    without requiring browser automation or complex subprocess management.
    """
    
    def __init__(self):
        self.scraper_agent = SimpleScraperAgent()
        self.database = Database()
        self.autoapply_agent = AutoApplyAgent()
        # self.scoring_agent = ScoringAgent()  # Temporarily disabled due to PyTorch memory issues
        self.scoring_agent = None  # Placeholder
        self.is_auto_mode = False
        self.auto_task = None
        self.last_search_time = None
        self.search_results_cache = {}
        self.max_cache_age = timedelta(hours=1)  # Cache results for 1 hour
        
        # Auto-apply settings
        self.auto_apply_enabled = False
        self.auto_apply_threshold = 80.0  # Default threshold score
        self.max_auto_applies_per_day = 10
    
    async def initialize(self):
        """Initialize the supervisor agent"""
        try:
            await self.scraper_agent.initialize()
            
            # Try to initialize auto-apply agent with graceful failure handling
            try:
                await self.autoapply_agent.initialize()
                logger.info("Auto-apply agent initialized successfully")
            except Exception as e:
                logger.warning(f"Auto-apply agent initialization failed: {e}")
                logger.info("Continuing without auto-apply functionality")
            
            # Temporarily disable scoring agent due to PyTorch memory issues
            try:
                if self.scoring_agent:
                    await self.scoring_agent.initialize()
                    logger.info("Scoring agent initialized successfully")
                else:
                    logger.info("Scoring agent disabled - using simplified scoring")
            except Exception as e:
                logger.warning(f"Scoring agent initialization failed: {e}")
                logger.info("Continuing without ML scoring functionality")
            
            logger.info("Simple supervisor agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize simple supervisor agent: {e}")
            raise
    
    async def cleanup(self):
        """Clean up resources"""
        if self.auto_task:
            self.auto_task.cancel()
        
        if self.scraper_agent:
            await self.scraper_agent.cleanup()
        
        if self.autoapply_agent:
            await self.autoapply_agent.cleanup()
        
        logger.info("Simple supervisor agent cleaned up")
    
    async def trigger_job_search(self, search_params: Dict) -> Dict:
        """
        Trigger a manual job search
        
        Args:
            search_params: Dict with search criteria
        
        Returns:
            Dict with search results and metadata
        """
        try:
            logger.info(f"Starting job search with params: {search_params}")
            
            # Create cache key
            cache_key = self._create_cache_key(search_params)
            
            # Check cache first
            if self._is_cache_valid(cache_key):
                logger.info("Returning cached results")
                return self.search_results_cache[cache_key]
            
            # Perform search
            start_time = datetime.now()
            jobs = await self.scraper_agent.scrape_jobs(search_params)
            search_duration = (datetime.now() - start_time).total_seconds()
            
            # Convert JobListing objects to dicts and save to database
            job_dicts = []
            for job in jobs:
                job_dict = {
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'apply_url': job.url,  # Map url to apply_url
                    'job_type': job.job_type,
                    'experience_level': job.experience,
                    'source': 'remoteok',  # Set source
                    'posted_date': job.date_posted,
                    'external_id': f"remoteok_{hash(job.title + job.company)}"  # Generate external_id
                }
                job_dicts.append(job_dict)
            
            # Save jobs to database if any were found
            saved_jobs = []
            if job_dicts:
                try:
                    saved_jobs = await self.database.save_jobs(job_dicts)
                    logger.info(f"Saved {len(saved_jobs)} jobs to database")
                except Exception as e:
                    logger.error(f"Failed to save jobs to database: {e}")
            
            # Prepare response with original job format for frontend
            response_jobs = []
            for job in jobs:
                job_dict = {
                    'title': job.title,
                    'company': job.company,
                    'location': job.location,
                    'description': job.description,
                    'url': job.url,
                    'salary': job.salary,
                    'date_posted': job.date_posted,
                    'job_type': job.job_type,
                    'experience': job.experience,
                    'skills': job.skills or []
                }
                response_jobs.append(job_dict)
            
            # Prepare response
            result = {
                'success': True,
                'search_params': search_params,
                'jobs': response_jobs,
                'total_found': len(response_jobs),
                'saved_to_db': len(saved_jobs),
                'search_duration_seconds': search_duration,
                'timestamp': datetime.now().isoformat(),
                'cache_key': cache_key
            }
            
            # Cache the results
            self.search_results_cache[cache_key] = result
            self.last_search_time = datetime.now()
            
            logger.info(f"Job search completed: found {len(job_dicts)} jobs in {search_duration:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Job search failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'search_params': search_params,
                'timestamp': datetime.now().isoformat()
            }
    
    async def start_auto_mode(self, search_params: Optional[Dict] = None) -> Dict:
        """
        Start automated job search mode
        
        Args:
            search_params: Optional search parameters, uses defaults if not provided
        
        Returns:
            Dict with operation status
        """
        try:
            if self.is_auto_mode:
                return {
                    'success': False,
                    'message': 'Auto mode is already running',
                    'status': 'already_running'
                }
            
            # Use default search params if not provided
            if not search_params:
                search_params = {
                    'keywords': 'software developer',
                    'location': 'India',
                    'max_results': 50
                }
            
            self.is_auto_mode = True
            self.auto_task = asyncio.create_task(
                self._auto_search_loop(search_params)
            )
            
            logger.info("Auto mode started")
            return {
                'success': True,
                'message': 'Auto mode started successfully',
                'search_params': search_params,
                'status': 'started'
            }
            
        except Exception as e:
            logger.error(f"Failed to start auto mode: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    async def stop_auto_mode(self) -> Dict:
        """
        Stop automated job search mode
        
        Returns:
            Dict with operation status
        """
        try:
            if not self.is_auto_mode:
                return {
                    'success': False,
                    'message': 'Auto mode is not running',
                    'status': 'not_running'
                }
            
            self.is_auto_mode = False
            
            if self.auto_task:
                self.auto_task.cancel()
                try:
                    await self.auto_task
                except asyncio.CancelledError:
                    pass
                self.auto_task = None
            
            logger.info("Auto mode stopped")
            return {
                'success': True,
                'message': 'Auto mode stopped successfully',
                'status': 'stopped'
            }
            
        except Exception as e:
            logger.error(f"Failed to stop auto mode: {e}")
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
    
    async def get_system_status(self) -> Dict:
        """
        Get current system status
        
        Returns:
            Dict with system status information
        """
        try:
            # Test scraper connection
            scraper_healthy = False
            if self.scraper_agent:
                scraper_healthy = await self.scraper_agent.test_connection()
            
            status = {
                'supervisor_agent': {
                    'status': 'running',
                    'auto_mode_active': self.is_auto_mode,
                    'last_search_time': self.last_search_time.isoformat() if self.last_search_time else None,
                    'cached_searches': len(self.search_results_cache)
                },
                'scraper_agent': {
                    'status': 'running' if scraper_healthy else 'error',
                    'healthy': scraper_healthy,
                    'type': 'simple_http_scraper'
                },
                'system': {
                    'timestamp': datetime.now().isoformat(),
                    'uptime_info': 'Available',
                    'version': '1.0.0-simple'
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _auto_search_loop(self, search_params: Dict):
        """
        Auto search loop that runs periodically
        """
        search_interval = 3600  # 1 hour in seconds
        
        try:
            while self.is_auto_mode:
                logger.info("Running automated job search")
                
                # Perform search
                result = await self.trigger_job_search(search_params)
                
                if result.get('success'):
                    logger.info(f"Auto search found {result.get('total_found', 0)} jobs")
                else:
                    logger.error(f"Auto search failed: {result.get('error', 'Unknown error')}")
                
                # Wait for next search
                await asyncio.sleep(search_interval)
                
        except asyncio.CancelledError:
            logger.info("Auto search loop cancelled")
        except Exception as e:
            logger.error(f"Auto search loop error: {e}")
            self.is_auto_mode = False
    
    def _create_cache_key(self, search_params: Dict) -> str:
        """Create a cache key from search parameters"""
        # Create a normalized key from search params
        key_parts = [
            search_params.get('keywords', '').lower().strip(),
            search_params.get('location', '').lower().strip(),
            str(search_params.get('max_results', 50))
        ]
        return '|'.join(key_parts)
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached results are still valid"""
        if cache_key not in self.search_results_cache:
            return False
        
        cached_result = self.search_results_cache[cache_key]
        cached_time = datetime.fromisoformat(cached_result['timestamp'])
        
        return datetime.now() - cached_time < self.max_cache_age
    
    def is_healthy(self) -> bool:
        """Check if the supervisor agent is healthy"""
        return (
            self.scraper_agent is not None and 
            self.scraper_agent.is_healthy()
        )
    
    async def apply_to_job(self, user_id: int, job_id: int) -> Dict:
        """Apply to a specific job manually"""
        try:
            logger.info(f"Manual apply triggered for user {user_id}, job {job_id}")
            
            # Apply using auto-apply agent
            results = await self.autoapply_agent.auto_apply_to_jobs(user_id, [job_id])
            
            if results:
                result = results[0]
                return {
                    'success': result.get('success', False),
                    'job_id': job_id,
                    'user_id': user_id,
                    'method': result.get('method', 'unknown'),
                    'message': 'Application submitted successfully' if result.get('success') else 'Application failed',
                    'error': result.get('error'),
                    'timestamp': datetime.now().isoformat()
                }
            else:
                return {
                    'success': False,
                    'job_id': job_id,
                    'user_id': user_id,
                    'message': 'No application results returned',
                    'timestamp': datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"Error in manual apply for job {job_id}: {e}")
            return {
                'success': False,
                'job_id': job_id,
                'user_id': user_id,
                'error': str(e),
                'message': 'Application failed due to error',
                'timestamp': datetime.now().isoformat()
            }
    
    async def enable_auto_apply(self, user_id: int, threshold: float = 80.0, max_per_day: int = 10) -> Dict:
        """Enable automatic job applications for high-scoring jobs"""
        try:
            self.auto_apply_enabled = True
            self.auto_apply_threshold = threshold
            self.max_auto_applies_per_day = max_per_day
            
            logger.info(f"Auto-apply enabled for user {user_id} with threshold {threshold}")
            
            return {
                'success': True,
                'message': f'Auto-apply enabled with {threshold}% threshold',
                'user_id': user_id,
                'threshold': threshold,
                'max_per_day': max_per_day,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error enabling auto-apply: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to enable auto-apply',
                'timestamp': datetime.now().isoformat()
            }
    
    async def configure_auto_apply(self, config: Dict) -> Dict:
        """Configure auto-apply settings"""
        try:
            if 'enabled' in config:
                self.auto_apply_enabled = config['enabled']
            if 'threshold' in config:
                self.auto_apply_threshold = config['threshold']
            if 'max_per_day' in config:
                self.max_auto_applies_per_day = config['max_per_day']
            
            logger.info(f"Auto-apply configured: enabled={self.auto_apply_enabled}, threshold={self.auto_apply_threshold}")
            return {
                'success': True,
                'message': 'Auto-apply configuration updated',
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error configuring auto-apply: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to configure auto-apply',
                'timestamp': datetime.now().isoformat()
            }
    
    async def disable_auto_apply(self) -> Dict:
        """Disable automatic job applications"""
        try:
            self.auto_apply_enabled = False
            logger.info("Auto-apply disabled")
            
            return {
                'success': True,
                'message': 'Auto-apply disabled',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error disabling auto-apply: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Failed to disable auto-apply',
                'timestamp': datetime.now().isoformat()
            }
    
    async def check_and_auto_apply(self, user_id: int) -> Dict:
        """Check for high-scoring jobs and auto-apply if enabled"""
        if not self.auto_apply_enabled:
            return {
                'success': False,
                'message': 'Auto-apply is not enabled',
                'timestamp': datetime.now().isoformat()
            }
        
        try:
            # Get user profile for scoring
            # This would typically get scored jobs above threshold
            # For now, we'll implement a basic version
            
            logger.info(f"Checking for auto-apply opportunities for user {user_id}")
            
            # Get recent jobs that haven't been applied to
            # Score them and apply to high-scoring ones
            # This is a simplified implementation
            
            return {
                'success': True,
                'message': 'Auto-apply check completed',
                'user_id': user_id,
                'threshold': self.auto_apply_threshold,
                'checked_jobs': 0,
                'applied_jobs': 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in auto-apply check: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'Auto-apply check failed',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_auto_apply_status(self) -> Dict:
        """Get current auto-apply settings and status"""
        return {
            'enabled': self.auto_apply_enabled,
            'threshold': self.auto_apply_threshold,
            'max_per_day': self.max_auto_applies_per_day,
            'applications_today': getattr(self.autoapply_agent, 'applications_today', 0),
            'timestamp': datetime.now().isoformat()
        }
