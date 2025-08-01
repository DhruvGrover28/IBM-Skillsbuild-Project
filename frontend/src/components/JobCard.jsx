import React, { useState } from 'react';
import { MapPin, Building, Calendar, ExternalLink, CheckCircle, AlertCircle } from 'lucide-react';
import ScoreTag from './ScoreTag';

const JobCard = ({ job, onViewDetails, onStatusUpdate }) => {
  const [isApplying, setIsApplying] = useState(false);
  
  const {
    id,
    title,
    company,
    location,
    description,
    requirements,
    salary_range,
    job_type,
    posted_date,
    application_url,
    apply_url, // Also check for apply_url from backend
    match_score,
    skillMatchScore, // New skill match score from scoring agent
    status
  } = job;

  // Use apply_url if application_url is not available
  const jobUrl = application_url || apply_url;

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'applied':
        return 'bg-blue-100 text-blue-800';
      case 'interview':
        return 'bg-yellow-100 text-yellow-800';
      case 'offered':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  return (
    <div className="card p-6 hover:shadow-md transition-shadow duration-200">
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
          <div className="flex items-center text-gray-600 mb-2">
            <Building className="w-4 h-4 mr-1" />
            <span className="font-medium">{company}</span>
          </div>
          <div className="flex items-center text-gray-500 mb-2">
            <MapPin className="w-4 h-4 mr-1" />
            <span>{location}</span>
          </div>
          <div className="flex items-center text-gray-500">
            <Calendar className="w-4 h-4 mr-1" />
            <span>Posted: {formatDate(posted_date)}</span>
          </div>
        </div>
        
        <div className="flex flex-col items-end space-y-2">
          <ScoreTag score={skillMatchScore || match_score} />
          {status && (
            <span className={`badge ${getStatusColor(status)}`}>
              {status}
            </span>
          )}
        </div>
      </div>

      <div className="mb-4">
        <p className="text-gray-700 text-sm line-clamp-3">
          {description}
        </p>
      </div>

      {/* Skills Analysis Section */}
      {(job.matchingSkills || job.missingSkills) && (
        <div className="mb-4 p-3 bg-gray-50 rounded-lg border">
          <h4 className="text-sm font-medium text-gray-900 mb-3">Skills Analysis</h4>
          
          {/* Matching Skills */}
          {job.matchingSkills && job.matchingSkills.length > 0 && (
            <div className="mb-3">
              <div className="flex items-center gap-2 mb-2">
                <CheckCircle className="w-4 h-4 text-green-600" />
                <span className="text-sm font-medium text-green-700">
                  Skills You Have ({job.matchingSkills.length})
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {job.matchingSkills.map((skill, index) => (
                  <span 
                    key={index} 
                    className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full border border-green-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Missing Skills */}
          {job.missingSkills && job.missingSkills.length > 0 && (
            <div>
              <div className="flex items-center gap-2 mb-2">
                <AlertCircle className="w-4 h-4 text-orange-600" />
                <span className="text-sm font-medium text-orange-700">
                  Skills to Develop ({job.missingSkills.length})
                </span>
              </div>
              <div className="flex flex-wrap gap-1">
                {job.missingSkills.map((skill, index) => (
                  <span 
                    key={index} 
                    className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded-full border border-orange-200"
                  >
                    {skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {salary_range && (
        <div className="mb-4">
          <span className="inline-block bg-green-50 text-green-700 text-sm px-2 py-1 rounded">
            {salary_range}
          </span>
        </div>
      )}

      {job_type && (
        <div className="mb-4">
          <span className="inline-block bg-purple-50 text-purple-700 text-sm px-2 py-1 rounded">
            {job_type}
          </span>
        </div>
      )}

      <div className="flex justify-between items-center gap-2">
        <button
          onClick={() => onViewDetails(job)}
          className="btn-secondary px-4 py-2 text-sm"
        >
          View Details
        </button>
        
        <div className="flex gap-2">
          {jobUrl && (
            <a
              href={jobUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="btn-primary px-4 py-2 text-sm inline-flex items-center hover:bg-blue-700 transition-colors"
              title="Visit original job posting"
            >
              <ExternalLink className="w-4 h-4 mr-1" />
              Visit Job
            </a>
          )}
          
          {jobUrl && (
            <button
              onClick={async () => {
                try {
                  setIsApplying(true);
                  
                  const response = await fetch(`http://localhost:8000/api/jobs/auto-apply/${id}`, {
                    method: 'POST',
                    headers: {
                      'Content-Type': 'application/json',
                    },
                  });
                  
                  const result = await response.json();
                  
                  if (response.ok && result.success) {
                    alert(`✅ Successfully applied to ${title} at ${company}!\n\nMethod: ${result.method}\nStatus: ${result.status}`);
                    // Optionally update job status in parent component
                    if (onStatusUpdate) {
                      onStatusUpdate(id, 'applied');
                    }
                  } else {
                    // Handle the specific case where auto-apply isn't available
                    if (result.reason === "Browser not available") {
                      alert(`🤖 Auto-Apply Currently Unavailable\n\n` +
                            `Unfortunately, automatic job application is temporarily limited due to technical constraints.\n\n` +
                            `You can still apply manually by clicking "Visit Job" to go directly to the job posting.\n\n` +
                            `Job: ${title} at ${company}`);
                    } else {
                      alert(`❌ Failed to apply to ${title}\n\nError: ${result.error || result.message || result.reason || 'Unknown error'}`);
                    }
                  }
                } catch (error) {
                  console.error('Auto-apply error:', error);
                  alert(`❌ Failed to apply to ${title}\n\nError: ${error.message}`);
                } finally {
                  setIsApplying(false);
                }
              }}
              disabled={isApplying}
              className={`${
                isApplying 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700'
              } text-white px-4 py-2 text-sm rounded-lg inline-flex items-center transition-colors`}
              title="Auto-apply using AI agent"
            >
              {isApplying ? (
                <>
                  <span className="animate-spin mr-1">⏳</span>
                  Applying...
                </>
              ) : (
                'Auto Apply'
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default JobCard;
