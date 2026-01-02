/**
 * UnoBot API Client
 *
 * Handles all HTTP communication with the UnoBot backend API.
 */

import { Session, Message, CreateSessionRequest, SendMessageRequest } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * API error response
 */
interface ApiError {
  detail: string;
  status_code?: number;
}

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  /**
   * Make a GET request
   */
  private async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Make a POST request
   */
  private async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
      const error: ApiError = await response.json().catch(() => ({ detail: `HTTP ${response.status}` }));
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return await response.json();
  }

  /**
   * Create a new chat session
   * POST /api/v1/sessions
   */
  async createSession(data: CreateSessionRequest): Promise<Session> {
    const response = await this.post<any>('/api/v1/sessions', data);

    // Transform messages metadata -> meta_data to match our types
    return {
      ...response,
      messages: response.messages.map((msg: any) => ({
        ...msg,
        meta_data: msg.meta_data || msg.metadata || {},
      })),
    };
  }

  /**
   * Get session details
   * GET /api/v1/sessions/{session_id}
   */
  async getSession(sessionId: string): Promise<Session> {
    const response = await this.get<any>(`/api/v1/sessions/${sessionId}`);

    // Transform messages metadata -> meta_data to match our types
    return {
      ...response,
      messages: response.messages.map((msg: any) => ({
        ...msg,
        meta_data: msg.meta_data || msg.metadata || {},
      })),
    };
  }

  /**
   * Send a message
   * POST /api/v1/sessions/{session_id}/messages
   */
  async sendMessage(sessionId: string, data: SendMessageRequest): Promise<Message> {
    const response = await this.post<any>(`/api/v1/sessions/${sessionId}/messages`, data);

    // Transform metadata -> meta_data to match our types
    return {
      ...response,
      meta_data: response.metadata || response.meta_data || {},
    };
  }

  /**
   * Resume a session
   * POST /api/v1/sessions/{session_id}/resume
   */
  async resumeSession(sessionId: string): Promise<Session> {
    const response = await this.post<any>(`/api/v1/sessions/${sessionId}/resume`, {});

    // Transform messages metadata -> meta_data to match our types
    return {
      ...response,
      messages: response.messages.map((msg: any) => ({
        ...msg,
        meta_data: msg.meta_data || msg.metadata || {},
      })),
    };
  }

  /**
   * Health check
   * GET /api/v1/health
   */
  async healthCheck(): Promise<{ status: string }> {
    return this.get<{ status: string }>('/api/v1/health');
  }
}

// Export singleton instance
export const api = new ApiClient();
