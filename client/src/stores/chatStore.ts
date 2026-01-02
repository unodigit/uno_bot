import { create } from 'zustand';
import { ChatStore, Message, CreateSessionRequest } from '../types';
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

      // Call API to get bot response
      const response = await api.sendMessage(sessionId, { content });

      // Add bot response
      addMessage(response);

      set({ isStreaming: false });
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
}));
