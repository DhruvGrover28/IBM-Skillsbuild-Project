import React, { useState, useEffect } from 'react'
import { Calendar, MapPin, Building, Clock, CheckCircle, XCircle, Eye, Trash2 } from 'lucide-react'

const Applications = () => {
  const [applications, setApplications] = useState([])
  const [filter, setFilter] = useState('all')
  const [loading, setLoading] = useState(false)

  // Mock application data
  const mockApplications = [
    {
      id: 1,
      jobTitle: 'Frontend Developer',
      company: 'Tech Corp',
      location: 'San Francisco, CA',
      appliedDate: '2024-01-15',
      status: 'pending',
      statusColor: 'yellow',
      notes: 'Applied through company website',
      interviewDate: null,
      salary: '$80,000 - $120,000'
    },
    {
      id: 2,
      jobTitle: 'React Developer',
      company: 'StartupXYZ',
      location: 'Remote',
      appliedDate: '2024-01-10',
      status: 'interview',
      statusColor: 'blue',
      notes: 'Phone screening scheduled for next week',
      interviewDate: '2024-01-25',
      salary: '$70,000 - $100,000'
    },
    {
      id: 3,
      jobTitle: 'Senior Developer',
      company: 'BigTech Inc',
      location: 'New York, NY',
      appliedDate: '2024-01-05',
      status: 'rejected',
      statusColor: 'red',
      notes: 'Not a good fit for the team',
      interviewDate: null,
      salary: '$120,000 - $160,000'
    },
    {
      id: 4,
      jobTitle: 'Full Stack Developer',
      company: 'Innovation Labs',
      location: 'Austin, TX',
      appliedDate: '2024-01-20',
      status: 'accepted',
      statusColor: 'green',
      notes: 'Offer received! Start date: Feb 1st',
      interviewDate: '2024-01-18',
      salary: '$95,000 - $130,000'
    }
  ]

  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setApplications(mockApplications)
      setLoading(false)
    }, 500)
  }, [])

  const getStatusBadge = (status, color) => {
    const baseClasses = "inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium"
    const colorClasses = {
      yellow: "bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-300",
      blue: "bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300",
      red: "bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-300",
      green: "bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-300"
    }

    const statusIcons = {
      pending: <Clock className="w-3 h-3 mr-1" />,
      interview: <Eye className="w-3 h-3 mr-1" />,
      rejected: <XCircle className="w-3 h-3 mr-1" />,
      accepted: <CheckCircle className="w-3 h-3 mr-1" />
    }

    return (
      <span className={`${baseClasses} ${colorClasses[color]}`}>
        {statusIcons[status]}
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </span>
    )
  }

  const filteredApplications = applications.filter(app => {
    if (filter === 'all') return true
    return app.status === filter
  })

  const getStatusCounts = () => {
    return {
      all: applications.length,
      pending: applications.filter(app => app.status === 'pending').length,
      interview: applications.filter(app => app.status === 'interview').length,
      accepted: applications.filter(app => app.status === 'accepted').length,
      rejected: applications.filter(app => app.status === 'rejected').length
    }
  }

  const statusCounts = getStatusCounts()

  const deleteApplication = (id) => {
    setApplications(prev => prev.filter(app => app.id !== id))
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
            My Applications
          </h1>
          <p className="text-gray-600 dark:text-gray-300">
            Track and manage your job applications
          </p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6 mb-8">
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Total Applications</h3>
            <p className="text-2xl font-bold text-gray-900 dark:text-white">{statusCounts.all}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Pending</h3>
            <p className="text-2xl font-bold text-yellow-600">{statusCounts.pending}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Interviews</h3>
            <p className="text-2xl font-bold text-blue-600">{statusCounts.interview}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Accepted</h3>
            <p className="text-2xl font-bold text-green-600">{statusCounts.accepted}</p>
          </div>
          <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md">
            <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400">Rejected</h3>
            <p className="text-2xl font-bold text-red-600">{statusCounts.rejected}</p>
          </div>
        </div>

        {/* Filter Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md mb-6">
          <nav className="flex space-x-8 px-6 py-4" aria-label="Tabs">
            {[
              { key: 'all', label: 'All Applications', count: statusCounts.all },
              { key: 'pending', label: 'Pending', count: statusCounts.pending },
              { key: 'interview', label: 'Interview', count: statusCounts.interview },
              { key: 'accepted', label: 'Accepted', count: statusCounts.accepted },
              { key: 'rejected', label: 'Rejected', count: statusCounts.rejected }
            ].map((tab) => (
              <button
                key={tab.key}
                onClick={() => setFilter(tab.key)}
                className={`${
                  filter === tab.key
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-300'
                } whitespace-nowrap py-2 px-1 border-b-2 font-medium text-sm transition-colors`}
              >
                {tab.label}
                <span className="ml-2 bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-gray-300 py-0.5 px-2 rounded-full text-xs">
                  {tab.count}
                </span>
              </button>
            ))}
          </nav>
        </div>

        {/* Applications List */}
        <div className="space-y-6">
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredApplications.length === 0 ? (
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-12 text-center">
              <div className="text-gray-400 dark:text-gray-500 mb-4">
                <Building className="mx-auto h-12 w-12" />
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                No applications found
              </h3>
              <p className="text-gray-500 dark:text-gray-400">
                {filter === 'all' 
                  ? "You haven't applied to any jobs yet."
                  : `No applications with status "${filter}".`
                }
              </p>
            </div>
          ) : (
            filteredApplications.map((application) => (
              <div key={application.id} className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
                <div className="flex justify-between items-start mb-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                        {application.jobTitle}
                      </h3>
                      {getStatusBadge(application.status, application.statusColor)}
                    </div>
                    <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-2">
                      <div className="flex items-center gap-1">
                        <Building className="h-4 w-4" />
                        {application.company}
                      </div>
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4" />
                        {application.location}
                      </div>
                      <div className="flex items-center gap-1">
                        <Calendar className="h-4 w-4" />
                        Applied: {new Date(application.appliedDate).toLocaleDateString()}
                      </div>
                    </div>
                    <p className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                      {application.salary}
                    </p>
                    {application.notes && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Notes: {application.notes}
                      </p>
                    )}
                    {application.interviewDate && (
                      <p className="text-sm text-blue-600 dark:text-blue-400 mt-2">
                        Interview: {new Date(application.interviewDate).toLocaleDateString()}
                      </p>
                    )}
                  </div>
                  <button
                    onClick={() => deleteApplication(application.id)}
                    className="text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  )
}

export default Applications
