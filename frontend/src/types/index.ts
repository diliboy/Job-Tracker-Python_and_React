// User types
export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string | null;
}

export interface UserCreate {
  email: string;
  username: string;
  full_name?: string;
  password: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
}

// Job Application types
export type ApplicationStatus = 'applied' | 'interview' | 'offer' | 'rejected' | 'withdrawn';

export interface JobApplication {
  id: number;
  user_id: number;
  company_name: string;
  job_title: string;
  job_url: string | null;
  location: string | null;
  salary_range: string | null;
  status: ApplicationStatus;
  applied_date: string | null;
  interview_date: string | null;
  follow_up_date: string | null;
  job_description: string | null;
  notes: string | null;
  contact_person: string | null;
  contact_email: string | null;
  contact_phone: string | null;
  created_at: string;
  updated_at: string | null;
}

export interface JobApplicationCreate {
  company_name: string;
  job_title: string;
  job_url?: string;
  location?: string;
  salary_range?: string;
  status?: ApplicationStatus;
  applied_date?: string;
  interview_date?: string;
  follow_up_date?: string;
  job_description?: string;
  notes?: string;
  contact_person?: string;
  contact_email?: string;
  contact_phone?: string;
}

export interface JobApplicationUpdate extends Partial<JobApplicationCreate> {}

export interface JobApplicationListResponse {
  items: JobApplication[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface JobApplicationStats {
  total_applications: number;
  applied: number;
  interview: number;
  offer: number;
  rejected: number;
  withdrawn: number;
}

// Document types
export type DocumentType = 'resume' | 'cover_letter' | 'other';

export interface Document {
  id: number;
  job_application_id: number;
  filename: string;
  file_size: number;
  content_type: string;
  document_type: DocumentType;
  created_at: string;
}

export interface DocumentUploadResponse {
  message: string;
  document: Document;
}

// API Error type
export interface ApiError {
  detail: string;
}