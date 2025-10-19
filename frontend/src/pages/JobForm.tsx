import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useForm } from 'react-hook-form';
import { ArrowLeft } from 'lucide-react';
import Layout from '../components/Layout';
import { jobsApi } from '../services/api';
import type { JobApplicationCreate, ApplicationStatus } from '../types';

export default function JobForm() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const isEditMode = !!id;
  
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [initialLoading, setInitialLoading] = useState(isEditMode);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<JobApplicationCreate>();

  useEffect(() => {
    if (isEditMode && id) {
      fetchJob(parseInt(id));
    }
  }, [id]);

  const fetchJob = async (jobId: number) => {
    try {
      const job = await jobsApi.getById(jobId);
      reset({
        company_name: job.company_name,
        job_title: job.job_title,
        job_url: job.job_url || '',
        location: job.location || '',
        salary_range: job.salary_range || '',
        status: job.status,
        applied_date: job.applied_date ? job.applied_date.split('T')[0] : '',
        interview_date: job.interview_date ? job.interview_date.split('T')[0] : '',
        follow_up_date: job.follow_up_date ? job.follow_up_date.split('T')[0] : '',
        job_description: job.job_description || '',
        notes: job.notes || '',
        contact_person: job.contact_person || '',
        contact_email: job.contact_email || '',
        contact_phone: job.contact_phone || '',
      });
    } catch (err: any) {
      setError('Failed to load job application');
      console.error(err);
    } finally {
      setInitialLoading(false);
    }
  };

  const onSubmit = async (data: JobApplicationCreate) => {
    setLoading(true);
    setError('');
    
    try {
      // Convert empty strings to undefined and format dates
      const cleanedData: any = {};
      Object.entries(data).forEach(([key, value]) => {
        if (value !== '') {
          // Convert date strings to ISO datetime format for date fields
          if ((key === 'applied_date' || key === 'interview_date' || key === 'follow_up_date') && value) {
            // Add time component to make it a valid datetime
            cleanedData[key] = `${value}T00:00:00Z`;
          } else {
            cleanedData[key] = value;
          }
        }
      });

      if (isEditMode && id) {
        await jobsApi.update(parseInt(id), cleanedData);
      } else {
        await jobsApi.create(cleanedData);
      }
      
      navigate('/jobs');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to save job application');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  if (initialLoading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading job application...</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-3xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/jobs')}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              {isEditMode ? 'Edit Job Application' : 'Add Job Application'}
            </h1>
            <p className="text-gray-600 mt-1">
              {isEditMode ? 'Update job application details' : 'Fill in the details below'}
            </p>
          </div>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit(onSubmit)} className="card space-y-6">
          {/* Company & Job Title */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Company Name <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Google"
                {...register('company_name', { required: 'Company name is required' })}
              />
              {errors.company_name && (
                <p className="mt-1 text-sm text-red-600">{errors.company_name.message}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Senior Software Engineer"
                {...register('job_title', { required: 'Job title is required' })}
              />
              {errors.job_title && (
                <p className="mt-1 text-sm text-red-600">{errors.job_title.message}</p>
              )}
            </div>
          </div>

          {/* Job URL & Location */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Job URL
              </label>
              <input
                type="url"
                className="input"
                placeholder="https://..."
                {...register('job_url')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g., Auckland, New Zealand"
                {...register('location')}
              />
            </div>
          </div>

          {/* Status & Salary Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Status
              </label>
              <select className="input" {...register('status')}>
                <option value="applied">Applied</option>
                <option value="interview">Interview</option>
                <option value="offer">Offer</option>
                <option value="rejected">Rejected</option>
                <option value="withdrawn">Withdrawn</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Salary Range
              </label>
              <input
                type="text"
                className="input"
                placeholder="e.g., $100k - $120k"
                {...register('salary_range')}
              />
            </div>
          </div>

          {/* Dates */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Applied Date
              </label>
              <input
                type="date"
                className="input"
                {...register('applied_date')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Interview Date
              </label>
              <input
                type="date"
                className="input"
                {...register('interview_date')}
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Follow-up Date
              </label>
              <input
                type="date"
                className="input"
                {...register('follow_up_date')}
              />
            </div>
          </div>

          {/* Job Description */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Job Description
            </label>
            <textarea
              className="input"
              rows={4}
              placeholder="Paste job description here..."
              {...register('job_description')}
            />
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Notes
            </label>
            <textarea
              className="input"
              rows={3}
              placeholder="Add any personal notes..."
              {...register('notes')}
            />
          </div>

          {/* Contact Information */}
          <div className="border-t pt-6">
            <h3 className="text-lg font-semibold mb-4">Contact Information</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Person
                </label>
                <input
                  type="text"
                  className="input"
                  placeholder="e.g., John Doe"
                  {...register('contact_person')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Email
                </label>
                <input
                  type="email"
                  className="input"
                  placeholder="contact@company.com"
                  {...register('contact_email')}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Contact Phone
                </label>
                <input
                  type="tel"
                  className="input"
                  placeholder="+64 123 456 789"
                  {...register('contact_phone')}
                />
              </div>
            </div>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}

          {/* Actions */}
          <div className="flex items-center justify-end gap-4 pt-6 border-t">
            <button
              type="button"
              onClick={() => navigate('/jobs')}
              className="btn btn-secondary"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn btn-primary"
            >
              {loading
                ? (isEditMode ? 'Updating...' : 'Creating...')
                : (isEditMode ? 'Update Job' : 'Create Job')}
            </button>
          </div>
        </form>
      </div>
    </Layout>
  );
}