import { create } from 'zustand';
import { ChatStore, Message, CreateSessionRequest, PRDPreview, MatchedExpert } from '../types';
import { api } from '../api/client';

// Generate visitor ID
const getVisitorId = (): string => {
  const existing = localStorage.getItem('unobot_visitor_id');
  if (existing) return existing;

  const newId = `visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem('unobot_visitor_id', newId);
  return newId;
};

export const useChatStore = create<ChatStore>((set, get) => ({
  // State
  isOpen: false,
  sessionId: null,
  messages: [],
  isLoading: false,
  isStreaming: false,
  error: null,
  visitorId: null,
  currentPhase: 'greeting',
  clientInfo: {},
  businessContext: {},
  qualification: {},
  prdPreview: null,
  isGeneratingPRD: false,
  matchedExperts: [],
  isMatchingExperts: false,

  // Actions
  openChat: () => {
    set({ isOpen: true });
    // Create session if doesn't exist
    const { sessionId, createSession } = get();
    if (!sessionId) {
      createSession();
    }
  },

  closeChat: () => {
    set({ isOpen: false });
  },

  createSession: async () => {
    // Prevent duplicate session creation
    const current = get();
    if (current.sessionId || current.isLoading) {
      return;
    }

    // Check if there's an existing session in localStorage
    const existingSessionId = localStorage.getItem('unobot_session_id');
    if (existingSessionId) {
      // Load existing session instead of creating new
      const { loadSession } = get();
      return loadSession(existingSessionId);
    }

    try {
      set({ isLoading: true, error: null });

      const visitorId = getVisitorId();
      const data: CreateSessionRequest = {
        visitor_id: visitorId,
        source_url: window.location.href,
        user_agent: navigator.userAgent,
      };

      const session = await api.createSession(data);

      // Store session ID
      localStorage.setItem('unobot_session_id', session.id);

      // Use messages from API response (includes welcome message)
      const messages: Message[] = session.messages.map(msg => ({
        id: msg.id,
        session_id: msg.session_id,
        role: msg.role,
        content: msg.content,
        meta_data: msg.meta_data,
        created_at: msg.created_at,
      }));

      set({
        sessionId: session.id,
        visitorId,
        messages: messages.length > 0 ? messages : [{
          id: `welcome_${Date.now()}`,
          session_id: session.id,
          role: 'assistant',
          content: "🎉 Welcome! I'm UnoBot, your AI business consultant from UnoDigit.\n\nTo get started, what's your name?",
          meta_data: { type: 'welcome' },
          created_at: new Date().toISOString(),
        }],
        isLoading: false,
        currentPhase: session.current_phase || 'greeting',
        clientInfo: session.client_info || {},
        businessContext: session.business_context || {},
        qualification: session.qualification || {},
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to create session'
      });
      console.error('Session creation error:', error);
    }
  },

  loadSession: async (sessionId: string) => {
    try {
      set({ isLoading: true, error: null });
      // Use resumeSession to mark session as active again
      const session = await api.resumeSession(sessionId);

      // Store session ID in localStorage for persistence across page refreshes
      localStorage.setItem('unobot_session_id', session.id);

      set({
        sessionId: session.id,
        messages: session.messages,
        isLoading: false,
        currentPhase: session.current_phase || 'greeting',
        clientInfo: session.client_info || {},
        businessContext: session.business_context || {},
        qualification: session.qualification || {},
      });
    } catch (error) {
      set({
        isLoading: false,
        error: error instanceof Error ? error.message : 'Failed to load session'
      });
      console.error('Session load error:', error);
    }
  },

  sendMessage: async (content: string) => {
    try {
      const { sessionId, messages, addMessage } = get();

      if (!sessionId) {
        throw new Error('No session available');
      }

      // Add user message immediately
      const userMessage: Message = {
        id: `user_${Date.now()}`,
        session_id: sessionId,
        role: 'user',
        content,
        meta_data: {},
        created_at: new Date().toISOString(),
      };

      addMessage(userMessage);

      // Set streaming state
      set({ isStreaming: true });

      // Call API to send message (this triggers AI response generation)
      await api.sendMessage(sessionId, { content });

      // Fetch the updated session to get the bot response
      const updatedSession = await api.getSession(sessionId);

      // Update messages and session data with the full conversation history
      set({
        messages: updatedSession.messages,
        isStreaming: false,
        currentPhase: updatedSession.current_phase || 'greeting',
        clientInfo: updatedSession.client_info || {},
        businessContext: updatedSession.business_context || {},
        qualification: updatedSession.qualification || {},
      });
    } catch (error) {
      set({
        isStreaming: false,
        error: error instanceof Error ? error.message : 'Failed to send message'
      });
      console.error('Send message error:', error);
    }
  },

  addMessage: (message: Message) => {
    set((state) => ({
      messages: [...state.messages, message],
    }));
  },

  clearError: () => {
    set({ error: null });
  },

  setStreaming: (isStreaming: boolean) => {
    set({ isStreaming });
  },

  generatePRD: async () => {
    try {
      const { sessionId } = get();
      if (!sessionId) {
        throw new Error('No session available');
      }

      set({ isGeneratingPRD: true, error: null });

      // Generate PRD
      const prdResponse = await api.generatePRD(sessionId);

      // Get preview
      const preview = await api.getPRDPreview(prdResponse.id);

      set({
        prdPreview: preview,
        isGeneratingPRD: false,
      });

      // Add a message to the chat indicating PRD was generated
      const prdMessage: Message = {
        id: `prd_${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: `📄 Project Requirements Document generated!\n\n**${preview.filename}**\n\nPreview: ${preview.preview_text}\n\nUse the download button to save the full PRD.`,
        meta_data: { type: 'prd_generated', prd_id: prdResponse.id },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, prdMessage],
      }));

    } catch (error) {
      set({
        isGeneratingPRD: false,
        error: error instanceof Error ? error.message : 'Failed to generate PRD'
      });
      console.error('PRD generation error:', error);
    }
  },

  downloadPRD: async (prdId: string) => {
    try {
      const blob = await api.downloadPRD(prdId);
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `PRD_${new Date().toISOString().split('T')[0]}.md`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (error) {
      set({
        error: error instanceof Error ? error.message : 'Failed to download PRD'
      });
      console.error('PRD download error:', error);
    }
  },

  clearPRDPreview: () => {
    set({ prdPreview: null });
  },

  matchExperts: async () => {
    try {
      const { sessionId } = get();
      if (!sessionId) {
        throw new Error('No session available');
      }

      set({ isMatchingExperts: true, error: null });

      // Call expert matching API
      const response = await api.matchExperts(sessionId);

      // Transform response to MatchedExpert format
      const matchedExperts: MatchedExpert[] = response.experts.map((expert, index) => ({
        id: expert.id,
        name: expert.name,
        email: expert.email,
        role: expert.role,
        bio: expert.bio,
        photo_url: expert.photo_url,
        specialties: expert.specialties,
        services: expert.services,
        match_score: response.match_scores[index] || 0,
      }));

      set({
        matchedExperts,
        isMatchingExperts: false,
      });

    } catch (error) {
      set({
        isMatchingExperts: false,
        error: error instanceof Error ? error.message : 'Failed to match experts'
      });
      console.error('Expert matching error:', error);
    }
  },

  clearMatchedExperts: () => {
    set({ matchedExperts: [] });
  },
}));
