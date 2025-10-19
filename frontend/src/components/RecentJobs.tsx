import { format } from 'date-fns';
import { Building2, MapPin, Calendar } from 'lucide-react';
import type { JobApplication } from '../types';

interface RecentJobsProps {
  jobs: JobApplication[];
  onJobClick: (id: number) => void;
}

const statusColors = {
  applied: 'badge-applied',
  interview: 'badge-interview',
  offer: 'badge-offer',
  rejected: 'badge-rejected',
  withdrawn: 'badge-withdrawn',
};

export default function RecentJobs({ jobs, onJobClick }: RecentJobsProps) {
  if (jobs.length === 0) {
    return (
      <div className="card">
        <h3 className="text-lg font-semibold mb-4">Recent Applications</h3>
        <div className="text-center py-8 text-gray-500">
          <p>No applications yet. Start by adding your first job application!</p>
        </div>
      </div>
    );
  }

  return (
    <div className="card">
      <h3 className="text-lg font-semibold mb-4">Recent Applications</h3>
      <div className="space-y-3">
        {jobs.map((job) => (
          <div
            key={job.id}
            onClick={() => onJobClick(job.id)}
            className="p-4 border border-gray-200 rounded-lg hover:border-primary-300 hover:bg-primary-50 cursor-pointer transition-colors"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Building2 className="w-4 h-4 text-gray-500" />
                  <h4 className="font-semibold text-gray-900">{job.company_name}</h4>
                  <span className={`badge ${statusColors[job.status]}`}>
                    {job.status}
                  </span>
                </div>
                <p className="text-sm text-gray-700 mb-2">{job.job_title}</p>
                <div className="flex items-center gap-4 text-xs text-gray-500">
                  {job.location && (
                    <span className="flex items-center gap-1">
                      <MapPin className="w-3 h-3" />
                      {job.location}
                    </span>
                  )}
                  {job.applied_date && (
                    <span className="flex items-center gap-1">
                      <Calendar className="w-3 h-3" />
                      Applied {format(new Date(job.applied_date), 'MMM d, yyyy')}
                    </span>
                  )}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}