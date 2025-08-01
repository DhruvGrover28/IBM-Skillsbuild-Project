import React, { useState, useEffect } from 'react';
import { 
  User, 
  Mail, 
  Phone, 
  MapPin, 
  FileText, 
  Briefcase,
  Save,
  Upload,
  Bell,
  Shield,
  Eye,
  EyeOff
} from 'lucide-react';
import axios from 'axios';

const Settings = () => {
  const [activeTab, setActiveTab] = useState('profile');
  const [profile, setProfile] = useState({
    name: '',
    email: '',
    phone: '',
    location: '',
    bio: '',
    skills: '',
    experience: '',
    education: '',
    resume_url: ''
  });
  const [preferences, setPreferences] = useState({
    job_types: [],
    preferred_locations: [],
    salary_min: '',
    salary_max: '',
    remote_work: false,
    email_notifications: true,
    push_notifications: false,
    auto_apply: false,
    auto_apply_threshold: 80
  });
  const [apiSettings, setApiSettings] = useState({
    openai_api_key: '',
    show_api_key: false
  });
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const [profileRes, preferencesRes, apiRes] = await Promise.all([
        axios.get('/api/profile').catch(() => ({ data: profile })),
        axios.get('/api/preferences').catch(() => ({ data: preferences })),
        axios.get('/api/settings').catch(() => ({ data: apiSettings }))
      ]);
      
      setProfile(profileRes.data);
      setPreferences(preferencesRes.data);
      setApiSettings(apiRes.data);
    } catch (error) {
      console.error('Error fetching settings:', error);
    }
  };

  const handleSave = async (section) => {
    setSaving(true);
    setMessage('');
    
    try {
      let endpoint = '';
      let data = {};
      
      switch (section) {
        case 'profile':
          endpoint = '/api/profile';
          data = profile;
          break;
        case 'preferences':
          endpoint = '/api/preferences';
          data = preferences;
          break;
        case 'api':
          endpoint = '/api/settings';
          data = apiSettings;
          break;
      }
      
      await axios.put(endpoint, data);
      setMessage('Settings saved successfully!');
      setTimeout(() => setMessage(''), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
      setMessage('Error saving settings. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('resume', file);

    try {
      const response = await axios.post('/api/upload/resume', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      setProfile({ ...profile, resume_url: response.data.url });
      setMessage('Resume uploaded successfully!');
    } catch (error) {
      console.error('Error uploading resume:', error);
      setMessage('Error uploading resume. Please try again.');
    }
  };

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'preferences', name: 'Job Preferences', icon: Briefcase },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'api', name: 'API Settings', icon: Shield }
  ];

  const TabButton = ({ tab, isActive, onClick }) => {
    const Icon = tab.icon;
    return (
      <button
        onClick={onClick}
        className={`flex items-center px-4 py-2 text-sm font-medium rounded-md transition-colors ${
          isActive
            ? 'bg-primary-100 text-primary-700'
            : 'text-gray-500 hover:text-gray-700 hover:bg-gray-100'
        }`}
      >
        <Icon className="w-4 h-4 mr-2" />
        {tab.name}
      </button>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="text-gray-600 mt-1">Manage your account and application preferences</p>
        </div>

        {message && (
          <div className={`mb-6 p-4 rounded-md ${
            message.includes('Error') 
              ? 'bg-red-50 text-red-700 border border-red-200' 
              : 'bg-green-50 text-green-700 border border-green-200'
          }`}>
            {message}
          </div>
        )}

        <div className="flex flex-col lg:flex-row gap-8">
          {/* Sidebar */}
          <div className="lg:w-64 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map((tab) => (
                <TabButton
                  key={tab.id}
                  tab={tab}
                  isActive={activeTab === tab.id}
                  onClick={() => setActiveTab(tab.id)}
                />
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="card p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Profile Information</h2>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Full Name
                    </label>
                    <div className="relative">
                      <User className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={profile.name}
                        onChange={(e) => setProfile({ ...profile, name: e.target.value })}
                        className="input pl-10"
                        placeholder="Your full name"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <Mail className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                      <input
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                        className="input pl-10"
                        placeholder="your.email@example.com"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <div className="relative">
                      <Phone className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                      <input
                        type="tel"
                        value={profile.phone}
                        onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                        className="input pl-10"
                        placeholder="+1 (555) 123-4567"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Location
                    </label>
                    <div className="relative">
                      <MapPin className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                      <input
                        type="text"
                        value={profile.location}
                        onChange={(e) => setProfile({ ...profile, location: e.target.value })}
                        className="input pl-10"
                        placeholder="City, State, Country"
                      />
                    </div>
                  </div>
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Professional Bio
                  </label>
                  <textarea
                    rows={4}
                    value={profile.bio}
                    onChange={(e) => setProfile({ ...profile, bio: e.target.value })}
                    className="input"
                    placeholder="Tell us about your professional background and career goals..."
                  />
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Skills (comma-separated)
                  </label>
                  <input
                    type="text"
                    value={profile.skills}
                    onChange={(e) => setProfile({ ...profile, skills: e.target.value })}
                    className="input"
                    placeholder="JavaScript, React, Node.js, Python, AWS"
                  />
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Resume
                  </label>
                  <div className="flex items-center space-x-4">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileUpload}
                      className="hidden"
                      id="resume-upload"
                    />
                    <label
                      htmlFor="resume-upload"
                      className="btn-secondary px-4 py-2 inline-flex items-center cursor-pointer"
                    >
                      <Upload className="w-4 h-4 mr-2" />
                      Upload Resume
                    </label>
                    {profile.resume_url && (
                      <a
                        href={profile.resume_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-primary-600 hover:text-primary-700 inline-flex items-center"
                      >
                        <FileText className="w-4 h-4 mr-1" />
                        View Current Resume
                      </a>
                    )}
                  </div>
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => handleSave('profile')}
                    disabled={saving}
                    className="btn-primary px-6 py-2 inline-flex items-center"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Profile'}
                  </button>
                </div>
              </div>
            )}

            {/* Job Preferences Tab */}
            {activeTab === 'preferences' && (
              <div className="card p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Job Preferences</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Preferred Job Types
                    </label>
                    <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                      {['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship', 'Remote'].map((type) => (
                        <label key={type} className="flex items-center">
                          <input
                            type="checkbox"
                            checked={preferences.job_types.includes(type)}
                            onChange={(e) => {
                              if (e.target.checked) {
                                setPreferences({
                                  ...preferences,
                                  job_types: [...preferences.job_types, type]
                                });
                              } else {
                                setPreferences({
                                  ...preferences,
                                  job_types: preferences.job_types.filter(t => t !== type)
                                });
                              }
                            }}
                            className="mr-2"
                          />
                          <span className="text-sm text-gray-700">{type}</span>
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Minimum Salary ($)
                      </label>
                      <input
                        type="number"
                        value={preferences.salary_min}
                        onChange={(e) => setPreferences({ ...preferences, salary_min: e.target.value })}
                        className="input"
                        placeholder="50000"
                      />
                    </div>

                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Maximum Salary ($)
                      </label>
                      <input
                        type="number"
                        value={preferences.salary_max}
                        onChange={(e) => setPreferences({ ...preferences, salary_max: e.target.value })}
                        className="input"
                        placeholder="150000"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Preferred Locations (comma-separated)
                    </label>
                    <input
                      type="text"
                      value={preferences.preferred_locations.join(', ')}
                      onChange={(e) => setPreferences({
                        ...preferences,
                        preferred_locations: e.target.value.split(',').map(l => l.trim()).filter(Boolean)
                      })}
                      className="input"
                      placeholder="New York, San Francisco, Remote, London"
                    />
                  </div>

                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.remote_work}
                        onChange={(e) => setPreferences({ ...preferences, remote_work: e.target.checked })}
                        className="mr-3"
                      />
                      <span className="text-sm font-medium text-gray-700">Open to remote work</span>
                    </label>

                    <label className="flex items-center">
                      <input
                        type="checkbox"
                        checked={preferences.auto_apply}
                        onChange={(e) => setPreferences({ ...preferences, auto_apply: e.target.checked })}
                        className="mr-3"
                      />
                      <span className="text-sm font-medium text-gray-700">Enable auto-apply for high-match jobs</span>
                    </label>

                    {/* Auto-apply status warning */}
                    <div className="ml-6 mt-2 p-3 bg-yellow-50 rounded-lg border border-yellow-200">
                      <div className="flex items-center">
                        <div className="flex-shrink-0">
                          <svg className="h-5 w-5 text-yellow-400" viewBox="0 0 20 20" fill="currentColor">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                        </div>
                        <div className="ml-3">
                          <p className="text-sm text-yellow-800">
                            <strong>Note:</strong> Auto-apply functionality is currently limited due to technical constraints. 
                            The system will attempt to apply but may not succeed on all job platforms.
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Auto-apply threshold setting */}
                    {preferences.auto_apply && (
                      <div className="ml-6 mt-3 p-4 bg-blue-50 rounded-lg border border-blue-200">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Auto-apply threshold (minimum match score)
                        </label>
                        <div className="flex items-center space-x-3">
                          <input
                            type="range"
                            min="50"
                            max="95"
                            step="5"
                            value={preferences.auto_apply_threshold}
                            onChange={(e) => setPreferences({ ...preferences, auto_apply_threshold: parseInt(e.target.value) })}
                            className="flex-1"
                          />
                          <span className="text-sm font-semibold text-blue-600 min-w-[40px]">
                            {preferences.auto_apply_threshold}%
                          </span>
                        </div>
                        <p className="text-xs text-gray-500 mt-1">
                          Jobs with a match score of {preferences.auto_apply_threshold}% or higher will be automatically applied to
                        </p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => handleSave('preferences')}
                    disabled={saving}
                    className="btn-primary px-6 py-2 inline-flex items-center"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="card p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">Notification Settings</h2>
                
                <div className="space-y-4">
                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Email notifications</span>
                      <p className="text-sm text-gray-500">Receive email updates about new job matches and application status</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.email_notifications}
                      onChange={(e) => setPreferences({ ...preferences, email_notifications: e.target.checked })}
                      className="ml-4"
                    />
                  </label>

                  <label className="flex items-center justify-between">
                    <div>
                      <span className="text-sm font-medium text-gray-700">Push notifications</span>
                      <p className="text-sm text-gray-500">Get instant alerts for urgent updates</p>
                    </div>
                    <input
                      type="checkbox"
                      checked={preferences.push_notifications}
                      onChange={(e) => setPreferences({ ...preferences, push_notifications: e.target.checked })}
                      className="ml-4"
                    />
                  </label>
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => handleSave('preferences')}
                    disabled={saving}
                    className="btn-primary px-6 py-2 inline-flex items-center"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save Settings'}
                  </button>
                </div>
              </div>
            )}

            {/* API Settings Tab */}
            {activeTab === 'api' && (
              <div className="card p-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-6">API Settings</h2>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      OpenAI API Key
                    </label>
                    <div className="relative">
                      <input
                        type={apiSettings.show_api_key ? 'text' : 'password'}
                        value={apiSettings.openai_api_key}
                        onChange={(e) => setApiSettings({ ...apiSettings, openai_api_key: e.target.value })}
                        className="input pr-10"
                        placeholder="sk-..."
                      />
                      <button
                        type="button"
                        onClick={() => setApiSettings({ ...apiSettings, show_api_key: !apiSettings.show_api_key })}
                        className="absolute right-3 top-3 text-gray-400 hover:text-gray-600"
                      >
                        {apiSettings.show_api_key ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                    <p className="text-sm text-gray-500 mt-1">
                      Required for AI-powered job matching and application assistance
                    </p>
                  </div>
                </div>

                <div className="mt-8 flex justify-end">
                  <button
                    onClick={() => handleSave('api')}
                    disabled={saving}
                    className="btn-primary px-6 py-2 inline-flex items-center"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {saving ? 'Saving...' : 'Save API Settings'}
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;
