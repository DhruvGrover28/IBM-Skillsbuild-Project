"""
Prompt Templates for AI-Generated Content
Cover letter generation and other AI-powered text generation
"""

import os
import logging
from typing import Dict, Optional
import openai

logger = logging.getLogger(__name__)


class CoverLetterGenerator:
    """Generate personalized cover letters using AI"""
    
    def __init__(self):
        self.openai_client = None
        self.default_template = self._get_default_template()
        self.templates = {
            'default': self.default_template,
            'technical': self._get_technical_template(),
            'entry_level': self._get_entry_level_template(),
            'executive': self._get_executive_template()
        }
    
    async def initialize(self):
        """Initialize the cover letter generator"""
        try:
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                self.openai_client = openai.AsyncOpenAI(api_key=openai_api_key)
                logger.info("Cover letter generator initialized with OpenAI")
            else:
                logger.warning("OpenAI API key not found, using template-based generation")
        except Exception as e:
            logger.error(f"Failed to initialize cover letter generator: {e}")
            raise
    
    async def generate_cover_letter(self, user_profile: Dict, job, template_type: str = 'default') -> str:
        """
        Generate a personalized cover letter
        
        Args:
            user_profile: User profile dictionary
            job: Job object or dictionary
            template_type: Type of template to use
            
        Returns:
            Generated cover letter text
        """
        try:
            if self.openai_client:
                return await self._generate_ai_cover_letter(user_profile, job)
            else:
                return self._generate_template_cover_letter(user_profile, job, template_type)
        except Exception as e:
            logger.error(f"Error generating cover letter: {e}")
            return self._generate_fallback_cover_letter(user_profile, job)
    
    async def _generate_ai_cover_letter(self, user_profile: Dict, job) -> str:
        """Generate cover letter using OpenAI"""
        
        # Extract job details
        job_title = getattr(job, 'title', job.get('title', 'Unknown Position'))
        company = getattr(job, 'company', job.get('company', 'Unknown Company'))
        job_description = getattr(job, 'description', job.get('description', ''))
        requirements = getattr(job, 'requirements', job.get('requirements', ''))
        
        # Create prompt
        prompt = self._create_ai_prompt(user_profile, job_title, company, job_description, requirements)
        
        try:
            response = await self.openai_client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-3.5-turbo"),
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional career counselor and expert writer. Generate personalized, compelling cover letters that highlight relevant skills and experience for specific job applications."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=800,
                temperature=0.7
            )
            
            cover_letter = response.choices[0].message.content.strip()
            
            # Post-process the cover letter
            cover_letter = self._post_process_cover_letter(cover_letter, user_profile)
            
            return cover_letter
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            return self._generate_template_cover_letter(user_profile, job, 'default')
    
    def _create_ai_prompt(self, user_profile: Dict, job_title: str, company: str, 
                         job_description: str, requirements: str) -> str:
        """Create AI prompt for cover letter generation"""
        
        user_name = user_profile.get('name', 'John Doe')
        user_skills = ', '.join(user_profile.get('skills', []))
        experience_years = user_profile.get('experience_years', 0)
        location = user_profile.get('location', '')
        
        prompt = f"""
Write a professional cover letter for the following job application:

APPLICANT INFORMATION:
- Name: {user_name}
- Skills: {user_skills}
- Experience: {experience_years} years
- Location: {location}

JOB INFORMATION:
- Position: {job_title}
- Company: {company}
- Job Description: {job_description[:500]}...
- Requirements: {requirements[:300]}...

REQUIREMENTS FOR THE COVER LETTER:
1. Keep it concise (3-4 paragraphs, ~300 words)
2. Start with a strong opening that mentions the specific position
3. Highlight 2-3 most relevant skills/experiences that match the job requirements
4. Show enthusiasm for the company and role
5. Include a professional closing with call to action
6. Use a professional but personable tone
7. Avoid generic phrases and make it specific to this job
8. Do not include placeholder text like [Your Name] or [Company Name]

Generate the cover letter now:
"""
        return prompt
    
    def _post_process_cover_letter(self, cover_letter: str, user_profile: Dict) -> str:
        """Post-process the generated cover letter"""
        
        # Replace any remaining placeholders
        replacements = {
            '[Your Name]': user_profile.get('name', ''),
            '[Your Email]': user_profile.get('email', ''),
            '[Your Phone]': user_profile.get('phone', ''),
            '[Date]': self._get_current_date()
        }
        
        for placeholder, replacement in replacements.items():
            cover_letter = cover_letter.replace(placeholder, replacement)
        
        # Ensure proper formatting
        lines = cover_letter.split('\n')
        formatted_lines = []
        
        for line in lines:
            line = line.strip()
            if line:
                formatted_lines.append(line)
        
        return '\n\n'.join(formatted_lines)
    
    def _generate_template_cover_letter(self, user_profile: Dict, job, template_type: str) -> str:
        """Generate cover letter using templates"""
        
        template = self.templates.get(template_type, self.default_template)
        
        # Extract variables for template
        variables = self._extract_template_variables(user_profile, job)
        
        # Fill template
        try:
            cover_letter = template.format(**variables)
            return cover_letter
        except KeyError as e:
            logger.warning(f"Template variable missing: {e}")
            return self._generate_fallback_cover_letter(user_profile, job)
    
    def _extract_template_variables(self, user_profile: Dict, job) -> Dict:
        """Extract variables for template filling"""
        
        # Job details
        job_title = getattr(job, 'title', job.get('title', 'this position'))
        company = getattr(job, 'company', job.get('company', 'your company'))
        
        # User details
        name = user_profile.get('name', 'John Doe')
        skills = user_profile.get('skills', [])
        experience_years = user_profile.get('experience_years', 0)
        
        # Select top 3 relevant skills
        top_skills = skills[:3] if len(skills) >= 3 else skills
        skills_text = ', '.join(top_skills) if top_skills else 'various technical skills'
        
        # Experience level text
        if experience_years == 0:
            experience_text = "recent graduate eager to begin my career"
        elif experience_years <= 2:
            experience_text = f"professional with {experience_years} years of experience"
        elif experience_years <= 5:
            experience_text = f"experienced professional with {experience_years} years in the field"
        else:
            experience_text = f"senior professional with {experience_years}+ years of expertise"
        
        return {
            'name': name,
            'date': self._get_current_date(),
            'job_title': job_title,
            'company': company,
            'skills': skills_text,
            'experience_text': experience_text,
            'experience_years': experience_years,
            'top_skill_1': top_skills[0] if len(top_skills) > 0 else 'technical skills',
            'top_skill_2': top_skills[1] if len(top_skills) > 1 else 'problem-solving',
            'top_skill_3': top_skills[2] if len(top_skills) > 2 else 'teamwork'
        }
    
    def _generate_fallback_cover_letter(self, user_profile: Dict, job) -> str:
        """Generate a basic fallback cover letter"""
        
        name = user_profile.get('name', 'John Doe')
        job_title = getattr(job, 'title', job.get('title', 'this position'))
        company = getattr(job, 'company', job.get('company', 'your company'))
        
        return f"""Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. As a motivated professional with relevant skills and experience, I am excited about the opportunity to contribute to your team.

My background includes experience with various technologies and a passion for continuous learning. I am particularly drawn to this role because it aligns with my career goals and offers the opportunity to work with a respected organization like {company}.

I would welcome the opportunity to discuss how my skills and enthusiasm can contribute to your team's success. Thank you for considering my application, and I look forward to hearing from you.

Sincerely,
{name}"""
    
    def _get_default_template(self) -> str:
        """Get the default cover letter template"""
        return """Dear Hiring Manager,

I am writing to express my strong interest in the {job_title} position at {company}. As a {experience_text}, I am excited about the opportunity to contribute to your team with my skills in {skills}.

Throughout my career, I have developed strong expertise in {top_skill_1}, {top_skill_2}, and {top_skill_3}. These skills, combined with my {experience_years} years of experience, have prepared me to make meaningful contributions to {company}. I am particularly drawn to this role because it aligns perfectly with my technical background and career aspirations.

What excites me most about this opportunity is the chance to work with a forward-thinking company like {company}. I am confident that my technical skills, problem-solving abilities, and passion for innovation would make me a valuable addition to your team.

I would welcome the opportunity to discuss how my background and enthusiasm can contribute to {company}'s continued success. Thank you for considering my application, and I look forward to hearing from you.

Sincerely,
{name}"""
    
    def _get_technical_template(self) -> str:
        """Get template for technical positions"""
        return """Dear Hiring Team,

I am excited to apply for the {job_title} position at {company}. With {experience_years} years of experience in software development and a strong foundation in {skills}, I am confident in my ability to contribute effectively to your engineering team.

In my previous roles, I have gained extensive experience with {top_skill_1} and {top_skill_2}, which are directly relevant to this position. My technical expertise includes {top_skill_3} and various other technologies that enable me to build scalable, efficient solutions. I am particularly interested in this role because it offers the opportunity to work on challenging technical problems at {company}.

I am impressed by {company}'s commitment to innovation and technical excellence. I would be thrilled to bring my passion for clean code, best practices, and continuous improvement to your team.

Thank you for your time and consideration. I look forward to the opportunity to discuss how my technical skills and enthusiasm can contribute to {company}'s engineering goals.

Best regards,
{name}"""
    
    def _get_entry_level_template(self) -> str:
        """Get template for entry-level positions"""
        return """Dear Hiring Manager,

I am writing to express my enthusiasm for the {job_title} position at {company}. As a {experience_text}, I am eager to begin my career with a respected organization and contribute my fresh perspective and strong foundational skills.

During my studies and projects, I have developed proficiency in {skills}, which I believe are highly relevant to this role. While I may be new to the professional world, I bring dedication, a strong work ethic, and a genuine passion for learning and growth. I am particularly excited about this opportunity because it aligns with my career goals and offers the chance to learn from experienced professionals at {company}.

I am drawn to {company} because of its reputation for excellence and commitment to employee development. I am confident that my enthusiasm, technical foundation, and willingness to learn would make me a valuable addition to your team.

I would be grateful for the opportunity to discuss how my skills and eagerness to contribute can benefit {company}. Thank you for considering my application.

Sincerely,
{name}"""
    
    def _get_executive_template(self) -> str:
        """Get template for executive/senior positions"""
        return """Dear Executive Team,

I am pleased to submit my application for the {job_title} position at {company}. With {experience_years} years of leadership experience and a proven track record in {skills}, I am excited about the opportunity to contribute to {company}'s strategic objectives.

Throughout my career, I have successfully led teams and initiatives in {top_skill_1}, {top_skill_2}, and {top_skill_3}. My experience includes driving organizational growth, implementing strategic initiatives, and building high-performing teams. I am particularly drawn to this role because it represents an opportunity to leverage my expertise to make a significant impact at {company}.

What impresses me most about {company} is its vision and commitment to excellence. I am confident that my leadership experience, strategic thinking, and results-driven approach would contribute meaningfully to your continued success.

I would welcome the opportunity to discuss how my experience and leadership capabilities can support {company}'s goals. Thank you for your consideration.

Best regards,
{name}"""
    
    def _get_current_date(self) -> str:
        """Get current date in proper format"""
        from datetime import datetime
        return datetime.now().strftime("%B %d, %Y")


