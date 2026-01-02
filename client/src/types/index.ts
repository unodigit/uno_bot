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
  generatePRD: () => Promise<void>;
  downloadPRD: (prdId: string) => Promise<void>;
  clearPRDPreview: () => void;
  matchExperts: () => Promise<void>;
  clearMatchedExperts: () => void;
}

export type ChatStore = ChatState & ChatActions;
