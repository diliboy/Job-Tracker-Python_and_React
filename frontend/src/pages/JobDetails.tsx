import { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { format } from 'date-fns';
import {
  ArrowLeft,
  Building2,
  MapPin,
  Calendar,
  DollarSign,
  ExternalLink,
  Edit,
  Trash2,
  FileText,
  Upload,
  Download,
  X,
} from 'lucide-react';
import Layout from '../components/Layout';
import { jobsApi, documentsApi } from '../services/api';
import type { JobApplication, Document, DocumentType } from '../types';

const statusColors = {
  applied: 'badge-applied',
  interview: 'badge-interview',
  offer: 'badge-offer',
  rejected: 'badge-rejected',
  withdrawn: 'badge-withdrawn',
};

export default function JobDetails() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  
  const [job, setJob] = useState<JobApplication | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [uploadingFile, setUploadingFile] = useState(false);
  const [showUploadForm, setShowUploadForm] = useState(false);

  useEffect(() => {
    if (id) {
      fetchJobDetails(parseInt(id));
      fetchDocuments(parseInt(id));
    }
  }, [id]);

  const fetchJobDetails = async (jobId: number) => {
    try {
      setLoading(true);
      const data = await jobsApi.getById(jobId);
      setJob(data);
    } catch (err: any) {
      setError('Failed to load job details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async (jobId: number) => {
    try {
      const docs = await documentsApi.getByJobId(jobId);
      setDocuments(docs);
    } catch (err: any) {
      console.error('Failed to load documents:', err);
    }
  };

  const handleDelete = async () => {
    if (!job || !window.confirm(`Delete application for ${job.company_name}?`)) {
      return;
    }

    try {
      await jobsApi.delete(job.id);
      navigate('/jobs');
    } catch (err: any) {
      alert('Failed to delete job application');
      console.error(err);
    }
  };

  const handleFileUpload = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    if (!id) return;

    const formData = new FormData(e.currentTarget);
    const file = formData.get('file') as File;
    const documentType = formData.get('document_type') as DocumentType;

    if (!file) {
      alert('Please select a file');
      return;
    }

    try {
      setUploadingFile(true);
      await documentsApi.upload(parseInt(id), file, documentType);
      setShowUploadForm(false);
      fetchDocuments(parseInt(id));
      alert('File uploaded successfully!');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Failed to upload file');
      console.error(err);
    } finally {
      setUploadingFile(false);
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const blob = await documentsApi.download(doc.id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = doc.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (err: any) {
      alert('Failed to download file');
      console.error(err);
    }
  };

  const handleDeleteDocument = async (docId: number) => {
    if (!window.confirm('Delete this document?')) return;

    try {
      await documentsApi.delete(docId);
      fetchDocuments(parseInt(id!));
      alert('Document deleted successfully');
    } catch (err: any) {
      alert('Failed to delete document');
      console.error(err);
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading job details...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !job) {
    return (
      <Layout>
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">{error || 'Job not found'}</p>
          <button onClick={() => navigate('/jobs')} className="btn btn-primary mt-4">
            Back to Jobs
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-4xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-4">
            <button
              onClick={() => navigate('/jobs')}
              className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <ArrowLeft className="w-5 h-5" />
            </button>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{job.company_name}</h1>
              <p className="text-gray-600">{job.job_title}</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <button
              onClick={() => navigate(`/jobs/${job.id}/edit`)}
              className="btn btn-secondary flex items-center gap-2"
            >
              <Edit className="w-4 h-4" />
              Edit
            </button>
            <button
              onClick={handleDelete}
              className="btn btn-danger flex items-center gap-2"
            >
              <Trash2 className="w-4 h-4" />
              Delete
            </button>
          </div>
        </div>

        {/* Main Info Card */}
        <div className="card">
          <div className="flex items-start justify-between mb-6">
            <span className={`badge ${statusColors[job.status]} text-lg`}>
              {job.status}
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {job.location && (
              <div className="flex items-start gap-3">
                <MapPin className="w-5 h-5 text-gray-500 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Location</p>
                  <p className="font-medium">{job.location}</p>
                </div>
              </div>
            )}

            {job.salary_range && (
              <div className="flex items-start gap-3">
                <DollarSign className="w-5 h-5 text-gray-500 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Salary Range</p>
                  <p className="font-medium">{job.salary_range}</p>
                </div>
              </div>
            )}

            {job.applied_date && (
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-500 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Applied Date</p>
                  <p className="font-medium">
                    {format(new Date(job.applied_date), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>
            )}

            {job.interview_date && (
              <div className="flex items-start gap-3">
                <Calendar className="w-5 h-5 text-gray-500 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Interview Date</p>
                  <p className="font-medium">
                    {format(new Date(job.interview_date), 'MMM d, yyyy')}
                  </p>
                </div>
              </div>
            )}

            {job.job_url && (
              <div className="flex items-start gap-3">
                <ExternalLink className="w-5 h-5 text-gray-500 mt-1" />
                <div>
                  <p className="text-sm text-gray-600">Job Posting</p>
                  <a
                    href={job.job_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="font-medium text-primary-600 hover:text-primary-700 flex items-center gap-1"
                  >
                    View Posting <ExternalLink className="w-3 h-3" />
                  </a>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Job Description */}
        {job.job_description && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Job Description</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{job.job_description}</p>
          </div>
        )}

        {/* Notes */}
        {job.notes && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Notes</h2>
            <p className="text-gray-700 whitespace-pre-wrap">{job.notes}</p>
          </div>
        )}

        {/* Contact Information */}
        {(job.contact_person || job.contact_email || job.contact_phone) && (
          <div className="card">
            <h2 className="text-xl font-semibold mb-4">Contact Information</h2>
            <div className="space-y-2">
              {job.contact_person && (
                <p>
                  <span className="text-gray-600">Name:</span>{' '}
                  <span className="font-medium">{job.contact_person}</span>
                </p>
              )}
              {job.contact_email && (
                <p>
                  <span className="text-gray-600">Email:</span>{' '}
                  <a
                    href={`mailto:${job.contact_email}`}
                    className="font-medium text-primary-600 hover:text-primary-700"
                  >
                    {job.contact_email}
                  </a>
                </p>
              )}
              {job.contact_phone && (
                <p>
                  <span className="text-gray-600">Phone:</span>{' '}
                  <span className="font-medium">{job.contact_phone}</span>
                </p>
              )}
            </div>
          </div>
        )}

        {/* Documents */}
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold">Documents</h2>
            <button
              onClick={() => setShowUploadForm(!showUploadForm)}
              className="btn btn-primary flex items-center gap-2"
            >
              <Upload className="w-4 h-4" />
              Upload Document
            </button>
          </div>

          {/* Upload Form */}
          {showUploadForm && (
            <form onSubmit={handleFileUpload} className="mb-6 p-4 bg-gray-50 rounded-lg">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Document Type
                  </label>
                  <select name="document_type" className="input" required>
                    <option value="resume">Resume</option>
                    <option value="cover_letter">Cover Letter</option>
                    <option value="other">Other</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    File (PDF, DOC, DOCX, TXT)
                  </label>
                  <input
                    type="file"
                    name="file"
                    accept=".pdf,.doc,.docx,.txt"
                    className="input"
                    required
                  />
                </div>
              </div>
              <div className="flex items-center gap-2 mt-4">
                <button type="submit" disabled={uploadingFile} className="btn btn-primary">
                  {uploadingFile ? 'Uploading...' : 'Upload'}
                </button>
                <button
                  type="button"
                  onClick={() => setShowUploadForm(false)}
                  className="btn btn-secondary"
                >
                  Cancel
                </button>
              </div>
            </form>
          )}

          {/* Documents List */}
          {documents.length === 0 ? (
            <p className="text-gray-500 text-center py-8">
              No documents uploaded yet
            </p>
          ) : (
            <div className="space-y-2">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 border border-gray-200 rounded-lg hover:bg-gray-50"
                >
                  <div className="flex items-center gap-3">
                    <FileText className="w-5 h-5 text-gray-500" />
                    <div>
                      <p className="font-medium">{doc.filename}</p>
                      <p className="text-sm text-gray-500">
                        {doc.document_type} • {(doc.file_size / 1024).toFixed(2)} KB •{' '}
                        {format(new Date(doc.created_at), 'MMM d, yyyy')}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => handleDownload(doc)}
                      className="p-2 text-primary-600 hover:bg-primary-50 rounded-lg"
                      title="Download"
                    >
                      <Download className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDeleteDocument(doc.id)}
                      className="p-2 text-red-600 hover:bg-red-50 rounded-lg"
                      title="Delete"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
}