import React, { useState } from 'react'
import { User, Mail, Phone, MapPin, Calendar, Briefcase, GraduationCap, Edit, Save, X, Plus } from 'lucide-react'

const Profile = () => {
  const [isEditing, setIsEditing] = useState(false)
  const [profile, setProfile] = useState({
    firstName: 'John',
    lastName: 'Doe',
    email: 'john.doe@email.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    title: 'Frontend Developer',
    bio: 'Passionate frontend developer with 5+ years of experience in React, JavaScript, and modern web technologies. Love creating beautiful and functional user experiences.',
    experience: [
      {
        id: 1,
        title: 'Senior Frontend Developer',
        company: 'Tech Corp',
        location: 'San Francisco, CA',
        startDate: '2022-01',
        endDate: 'Present',
        description: 'Lead frontend development for multiple React applications, mentoring junior developers, and implementing modern UI/UX designs.'
      },
      {
        id: 2,
        title: 'Frontend Developer',
        company: 'StartupXYZ',
        location: 'Remote',
        startDate: '2020-03',
        endDate: '2021-12',
        description: 'Developed responsive web applications using React, Redux, and TypeScript. Collaborated with design team to implement pixel-perfect UIs.'
      }
    ],
    education: [
      {
        id: 1,
        degree: 'Bachelor of Science in Computer Science',
        school: 'University of California, Berkeley',
        location: 'Berkeley, CA',
        startDate: '2016-09',
        endDate: '2020-05',
        gpa: '3.8'
      }
    ],
    skills: ['React', 'JavaScript', 'TypeScript', 'HTML/CSS', 'Node.js', 'Python', 'Git', 'Figma']
  })

  const [tempProfile, setTempProfile] = useState(profile)

  const handleEdit = () => {
    setTempProfile(profile)
    setIsEditing(true)
  }

  const handleSave = () => {
    setProfile(tempProfile)
    setIsEditing(false)
  }

  const handleCancel = () => {
    setTempProfile(profile)
    setIsEditing(false)
  }

  const handleInputChange = (field, value) => {
    setTempProfile(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const addSkill = () => {
    const skill = prompt('Enter new skill:')
    if (skill && !tempProfile.skills.includes(skill)) {
      setTempProfile(prev => ({
        ...prev,
        skills: [...prev.skills, skill]
      }))
    }
  }

  const removeSkill = (skillToRemove) => {
    setTempProfile(prev => ({
      ...prev,
      skills: prev.skills.filter(skill => skill !== skillToRemove)
    }))
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              My Profile
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              Manage your professional information
            </p>
          </div>
          <div className="flex gap-2">
            {isEditing ? (
              <>
                <button
                  onClick={handleSave}
                  className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 transition-colors"
                >
                  <Save className="h-4 w-4" />
                  Save
                </button>
                <button
                  onClick={handleCancel}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-500 text-white rounded-md hover:bg-gray-600 transition-colors"
                >
                  <X className="h-4 w-4" />
                  Cancel
                </button>
              </>
            ) : (
              <button
                onClick={handleEdit}
                className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
              >
                <Edit className="h-4 w-4" />
                Edit Profile
              </button>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column - Basic Info */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 mb-6">
              {/* Profile Picture */}
              <div className="text-center mb-6">
                <div className="w-24 h-24 bg-gray-300 dark:bg-gray-600 rounded-full mx-auto mb-4 flex items-center justify-center">
                  <User className="h-12 w-12 text-gray-500 dark:text-gray-400" />
                </div>
                <h2 className="text-xl font-bold text-gray-900 dark:text-white">
                  {isEditing ? (
                    <div className="space-y-2">
                      <input
                        type="text"
                        value={tempProfile.firstName}
                        onChange={(e) => handleInputChange('firstName', e.target.value)}
                        className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-center dark:bg-gray-700 dark:text-white"
                        placeholder="First Name"
                      />
                      <input
                        type="text"
                        value={tempProfile.lastName}
                        onChange={(e) => handleInputChange('lastName', e.target.value)}
                        className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-center dark:bg-gray-700 dark:text-white"
                        placeholder="Last Name"
                      />
                    </div>
                  ) : (
                    `${profile.firstName} ${profile.lastName}`
                  )}
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  {isEditing ? (
                    <input
                      type="text"
                      value={tempProfile.title}
                      onChange={(e) => handleInputChange('title', e.target.value)}
                      className="w-full px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md text-center dark:bg-gray-700 dark:text-white"
                      placeholder="Job Title"
                    />
                  ) : (
                    profile.title
                  )}
                </p>
              </div>

              {/* Contact Info */}
              <div className="space-y-3">
                <div className="flex items-center gap-3">
                  <Mail className="h-4 w-4 text-gray-500" />
                  {isEditing ? (
                    <input
                      type="email"
                      value={tempProfile.email}
                      onChange={(e) => handleInputChange('email', e.target.value)}
                      className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <span className="text-gray-700 dark:text-gray-300">{profile.email}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <Phone className="h-4 w-4 text-gray-500" />
                  {isEditing ? (
                    <input
                      type="tel"
                      value={tempProfile.phone}
                      onChange={(e) => handleInputChange('phone', e.target.value)}
                      className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <span className="text-gray-700 dark:text-gray-300">{profile.phone}</span>
                  )}
                </div>
                <div className="flex items-center gap-3">
                  <MapPin className="h-4 w-4 text-gray-500" />
                  {isEditing ? (
                    <input
                      type="text"
                      value={tempProfile.location}
                      onChange={(e) => handleInputChange('location', e.target.value)}
                      className="flex-1 px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
                    />
                  ) : (
                    <span className="text-gray-700 dark:text-gray-300">{profile.location}</span>
                  )}
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Skills</h3>
                {isEditing && (
                  <button
                    onClick={addSkill}
                    className="text-blue-600 hover:text-blue-700 dark:text-blue-400"
                  >
                    <Plus className="h-4 w-4" />
                  </button>
                )}
              </div>
              <div className="flex flex-wrap gap-2">
                {(isEditing ? tempProfile.skills : profile.skills).map((skill, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-300"
                  >
                    {skill}
                    {isEditing && (
                      <button
                        onClick={() => removeSkill(skill)}
                        className="ml-2 text-blue-600 hover:text-blue-800 dark:text-blue-400"
                      >
                        <X className="h-3 w-3" />
                      </button>
                    )}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Detailed Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* About */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">About</h3>
              {isEditing ? (
                <textarea
                  value={tempProfile.bio}
                  onChange={(e) => handleInputChange('bio', e.target.value)}
                  rows={4}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md dark:bg-gray-700 dark:text-white"
                  placeholder="Tell us about yourself..."
                />
              ) : (
                <p className="text-gray-600 dark:text-gray-300">{profile.bio}</p>
              )}
            </div>

            {/* Experience */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Briefcase className="h-5 w-5" />
                Experience
              </h3>
              <div className="space-y-6">
                {profile.experience.map((exp) => (
                  <div key={exp.id} className="border-l-2 border-blue-200 dark:border-blue-800 pl-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{exp.title}</h4>
                    <p className="text-blue-600 dark:text-blue-400 font-medium">{exp.company}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">
                      {exp.location} • {exp.startDate} - {exp.endDate}
                    </p>
                    <p className="text-gray-600 dark:text-gray-300">{exp.description}</p>
                  </div>
                ))}
              </div>
            </div>

            {/* Education */}
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <GraduationCap className="h-5 w-5" />
                Education
              </h3>
              <div className="space-y-4">
                {profile.education.map((edu) => (
                  <div key={edu.id} className="border-l-2 border-green-200 dark:border-green-800 pl-4">
                    <h4 className="font-semibold text-gray-900 dark:text-white">{edu.degree}</h4>
                    <p className="text-green-600 dark:text-green-400 font-medium">{edu.school}</p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                      {edu.location} • {edu.startDate} - {edu.endDate}
                      {edu.gpa && ` • GPA: ${edu.gpa}`}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Profile
