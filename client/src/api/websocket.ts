/**
 * UnoBot WebSocket Client
 *
 * Handles real-time bidirectional communication with the backend using Socket.IO.
 */

import { io, Socket } from 'socket.io-client';
import { Message } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// WebSocket event types
export interface WebSocketEvents {
  connected: { session_id: string };
  message: { user_message: Message; ai_message: Message };
  typing_start: { from: 'bot' | 'user' };
  typing_stop: { from: 'bot' | 'user' };
  phase_change: { phase: string };
  prd_ready: { message: string };
  prd_generated: {
    prd_id: string;
    filename: string;
    preview_text: string;
    version: number;
    storage_url: string | null;
  };
  experts_matched: {
    experts: Array<{
      id: string;
      name: string;
      email: string;
      role: string;
      bio: string | null;
      photo_url: string | null;
      specialties: string[];
      services: string[];
      is_active: boolean;
    }>;
    match_scores: number[];
  };
  availability: {
    expert_id: string;
    expert_name: string;
    expert_role: string;
    timezone: string;
    slots: Array<{
      start_time: string;
      end_time: string;
      timezone: string;
      display_time: string;
      display_date: string;
    }>;
  };
  booking_confirmed: {
    booking_id: string;
    expert_id: string;
    start_time: string;
    end_time: string;
    timezone: string;
    meeting_link: string | null;
    client_name: string;
    client_email: string;
    status: string;
  };
  error: { message: string };
}

// Union type for all possible event names
type EventName = keyof WebSocketEvents | 'connect' | 'disconnect';

export class WebSocketClient {
  private socket: Socket | null = null;
  private sessionId: string | null = null;
  private isSocketConnected = false;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000; // Start with 1 second

  // Event listeners - key is event name, value is set of callbacks
  private listeners: Map<string, Set<(data: any) => void>> = new Map();

  // Track if listeners have been set up
  private listenersInitialized = false;

  /**
   * Connect to the WebSocket server
   */
  connect(sessionId: string): void {
    if (this.socket && this.socket.connected) {
      console.log('[WebSocket] Already connected');
      return;
    }

    this.sessionId = sessionId;

    // Connect with session_id in query params
    this.socket = io(`${API_BASE_URL}/ws`, {
      query: { session_id: sessionId },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionAttempts: this.maxReconnectAttempts,
      reconnectionDelay: this.reconnectDelay,
    });

    this.setupEventHandlers();
  }

  /**
   * Set up Socket.IO event handlers
   */
  private setupEventHandlers(): void {
    if (!this.socket) return;

    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected');
      this.isSocketConnected = true;
      this.reconnectAttempts = 0;

      // Join the session room
      if (this.socket && this.sessionId) {
        this.socket.emit('join_session', { session_id: this.sessionId });
      }
      this.emitLocal('connect', {});
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[WebSocket] Disconnected:', reason);
      this.isSocketConnected = false;
    });

    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error);
      this.reconnectAttempts++;
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        this.emitLocal('error', { message: 'Failed to connect to WebSocket server' });
      }
    });

    // Handle all WebSocket events
    this.socket.on('connected', (data) => this.emitLocal('connected', data));
    this.socket.on('message', (data) => this.emitLocal('message', data));
    this.socket.on('typing_start', (data) => this.emitLocal('typing_start', data));
    this.socket.on('typing_stop', (data) => this.emitLocal('typing_stop', data));
    this.socket.on('phase_change', (data) => this.emitLocal('phase_change', data));
    this.socket.on('prd_ready', (data) => this.emitLocal('prd_ready', data));
    this.socket.on('prd_generated', (data) => this.emitLocal('prd_generated', data));
    this.socket.on('experts_matched', (data) => this.emitLocal('experts_matched', data));
    this.socket.on('availability', (data) => this.emitLocal('availability', data));
    this.socket.on('booking_confirmed', (data) => this.emitLocal('booking_confirmed', data));
    this.socket.on('error', (data) => this.emitLocal('error', data));
  }

  /**
   * Send a chat message
   */
  sendMessage(content: string): void {
    if (!this.socket || !this.isSocketConnected) {
      console.error('[WebSocket] Not connected');
      return;
    }

    this.socket.emit('send_message', { content });
  }

  /**
   * Request PRD generation
   */
  generatePRD(): void {
    if (!this.socket || !this.isSocketConnected) {
      console.error('[WebSocket] Not connected');
      return;
    }

    this.socket.emit('generate_prd', {});
  }

  /**
   * Request expert matching
   */
  matchExperts(): void {
    if (!this.socket || !this.isSocketConnected) {
      console.error('[WebSocket] Not connected');
      return;
    }

    this.socket.emit('match_experts', {});
  }

  /**
   * Get expert availability
   */
  getAvailability(expertId: string, timezone: string = 'UTC'): void {
    if (!this.socket || !this.isSocketConnected) {
      console.error('[WebSocket] Not connected');
      return;
    }

    this.socket.emit('get_availability', { expert_id: expertId, timezone });
  }

  /**
   * Create a booking
   */
  createBooking(data: {
    expert_id: string;
    start_time: string;
    end_time: string;
    timezone: string;
    client_name: string;
    client_email: string;
  }): void {
    if (!this.socket || !this.isSocketConnected) {
      console.error('[WebSocket] Not connected');
      return;
    }

    this.socket.emit('create_booking', data);
  }

  /**
   * Add an event listener
   */
  on<K extends keyof WebSocketEvents>(
    event: K,
    callback: (data: WebSocketEvents[K]) => void
  ): void {
    const key = event as string;
    if (!this.listeners.has(key)) {
      this.listeners.set(key, new Set());
    }
    this.listeners.get(key)?.add(callback);
    this.listenersInitialized = true;
  }

  /**
   * Remove an event listener
   */
  off<K extends keyof WebSocketEvents>(
    event: K,
    callback: (data: WebSocketEvents[K]) => void
  ): void {
    const key = event as string;
    this.listeners.get(key)?.delete(callback);
  }

  /**
   * Emit an event to all listeners (internal)
   */
  private emitLocal(eventName: string, data: any): void {
    const callbacks = this.listeners.get(eventName);
    if (callbacks) {
      callbacks.forEach((callback) => callback(data));
    }
  }

  /**
   * Check if connected
   */
  isConnected(): boolean {
    return this.isSocketConnected;
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      this.isSocketConnected = false;
      this.sessionId = null;
    }
  }

  /**
   * Reconnect to the WebSocket server
   */
  reconnect(): void {
    if (this.sessionId) {
      this.disconnect();
      this.connect(this.sessionId);
    }
  }

  /**
   * Check if listeners have been initialized
   */
  areListenersInitialized(): boolean {
    return this.listenersInitialized;
  }
}

// Export singleton instance
export const wsClient = new WebSocketClient();
