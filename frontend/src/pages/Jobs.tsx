import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { format } from 'date-fns';
import { Building2, MapPin, Calendar, Edit, Trash2, Eye, Search, Filter } from 'lucide-react';
import Layout from '../components/Layout';
import { jobsApi } from '../services/api';
import type { JobApplication, ApplicationStatus, JobApplicationListResponse } from '../types';

const statusOptions: { value: ApplicationStatus | ''; label: string }[] = [
  { value: '', label: 'All Statuses' },
  { value: 'applied', label: 'Applied' },
  { value: 'interview', label: 'Interview' },
  { value: 'offer', label: 'Offer' },
  { value: 'rejected', label: 'Rejected' },
  { value: 'withdrawn', label: 'Withdrawn' },
];

const statusColors = {
  applied: 'badge-applied',
  interview: 'badge-interview',
  offer: 'badge-offer',
  rejected: 'badge-rejected',
  withdrawn: 'badge-withdrawn',
};

export default function Jobs() {
  const navigate = useNavigate();
  const [data, setData] = useState<JobApplicationListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  
  // Filters
  const [searchCompany, setSearchCompany] = useState('');
  const [filterStatus, setFilterStatus] = useState<ApplicationStatus | ''>('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;

  useEffect(() => {
    fetchJobs();
  }, [currentPage, filterStatus]);

  const fetchJobs = async () => {
    try {
      setLoading(true);
      const params: any = {
        page: currentPage,
        size: pageSize,
      };
      
      if (filterStatus) params.status = filterStatus;
      if (searchCompany) params.company = searchCompany;

      const response = await jobsApi.getAll(params);
      setData(response);
    } catch (err: any) {
      setError('Failed to load jobs');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = () => {
    setCurrentPage(1);
    fetchJobs();
  };

  const handleDelete = async (id: number, companyName: string) => {
    if (!window.confirm(`Are you sure you want to delete the application for ${companyName}?`)) {
      return;
    }

    try {
      await jobsApi.delete(id);
      fetchJobs(); // Refresh list
    } catch (err: any) {
      alert('Failed to delete job application');
      console.error(err);
    }
  };

  if (loading && !data) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading jobs...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Job Applications</h1>
            <p className="text-gray-600 mt-1">
              {data?.total || 0} total applications
            </p>
          </div>
        </div>

        {/* Filters */}
        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Search by Company
              </label>
              <div className="flex gap-2">
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., Google, Microsoft..."
                  value={searchCompany}
                  onChange={(e) => setSearchCompany(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                />
                <button onClick={handleSearch} className="btn btn-primary">
                  <Search className="w-4 h-4" />
                </button>
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Filter by Status
              </label>
              <select
                className="input"
                value={filterStatus}
                onChange={(e) => {
                  setFilterStatus(e.target.value as ApplicationStatus | '');
                  setCurrentPage(1);
                }}
              >
                {statusOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Error */}
        {error && (
          <div className="card bg-red-50 border-red-200">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {/* Jobs List */}
        {data && data.items.length === 0 ? (
          <div className="card text-center py-12">
            <Building2 className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">
              No job applications found
            </h3>
            <p className="text-gray-600 mb-6">
              {searchCompany || filterStatus
                ? 'Try adjusting your filters'
                : 'Start by adding your first job application'}
            </p>
            <button
              onClick={() => navigate('/jobs/new')}
              className="btn btn-primary"
            >
              Add Job Application
            </button>
          </div>
        ) : (
          <div className="space-y-3">
            {data?.items.map((job) => (
              <div
                key={job.id}
                className="card hover:shadow-lg transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-2">
                      <Building2 className="w-5 h-5 text-gray-500" />
                      <h3 className="text-xl font-semibold text-gray-900">
                        {job.company_name}
                      </h3>
                      <span className={`badge ${statusColors[job.status]}`}>
                        {job.status}
                      </span>
                    </div>
                    
                    <p className="text-gray-700 font-medium mb-3">
                      {job.job_title}
                    </p>
                    
                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                      {job.location && (
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {job.location}
                        </span>
                      )}
                      {job.salary_range && (
                        <span>💰 {job.salary_range}</span>
                      )}
                      {job.applied_date && (
                        <span className="flex items-center gap-1">
                          <Calendar className="w-4 h-4" />
                          Applied {format(new Date(job.applied_date), 'MMM d, yyyy')}
                        </span>
                      )}
                    </div>
                    
                    {job.notes && (
                      <p className="mt-3 text-sm text-gray-600 line-clamp-2">
                        {job.notes}
                      </p>
                    )}
                  </div>
                  
                  <div className="flex items-center gap-2 ml-4">
                    <button
                      onClick={() => navigate(`/jobs/${job.id}`)}
                      className="p-2 text-gray-600 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors"
                      title="View Details"
                    >
                      <Eye className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => navigate(`/jobs/${job.id}/edit`)}
                      className="p-2 text-gray-600 hover:text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                      title="Edit"
                    >
                      <Edit className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(job.id, job.company_name)}
                      className="p-2 text-gray-600 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete"
                    >
                      <Trash2 className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Pagination */}
        {data && data.pages > 1 && (
          <div className="flex items-center justify-center gap-2">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="btn btn-secondary disabled:opacity-50"
            >
              Previous
            </button>
            
            <div className="flex items-center gap-2">
              {Array.from({ length: data.pages }, (_, i) => i + 1).map((page) => (
                <button
                  key={page}
                  onClick={() => setCurrentPage(page)}
                  className={`w-10 h-10 rounded-lg font-medium transition-colors ${
                    page === currentPage
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  {page}
                </button>
              ))}
            </div>
            
            <button
              onClick={() => setCurrentPage((p) => Math.min(data.pages, p + 1))}
              disabled={currentPage === data.pages}
              className="btn btn-secondary disabled:opacity-50"
            >
              Next
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}