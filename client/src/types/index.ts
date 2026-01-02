// API Types
export interface Session {
  id: string;
  visitor_id: string;
  status: 'active' | 'completed' | 'abandoned';
  current_phase: string;
  client_info: Record<string, any>;
  business_context: Record<string, any>;
  qualification: Record<string, any>;
  lead_score: number | null;
  recommended_service: string | null;
  matched_expert_id: string | null;
  prd_id: string | null;
  booking_id: string | null;
  started_at: string;
  last_activity: string;
  completed_at: string | null;
  messages: Message[];
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  meta_data: Record<string, any>;
  created_at: string;
}

export interface CreateSessionRequest {
  visitor_id: string;
  source_url?: string;
  user_agent?: string;
}

export interface CreateSessionResponse extends Session {}

export interface MessageCreate {
  content: string;
  metadata?: Record<string, any>;
}

export interface SendMessageRequest {
  content: string;
  metadata?: Record<string, any>;
}

export interface MessageResponse extends Message {}

// PRD Types
export interface PRDResponse {
  id: string;
  session_id: string;
  version: number;
  content_markdown: string;
  conversation_summary: string | null;
  client_company: string | null;
  client_name: string | null;
  recommended_service: string | null;
  matched_expert: string | null;
  storage_url: string | null;
  download_count: number;
  created_at: string;
  expires_at: string;
}

export interface PRDPreview {
  id: string;
  filename: string;
  preview_text: string;
  version: number;
  created_at: string;
}

export interface PRDGenerateRequest {
  session_id: string;
}

export interface PRDRegenerateRequest {
  session_id: string;
  feedback?: string;
}

export interface ConversationSummaryResponse {
  summary: string;
  session_id: string;
}

export interface ConversationSummaryApproveRequest {
  session_id: string;
  summary: string;
  approve: boolean;
}

export interface SummaryState {
  summary: string | null;
  isGenerating: boolean;
  isReviewing: boolean;
}

// Expert Types
export interface Expert {
  id: string;
  name: string;
  email: string;
  role: string;
  bio: string | null;
  photo_url: string | null;
  specialties: string[];
  services: string[];
  is_active: boolean;
}

export interface ExpertMatchResponse {
  experts: Expert[];
  match_scores: number[];
}

export interface MatchedExpert {
  id: string;
  name: string;
  email: string;
  role: string;
  bio: string | null;
  photo_url: string | null;
  specialties: string[];
  services: string[];
  match_score: number;
}

// Booking Types
export interface TimeSlot {
  start_time: string;
  end_time: string;
  timezone: string;
  display_time: string;
  display_date: string;
}

export interface AvailabilityResponse {
  expert_id: string;
  expert_name: string;
  expert_role: string;
  timezone: string;
  slots: TimeSlot[];
  generated_at: string;
}

export interface BookingCreateRequest {
  expert_id: string;
  start_time: string;
  end_time: string;
  timezone: string;
  client_name: string;
  client_email: string;
}

export interface BookingResponse {
  id: string;
  session_id: string;
  expert_id: string;
  calendar_event_id: string | null;
  title: string;
  start_time: string;
  end_time: string;
  timezone: string;
  meeting_link: string | null;
  expert_email: string;
  client_email: string;
  client_name: string;
  status: string;
  created_at: string;
}

// Chat UI Types
export interface ChatState {
  isOpen: boolean;
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  visitorId: string | null;
  currentPhase: string;
  clientInfo: Record<string, any>;
  businessContext: Record<string, any>;
  qualification: Record<string, any>;
  prdPreview: PRDPreview | null;
  isGeneratingPRD: boolean;
  matchedExperts: MatchedExpert[];
  isMatchingExperts: boolean;
  // Summary state
  conversationSummary: string | null;
  isGeneratingSummary: boolean;
  isReviewingSummary: boolean;
  // Booking flow state
  bookingState: 'idle' | 'selecting_expert' | 'selecting_time' | 'confirming' | 'completed' | 'cancelled';
  selectedExpert: MatchedExpert | null;
  selectedTimeSlot: TimeSlot | null;
  createdBooking: BookingResponse | null;
  isCreatingBooking: boolean;
  isCancellingBooking: boolean;
  // WebSocket state
  isWebSocketConnected: boolean;
  isTyping: boolean;
  // Sound notifications state
  soundNotificationsEnabled: boolean;
  // Widget position configuration
  widgetPosition: 'left' | 'right';
  // GDPR Consent state
  hasGivenConsent: boolean;
  showConsentModal: boolean;
}

export interface ChatActions {
  openChat: () => void;
  closeChat: () => void;
  sendMessage: (content: string) => Promise<void>;
  sendStreamingMessage: (content: string) => void;
  createSession: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearError: () => void;
  setStreaming: (isStreaming: boolean) => void;
  generatePRD: () => Promise<void>;
  regeneratePRD: (feedback?: string) => Promise<void>;
  downloadPRD: (prdId: string) => Promise<void>;
  clearPRDPreview: () => void;
  matchExperts: () => Promise<void>;
  clearMatchedExperts: () => void;
  // Summary actions
  generateSummary: () => Promise<void>;
  approveSummary: () => Promise<void>;
  rejectSummary: () => Promise<void>;
  clearSummary: () => void;
  // Booking flow actions
  startBookingFlow: (expert: MatchedExpert) => void;
  selectTimeSlot: (slot: TimeSlot) => Promise<void>;
  confirmBooking: (clientName: string, clientEmail: string) => Promise<void>;
  cancelBooking: (reason?: string) => Promise<void>;
  resetBookingFlow: () => void;
  // WebSocket actions
  initializeWebSocket: () => void;
  disconnectWebSocket: () => void;
  sendMessageViaWebSocket: (content: string) => void;
  generatePRDViaWebSocket: () => void;
  matchExpertsViaWebSocket: () => void;
  getAvailabilityViaWebSocket: (expertId: string, timezone?: string) => void;
  createBookingViaWebSocket: (data: {
    expert_id: string;
    start_time: string;
    end_time: string;
    timezone: string;
    client_name: string;
    client_email: string;
  }) => void;
  isWebSocketAvailable: () => boolean;
  // Sound notification actions
  toggleSoundNotifications: () => void;
  setSoundNotificationsEnabled: (enabled: boolean) => void;
  playNotificationSound: (type?: 'message' | 'booking' | 'prd') => void;
  // Widget position actions
  setWidgetPosition: (position: 'left' | 'right') => void;
  toggleWidgetPosition: () => void;
  // Consent actions
  checkConsent: () => Promise<void>;
  acceptConsent: () => Promise<void>;
  declineConsent: () => Promise<void>;
  // Note: The following methods are also available on the store but are not part of ChatActions
  // They are added for completeness: addMessage, clearError, setStreaming
}

export type ChatStore = ChatState & ChatActions;
