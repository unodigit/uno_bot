import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import { CreateSessionRequest, CreateSessionResponse, MessageCreate, MessageResponse, Session } from '../types';

// Get API URL from environment or default
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class APIClient {
  private client: AxiosInstance;

  constructor(baseURL: string) {
    this.client = axios.create({
      baseURL,
      headers: {
        'Content-Type': 'application/json',
      },
      timeout: 30000,
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add session ID header if available
        const sessionId = localStorage.getItem('unobot_session_id');
        if (sessionId) {
          config.headers['X-Session-ID'] = sessionId;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        // Handle common errors
        if (error.response) {
          const { status, data } = error.response;
          console.error(`API Error ${status}:`, data);
        } else if (error.request) {
          console.error('API Error: No response received');
        } else {
          console.error('API Error:', error.message);
        }
        return Promise.reject(error);
      }
    );
  }

  // Session endpoints
  async createSession(data: CreateSessionRequest): Promise<CreateSessionResponse> {
    const response = await this.client.post('/api/v1/sessions', data);
    return response.data;
  }

  async getSession(sessionId: string): Promise<Session> {
    const response = await this.client.get(`/api/v1/sessions/${sessionId}`);
    return response.data;
  }

  async resumeSession(sessionId: string): Promise<Session> {
    const response = await this.client.post('/api/v1/sessions/${sessionId}/resume', { session_id: sessionId });
    return response.data;
  }

  // Message endpoints
  async sendMessage(sessionId: string, data: MessageCreate): Promise<MessageResponse> {
    const response = await this.client.post(`/api/v1/sessions/${sessionId}/messages`, data);
    return response.data;
  }

  // Health check
  async healthCheck(): Promise<{ status: string; version: string }> {
    const response = await this.client.get('/api/v1/health');
    return response.data;
  }
}

// Export singleton instance
export const api = new APIClient(API_BASE_URL);
