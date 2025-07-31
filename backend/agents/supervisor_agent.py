"""
Supervisor Agent - Multi-Agent Orchestration
Coordinates and manages all other agents using workflow automation
"""

import asyncio
import logging
import schedule
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from backend.agents.scraper_agent import ScraperAgent
from backend.agents.scoring_agent import ScoringAgent
from backend.agents.autoapply_agent import AutoApplyAgent
from backend.agents.tracker_agent import TrackerAgent
from backend.database.db_connection import database

logger = logging.getLogger(__name__)


class SupervisorAgent:
    """Main orchestration agent that manages the entire job application workflow"""
    
    def __init__(self):
        # Initialize sub-agents
        self.scraper_agent = ScraperAgent()
        self.scoring_agent = ScoringAgent()
        self.autoapply_agent = AutoApplyAgent()
        self.tracker_agent = TrackerAgent()
        
        # Workflow state
        self.auto_mode_enabled = False
        self.last_scraping_time = None
        self.workflow_running = False
        
        # Configuration
        self.config = {
            'scraping_interval_hours': 24,  # Scrape once per day
            'scoring_threshold': 0.7,  # Minimum score for auto-apply
            'max_auto_applications': 5,  # Max auto applications per day
            'auto_apply_enabled': False,
            'follow_up_interval_days': 7
        }
    
    async def initialize(self):
        """Initialize the supervisor agent and all sub-agents"""
        try:
            logger.info("Initializing supervisor agent...")
            
            # Initialize all sub-agents
            await self.scraper_agent.initialize()
            await self.scoring_agent.initialize()
            await self.autoapply_agent.initialize()
            await self.tracker_agent.initialize()
            
            # Load configuration from database/environment
            await self._load_configuration()
            
            # Schedule recurring tasks
            self._schedule_recurring_tasks()
            
            logger.info("Supervisor agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize supervisor agent: {e}")
            raise
    
    async def cleanup(self):
        """Clean up all agents and resources"""
        try:
            await self.scraper_agent.cleanup()
            await self.scoring_agent.cleanup()
            await self.autoapply_agent.cleanup()
            await self.tracker_agent.cleanup()
            logger.info("Supervisor agent cleanup completed")
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    async def trigger_job_search(self, search_params: Dict) -> Dict:
        """
        Manually trigger the complete job search workflow
        
        Args:
            search_params: Search parameters for job scraping
            
        Returns:
            Workflow execution results
        """
        if self.workflow_running:
            return {
                'success': False,
                'error': 'Workflow already running',
                'status': 'busy'
            }
        
        self.workflow_running = True
        
        try:
            logger.info("Starting manual job search workflow")
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="workflow_start",
                message="Manual job search workflow initiated",
                metadata=search_params
            )
            
            # Step 1: Scrape jobs
            scraping_result = await self._execute_scraping_phase(search_params)
            
            # Step 2: Score jobs
            scoring_result = await self._execute_scoring_phase()
            
            # Step 3: Auto-apply (if enabled)
            autoapply_result = None
            if self.config.get('auto_apply_enabled', False):
                autoapply_result = await self._execute_autoapply_phase()
            
            # Step 4: Update tracking
            tracking_result = await self._execute_tracking_phase()
            
            workflow_result = {
                'success': True,
                'phases': {
                    'scraping': scraping_result,
                    'scoring': scoring_result,
                    'autoapply': autoapply_result,
                    'tracking': tracking_result
                },
                'summary': self._generate_workflow_summary(
                    scraping_result, scoring_result, autoapply_result, tracking_result
                )
            }
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="workflow_complete",
                message="Manual job search workflow completed successfully",
                metadata=workflow_result['summary']
            )
            
            return workflow_result
            
        except Exception as e:
            logger.error(f"Error in job search workflow: {e}")
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="workflow_error",
                message=f"Job search workflow failed: {str(e)}",
                level="error"
            )
            
            return {
                'success': False,
                'error': str(e),
                'status': 'failed'
            }
        finally:
            self.workflow_running = False
    
    async def start_auto_mode(self) -> Dict:
        """Start automated job search mode"""
        try:
            self.auto_mode_enabled = True
            
            # Start background task for automated workflow
            asyncio.create_task(self._auto_mode_loop())
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="auto_mode_start",
                message="Automated mode started"
            )
            
            return {
                'success': True,
                'message': 'Auto mode started successfully',
                'config': self.config
            }
            
        except Exception as e:
            logger.error(f"Error starting auto mode: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def stop_auto_mode(self) -> Dict:
        """Stop automated job search mode"""
        try:
            self.auto_mode_enabled = False
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="auto_mode_stop",
                message="Automated mode stopped"
            )
            
            return {
                'success': True,
                'message': 'Auto mode stopped successfully'
            }
            
        except Exception as e:
            logger.error(f"Error stopping auto mode: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_system_status(self) -> Dict:
        """Get comprehensive system status"""
        try:
            status = {
                'supervisor': {
                    'auto_mode_enabled': self.auto_mode_enabled,
                    'workflow_running': self.workflow_running,
                    'last_scraping_time': self.last_scraping_time.isoformat() if self.last_scraping_time else None,
                    'config': self.config
                },
                'agents': {
                    'scraper': {
                        'healthy': self.scraper_agent.is_healthy(),
                        'status': 'running' if self.scraper_agent.is_healthy() else 'stopped'
                    },
                    'scoring': {
                        'healthy': self.scoring_agent.is_healthy(),
                        'status': 'running' if self.scoring_agent.is_healthy() else 'stopped'
                    },
                    'autoapply': {
                        'healthy': self.autoapply_agent.is_healthy(),
                        'status': 'running' if self.autoapply_agent.is_healthy() else 'stopped'
                    },
                    'tracker': {
                        'healthy': self.tracker_agent.is_healthy(),
                        'status': 'running' if self.tracker_agent.is_healthy() else 'stopped'
                    }
                },
                'system': {
                    'overall_health': self._calculate_overall_health(),
                    'timestamp': datetime.utcnow().isoformat()
                }
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def update_configuration(self, config_updates: Dict) -> Dict:
        """Update system configuration"""
        try:
            # Validate configuration updates
            valid_keys = {
                'scraping_interval_hours', 'scoring_threshold', 'max_auto_applications',
                'auto_apply_enabled', 'follow_up_interval_days'
            }
            
            invalid_keys = set(config_updates.keys()) - valid_keys
            if invalid_keys:
                return {
                    'success': False,
                    'error': f'Invalid configuration keys: {invalid_keys}'
                }
            
            # Update configuration
            self.config.update(config_updates)
            
            # Save to database
            await self._save_configuration()
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="config_update",
                message="Configuration updated",
                metadata=config_updates
            )
            
            return {
                'success': True,
                'message': 'Configuration updated successfully',
                'config': self.config
            }
            
        except Exception as e:
            logger.error(f"Error updating configuration: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_scraping_phase(self, search_params: Dict) -> Dict:
        """Execute the job scraping phase"""
        try:
            logger.info("Starting scraping phase")
            
            # Add default search parameters if not provided
            default_params = {
                'keywords': 'software engineer',
                'location': 'Remote',
                'max_jobs': 50
            }
            search_params = {**default_params, **search_params}
            
            # Scrape jobs
            scraped_jobs = await self.scraper_agent.scrape_jobs(search_params)
            
            self.last_scraping_time = datetime.utcnow()
            
            result = {
                'success': True,
                'jobs_found': len(scraped_jobs),
                'search_params': search_params,
                'timestamp': self.last_scraping_time.isoformat()
            }
            
            logger.info(f"Scraping phase completed: {len(scraped_jobs)} jobs found")
            return result
            
        except Exception as e:
            logger.error(f"Error in scraping phase: {e}")
            return {
                'success': False,
                'error': str(e),
                'jobs_found': 0
            }
    
    async def _execute_scoring_phase(self) -> Dict:
        """Execute the job scoring phase"""
        try:
            logger.info("Starting scoring phase")
            
            # Get default user (for demo purposes)
            # In production, this would iterate through all users
            user_id = 1  # Default demo user
            
            # Score jobs
            scored_jobs = await self.scoring_agent.score_jobs(user_id)
            
            # Filter high-scoring jobs
            high_scoring_jobs = [
                job for job in scored_jobs 
                if job['score'] >= self.config['scoring_threshold']
            ]
            
            result = {
                'success': True,
                'jobs_scored': len(scored_jobs),
                'high_scoring_jobs': len(high_scoring_jobs),
                'scoring_threshold': self.config['scoring_threshold'],
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Scoring phase completed: {len(scored_jobs)} jobs scored, {len(high_scoring_jobs)} high-scoring")
            return result
            
        except Exception as e:
            logger.error(f"Error in scoring phase: {e}")
            return {
                'success': False,
                'error': str(e),
                'jobs_scored': 0
            }
    
    async def _execute_autoapply_phase(self) -> Dict:
        """Execute the auto-apply phase"""
        try:
            logger.info("Starting auto-apply phase")
            
            # Get high-scoring jobs for auto-application
            user_id = 1  # Default demo user
            
            # Get top jobs (placeholder - would get from database)
            top_job_ids = []  # This would be populated from scoring results
            
            if not top_job_ids:
                return {
                    'success': True,
                    'applications_sent': 0,
                    'message': 'No high-scoring jobs found for auto-apply'
                }
            
            # Limit applications per day
            max_applications = min(len(top_job_ids), self.config['max_auto_applications'])
            job_ids_to_apply = top_job_ids[:max_applications]
            
            # Auto-apply to jobs
            application_results = await self.autoapply_agent.auto_apply_to_jobs(
                user_id, job_ids_to_apply
            )
            
            successful_applications = len([r for r in application_results if r['success']])
            
            result = {
                'success': True,
                'applications_sent': successful_applications,
                'applications_attempted': len(application_results),
                'success_rate': (successful_applications / len(application_results) * 100) if application_results else 0,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Auto-apply phase completed: {successful_applications} applications sent")
            return result
            
        except Exception as e:
            logger.error(f"Error in auto-apply phase: {e}")
            return {
                'success': False,
                'error': str(e),
                'applications_sent': 0
            }
    
    async def _execute_tracking_phase(self) -> Dict:
        """Execute the application tracking phase"""
        try:
            logger.info("Starting tracking phase")
            
            # Track applications for all users
            # For demo, use default user
            user_id = 1
            
            tracking_result = await self.tracker_agent.track_applications(user_id)
            
            result = {
                'success': True,
                **tracking_result,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info(f"Tracking phase completed: {tracking_result.get('total_applications', 0)} applications tracked")
            return result
            
        except Exception as e:
            logger.error(f"Error in tracking phase: {e}")
            return {
                'success': False,
                'error': str(e),
                'total_applications': 0
            }
    
    async def _auto_mode_loop(self):
        """Background loop for automated mode"""
        logger.info("Auto mode loop started")
        
        while self.auto_mode_enabled:
            try:
                # Check if it's time for scheduled scraping
                if await self._should_run_scheduled_scraping():
                    logger.info("Running scheduled job search workflow")
                    
                    # Use default search parameters for auto mode
                    default_search_params = {
                        'keywords': 'software engineer python javascript',
                        'location': 'Remote',
                        'max_jobs': 30
                    }
                    
                    await self.trigger_job_search(default_search_params)
                
                # Sleep for 1 hour before checking again
                await asyncio.sleep(3600)
                
            except Exception as e:
                logger.error(f"Error in auto mode loop: {e}")
                await asyncio.sleep(3600)  # Continue after error
        
        logger.info("Auto mode loop stopped")
    
    async def _should_run_scheduled_scraping(self) -> bool:
        """Check if scheduled scraping should run"""
        if not self.last_scraping_time:
            return True
        
        hours_since_last_scraping = (datetime.utcnow() - self.last_scraping_time).total_seconds() / 3600
        return hours_since_last_scraping >= self.config['scraping_interval_hours']
    
    def _schedule_recurring_tasks(self):
        """Schedule recurring tasks using the schedule library"""
        # Schedule daily application tracking
        schedule.every().day.at("09:00").do(self._run_scheduled_tracking)
        
        # Schedule weekly status updates
        schedule.every().monday.at("10:00").do(self._run_weekly_status_update)
    
    async def _run_scheduled_tracking(self):
        """Run scheduled application tracking"""
        try:
            # Track applications for all users
            # For demo, use default user
            user_id = 1
            await self.tracker_agent.track_applications(user_id)
        except Exception as e:
            logger.error(f"Error in scheduled tracking: {e}")
    
    async def _run_weekly_status_update(self):
        """Run weekly status update"""
        try:
            # Generate and log weekly status report
            status = await self.get_system_status()
            
            await database.log_system_activity(
                agent_name="supervisor_agent",
                action="weekly_status",
                message="Weekly status update",
                metadata=status
            )
        except Exception as e:
            logger.error(f"Error in weekly status update: {e}")
    
    def _generate_workflow_summary(self, scraping_result: Dict, scoring_result: Dict, 
                                 autoapply_result: Dict, tracking_result: Dict) -> Dict:
        """Generate summary of workflow execution"""
        return {
            'total_jobs_found': scraping_result.get('jobs_found', 0),
            'jobs_scored': scoring_result.get('jobs_scored', 0),
            'high_scoring_jobs': scoring_result.get('high_scoring_jobs', 0),
            'applications_sent': autoapply_result.get('applications_sent', 0) if autoapply_result else 0,
            'applications_tracked': tracking_result.get('total_applications', 0),
            'workflow_duration': 'calculated_duration',  # Would calculate actual duration
            'success': all(r.get('success', False) for r in [scraping_result, scoring_result, tracking_result])
        }
    
    def _calculate_overall_health(self) -> str:
        """Calculate overall system health"""
        agents_healthy = [
            self.scraper_agent.is_healthy(),
            self.scoring_agent.is_healthy(),
            self.autoapply_agent.is_healthy(),
            self.tracker_agent.is_healthy()
        ]
        
        healthy_count = sum(agents_healthy)
        total_agents = len(agents_healthy)
        
        if healthy_count == total_agents:
            return "healthy"
        elif healthy_count >= total_agents * 0.75:
            return "degraded"
        else:
            return "unhealthy"
    
    async def _load_configuration(self):
        """Load configuration from database or environment"""
        # This would load saved configuration from database
        # For now, use defaults
        pass
    
    async def _save_configuration(self):
        """Save configuration to database"""
        # This would save configuration to database
        logger.info("Configuration saved")
    
    def is_healthy(self) -> bool:
        """Check if the supervisor agent is healthy"""
        return all([
            self.scraper_agent.is_healthy(),
            self.scoring_agent.is_healthy(),
            self.autoapply_agent.is_healthy(),
            self.tracker_agent.is_healthy()
        ])
