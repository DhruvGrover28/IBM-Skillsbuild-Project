import React from 'react';
import { 
  Calendar, 
  Building, 
  MapPin, 
  ExternalLink,
  Clock,
  CheckCircle,
  XCircle,
  AlertCircle
} from 'lucide-react';

const TrackerTable = ({ applications = [] }) => {
  const getStatusIcon = (status) => {
    switch (status?.toLowerCase()) {
      case 'applied':
        return <Clock className="w-4 h-4 text-blue-500" />;
      case 'interview':
        return <AlertCircle className="w-4 h-4 text-yellow-500" />;
      case 'offered':
        return <CheckCircle className="w-4 h-4 text-green-500" />;
      case 'rejected':
        return <XCircle className="w-4 h-4 text-red-500" />;
      default:
        return <Clock className="w-4 h-4 text-gray-500" />;
    }
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

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric'
    });
  };

  if (applications.length === 0) {
    return (
      <div className="card p-8 text-center">
        <div className="text-gray-400 mb-4">
          <Building className="w-12 h-12 mx-auto" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">No Applications Yet</h3>
        <p className="text-gray-500">
          Start applying to jobs to track your progress here.
        </p>
      </div>
    );
  }

  return (
    <div className="card overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900">Application Tracker</h2>
        <p className="text-sm text-gray-600">Track the status of your job applications</p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Job Details
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Company
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Applied Date
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {applications.map((app, index) => (
              <tr key={app.id || index} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="text-sm font-medium text-gray-900">
                      {app.job_title || app.title}
                    </div>
                    <div className="text-sm text-gray-500 flex items-center mt-1">
                      <MapPin className="w-3 h-3 mr-1" />
                      {app.job_location || app.location || 'Remote'}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    <Building className="w-4 h-4 text-gray-400 mr-2" />
                    <div className="text-sm text-gray-900">
                      {app.company_name || app.company}
                    </div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center text-sm text-gray-500">
                    <Calendar className="w-4 h-4 mr-1" />
                    {formatDate(app.applied_date || app.application_date)}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center">
                    {getStatusIcon(app.status)}
                    <span className={`ml-2 inline-flex px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(app.status)}`}>
                      {app.status || 'pending'}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="flex items-center space-x-2">
                    {app.application_url && (
                      <a
                        href={app.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-900 transition-colors"
                        title="View Application"
                      >
                        <ExternalLink className="w-4 h-4" />
                      </a>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {applications.length > 0 && (
        <div className="px-6 py-3 bg-gray-50 border-t border-gray-200">
          <div className="text-sm text-gray-700">
            Showing {applications.length} application{applications.length !== 1 ? 's' : ''}
          </div>
        </div>
      )}
    </div>
  );
};

export default TrackerTable;