class EmailTemplates:
    """Templates for various email communications"""
    
    @staticmethod
    def get_follow_up_email_template() -> str:
        """Template for follow-up emails"""
        return """Subject: Following up on my application for {job_title}

Dear Hiring Manager,

I hope this email finds you well. I am writing to follow up on my application for the {job_title} position at {company}, which I submitted on {application_date}.

I remain very interested in this opportunity and would welcome the chance to discuss how my skills and experience can contribute to your team. If you need any additional information or have any questions about my application, please don't hesitate to reach out.

Thank you for your time and consideration. I look forward to hearing from you.

Best regards,
{name}
{email}
{phone}"""
    
    @staticmethod
    def get_interview_thank_you_template() -> str:
        """Template for post-interview thank you emails"""
        return """Subject: Thank you for the interview - {job_title} position

Dear {interviewer_name},

Thank you for taking the time to speak with me about the {job_title} position at {company}. I enjoyed our conversation and learning more about the role and your team.

Our discussion reinforced my enthusiasm for this opportunity. I am particularly excited about {specific_topic_discussed} and believe my experience with {relevant_skill} would enable me to contribute effectively to your team's goals.

Please don't hesitate to reach out if you need any additional information. I look forward to the next steps in the process.

Best regards,
{name}"""
    
    @staticmethod
    def get_application_withdrawal_template() -> str:
        """Template for withdrawing applications"""
        return """Subject: Withdrawal of application for {job_title}

Dear Hiring Manager,

I am writing to formally withdraw my application for the {job_title} position at {company}.

After careful consideration, I have decided to pursue other opportunities that are more aligned with my current career goals. I appreciate the time and consideration you have given to my application.

I have great respect for {company} and hope our paths may cross again in the future.

Thank you for your understanding.

Best regards,
{name}"""


class ResumeTemplates:
    """Templates for resume optimization suggestions"""
    
    @staticmethod
    def get_skill_optimization_prompt() -> str:
        """Prompt for optimizing skills section based on job requirements"""
        return """Analyze the following job requirements and suggest how to optimize the candidate's skills section:

Job Requirements:
{job_requirements}

Current Skills:
{current_skills}

Please provide:
1. Skills to emphasize (from current skills that match requirements)
2. Skills to add (if the candidate likely has them but didn't list them)
3. Skills to de-emphasize (not relevant to this job)
4. Skill gaps to address

Format your response as a structured recommendation."""
    
    @staticmethod
    def get_experience_optimization_prompt() -> str:
        """Prompt for optimizing experience descriptions"""
        return """Help optimize this work experience description to better match the job requirements:

Job Title: {job_title}
Company: {company}
Job Requirements: {job_requirements}

Current Experience Description:
{current_description}

Please rewrite the experience description to:
1. Highlight relevant achievements
2. Use keywords from the job requirements
3. Quantify accomplishments where possible
4. Make it more compelling for this specific role

Provide the optimized description."""
