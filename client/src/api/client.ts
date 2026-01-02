/**
 * UnoBot API Client
 *
 * Handles all HTTP communication with the UnoBot backend API.
 */

import { Session, Message, CreateSessionRequest, SendMessageRequest, PRDResponse, PRDPreview, ExpertMatchResponse } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

/**
 * API error response
 */
interface ApiError {
  detail: string;
  status_code: number;
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
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Backend returns data directly, not wrapped in { data: ... }
    return response.json();
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
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    // Backend returns data directly, not wrapped in { data: ... }
    return response.json();
  }

  /**
   * Create a new chat session
   * POST /api/v1/sessions
   */
  async createSession(data: CreateSessionRequest): Promise<Session> {
    return this.post<Session>('/api/v1/sessions', data);
  }

  /**
   * Get session details
   * GET /api/v1/sessions/{session_id}
   */
  async getSession(sessionId: string): Promise<Session> {
    return this.get<Session>(`/api/v1/sessions/${sessionId}`);
  }

  /**
   * Send a message
   * POST /api/v1/sessions/{session_id}/messages
   */
  async sendMessage(sessionId: string, data: SendMessageRequest): Promise<Message> {
    return this.post<Message>(`/api/v1/sessions/${sessionId}/messages`, data);
  }

  /**
   * Resume a session
   * POST /api/v1/sessions/{session_id}/resume
   */
  async resumeSession(sessionId: string): Promise<Session> {
    return this.post<Session>(`/api/v1/sessions/${sessionId}/resume`, {});
  }

  /**
   * Generate a PRD for a session
   * POST /api/v1/prd/generate
   */
  async generatePRD(sessionId: string): Promise<PRDResponse> {
    return this.post<PRDResponse>('/api/v1/prd/generate', { session_id: sessionId });
  }

  /**
   * Get PRD by session ID
   * GET /api/v1/prd/session/{session_id}
   */
  async getPRDBySession(sessionId: string): Promise<PRDResponse> {
    return this.get<PRDResponse>(`/api/v1/prd/session/${sessionId}`);
  }

  /**
   * Get PRD preview
   * GET /api/v1/prd/{prd_id}/preview
   */
  async getPRDPreview(prdId: string): Promise<PRDPreview> {
    return this.get<PRDPreview>(`/api/v1/prd/${prdId}/preview`);
  }

  /**
   * Download PRD as markdown file
   * GET /api/v1/prd/{prd_id}/download
   */
  async downloadPRD(prdId: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/v1/prd/${prdId}/download`, {
      method: 'GET',
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.blob();
  }

  /**
   * Match experts to a session
   * POST /api/v1/sessions/{session_id}/match-expert
   */
  async matchExperts(sessionId: string): Promise<ExpertMatchResponse> {
    return this.post<ExpertMatchResponse>(`/api/v1/sessions/${sessionId}/match-expert`, {});
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
