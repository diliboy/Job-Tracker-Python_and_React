import axios, { AxiosError } from 'axios';
import type {
  User,
  UserCreate,
  LoginRequest,
  AuthResponse,
  JobApplication,
  JobApplicationCreate,
  JobApplicationUpdate,
  JobApplicationListResponse,
  JobApplicationStats,
  Document,
  DocumentUploadResponse,
  ApplicationStatus,
  DocumentType,
} from '../types';

// Base API URL - use environment variable in production
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authApi = {
  register: async (data: UserCreate): Promise<User> => {
    const response = await api.post<User>('/auth/register', data);
    return response.data;
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    const response = await api.post<AuthResponse>('/auth/login', data);
    return response.data;
  },

  getCurrentUser: async (): Promise<User> => {
    const response = await api.get<User>('/auth/me');
    return response.data;
  },
};

// Job Applications API
export const jobsApi = {
  getAll: async (params?: {
    page?: number;
    size?: number;
    status?: ApplicationStatus;
    company?: string;
  }): Promise<JobApplicationListResponse> => {
    const response = await api.get<JobApplicationListResponse>('/jobs', { params });
    return response.data;
  },

  getById: async (id: number): Promise<JobApplication> => {
    const response = await api.get<JobApplication>(`/jobs/${id}`);
    return response.data;
  },

  create: async (data: JobApplicationCreate): Promise<JobApplication> => {
    const response = await api.post<JobApplication>('/jobs', data);
    return response.data;
  },

  update: async (id: number, data: JobApplicationUpdate): Promise<JobApplication> => {
    const response = await api.put<JobApplication>(`/jobs/${id}`, data);
    return response.data;
  },

  delete: async (id: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/jobs/${id}`);
    return response.data;
  },

  getStats: async (): Promise<JobApplicationStats> => {
    const response = await api.get<JobApplicationStats>('/jobs/stats');
    return response.data;
  },
};

// Documents API
export const documentsApi = {
  getByJobId: async (jobId: number): Promise<Document[]> => {
    const response = await api.get<Document[]>(`/jobs/${jobId}/documents`);
    return response.data;
  },

  upload: async (
    jobId: number,
    file: File,
    documentType: DocumentType
  ): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('document_type', documentType);

    const response = await api.post<DocumentUploadResponse>(
      `/jobs/${jobId}/documents`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  download: async (documentId: number): Promise<Blob> => {
    const response = await api.get(`/documents/${documentId}`, {
      responseType: 'blob',
    });
    return response.data;
  },

  delete: async (documentId: number): Promise<{ message: string }> => {
    const response = await api.delete<{ message: string }>(`/documents/${documentId}`);
    return response.data;
  },
};

export default api;