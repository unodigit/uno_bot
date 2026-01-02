/**
 * UnoBot API Client
 *
 * Handles all HTTP communication with the UnoBot backend API.
 */

import { Session, Message, CreateSessionRequest, SendMessageRequest, PRDResponse, PRDPreview, ExpertMatchResponse, AvailabilityResponse, BookingCreateRequest, BookingResponse, ConversationSummaryResponse, ConversationSummaryApproveRequest } from '../types';

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
   * Get expert availability
   * GET /api/v1/bookings/experts/{expert_id}/availability
   */
  async getExpertAvailability(expertId: string, timezone?: string): Promise<AvailabilityResponse> {
    const params = timezone ? `?timezone=${encodeURIComponent(timezone)}` : ''
    return this.get<AvailabilityResponse>(`/api/v1/bookings/experts/${expertId}/availability${params}`);
  }

  /**
   * Create a booking
   * POST /api/v1/bookings/sessions/{session_id}/bookings
   */
  async createBooking(sessionId: string, data: BookingCreateRequest): Promise<BookingResponse> {
    return this.post<BookingResponse>(`/api/v1/bookings/sessions/${sessionId}/bookings`, data);
  }

  /**
   * Cancel a booking
   * DELETE /api/v1/bookings/{booking_id}
   */
  async cancelBooking(bookingId: string, reason?: string): Promise<{ message: string }> {
    const endpoint = `/api/v1/bookings/${bookingId}`;
    const body = reason ? { reason } : {};

    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const error: ApiError = await response.json();
      throw new Error(error.detail || `HTTP ${response.status}`);
    }

    return response.json();
  }

  /**
   * Generate a session resume URL that can be used in emails
   */
  generateSessionResumeUrl(sessionId: string): string {
    const currentUrl = window.location.origin
    return `${currentUrl}?session_id=${encodeURIComponent(sessionId)}`
  }

  /**
   * Health check
   * GET /api/v1/health
   */
  async healthCheck(): Promise<{ status: string }> {
    return this.get<{ status: string }>('/api/v1/health');
  }

  /**
   * Generate conversation summary
   * POST /api/v1/prd/generate-summary
   */
  async generateSummary(sessionId: string): Promise<ConversationSummaryResponse> {
    return this.post<ConversationSummaryResponse>('/api/v1/prd/generate-summary', { session_id: sessionId });
  }

  /**
   * Approve summary and generate PRD
   * POST /api/v1/prd/approve-summary-and-generate-prd
   */
  async approveSummaryAndGeneratePRD(data: ConversationSummaryApproveRequest): Promise<PRDResponse> {
    return this.post<PRDResponse>('/api/v1/prd/approve-summary-and-generate-prd', data);
  }
}

// Export singleton instance
export const api = new ApiClient();
