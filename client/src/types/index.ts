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
  metadata: Record<string, any>;
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

export interface MessageResponse extends Message {}

// Chat UI Types
export interface ChatState {
  isOpen: boolean;
  sessionId: string | null;
  messages: Message[];
  isLoading: boolean;
  isStreaming: boolean;
  error: string | null;
  visitorId: string | null;
}

export interface ChatActions {
  openChat: () => void;
  closeChat: () => void;
  sendMessage: (content: string) => Promise<void>;
  createSession: () => Promise<void>;
  loadSession: (sessionId: string) => Promise<void>;
  addMessage: (message: Message) => void;
  clearError: () => void;
  setStreaming: (isStreaming: boolean) => void;
}

export type ChatStore = ChatState & ChatActions;
