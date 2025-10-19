import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Briefcase, Clock, CheckCircle, XCircle, MinusCircle } from 'lucide-react';
import Layout from '../components/Layout';
import StatsCard from '../components/StatsCard';
import RecentJobs from '../components/RecentJobs';
import { jobsApi } from '../services/api';
import type { JobApplicationStats, JobApplication } from '../types';

export default function Dashboard() {
  const navigate = useNavigate();
  const [stats, setStats] = useState<JobApplicationStats | null>(null);
  const [recentJobs, setRecentJobs] = useState<JobApplication[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      // Fetch statistics
      const statsData = await jobsApi.getStats();
      setStats(statsData);

      // Fetch recent jobs (first page, 5 items)
      const jobsData = await jobsApi.getAll({ page: 1, size: 5 });
      setRecentJobs(jobsData.items);
    } catch (err: any) {
      setError('Failed to load dashboard data');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleJobClick = (jobId: number) => {
    navigate(`/jobs/${jobId}`);
  };

  if (loading) {
    return (
      <Layout>
        <div className="flex items-center justify-center h-64">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading dashboard...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="card bg-red-50 border-red-200">
          <p className="text-red-700">{error}</p>
          <button onClick={fetchDashboardData} className="btn btn-primary mt-4">
            Retry
          </button>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Track and manage your job applications</p>
        </div>

        {/* Statistics Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          <StatsCard
            title="Total Applications"
            value={stats?.total_applications || 0}
            icon={Briefcase}
            color="blue"
          />
          <StatsCard
            title="Applied"
            value={stats?.applied || 0}
            icon={Clock}
            color="gray"
          />
          <StatsCard
            title="Interviews"
            value={stats?.interview || 0}
            icon={Clock}
            color="yellow"
          />
          <StatsCard
            title="Offers"
            value={stats?.offer || 0}
            icon={CheckCircle}
            color="green"
          />
          <StatsCard
            title="Rejected"
            value={stats?.rejected || 0}
            icon={XCircle}
            color="red"
          />
        </div>

        {/* Quick Actions */}
        {stats?.total_applications === 0 && (
          <div className="card bg-primary-50 border-primary-200">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-semibold text-primary-900">
                  Get Started
                </h3>
                <p className="text-primary-700 mt-1">
                  Add your first job application to start tracking!
                </p>
              </div>
              <button
                onClick={() => navigate('/jobs/new')}
                className="btn btn-primary"
              >
                Add Job Application
              </button>
            </div>
          </div>
        )}

        {/* Recent Applications */}
        <RecentJobs jobs={recentJobs} onJobClick={handleJobClick} />

        {/* View All Button */}
        {recentJobs.length > 0 && (
          <div className="text-center">
            <button
              onClick={() => navigate('/jobs')}
              className="btn btn-secondary"
            >
              View All Applications
            </button>
          </div>
        )}
      </div>
    </Layout>
  );
}