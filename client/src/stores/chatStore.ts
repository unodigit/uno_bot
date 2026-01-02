import { create } from 'zustand';
import { ChatStore, Message, CreateSessionRequest } from '../types';
import { io, Socket } from 'socket.io-client';
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
  socket: null,

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
    // Disconnect WebSocket when closing chat
    const { socket } = get();
    if (socket) {
      socket.disconnect();
      set({ socket: null });
    }
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

      // Initialize WebSocket connection
      const { connectWebSocket } = get();
      connectWebSocket(session.id);
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

      // Initialize WebSocket connection for loaded session
      const { connectWebSocket } = get();
      connectWebSocket(session.id);
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
      const { sessionId, socket, addMessage, isStreaming } = get();

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

      // Send message via WebSocket
      if (socket && socket.connected) {
        socket.emit('message', {
          type: 'message',
          content
        });
      } else {
        // Fallback to REST API if WebSocket is not connected
        console.warn('WebSocket not connected, falling back to REST API');
        await api.sendMessage(sessionId, { content });

        // Fetch the updated session to get the bot response
        const updatedSession = await api.getSession(sessionId);

        // Update messages with the full conversation history
        set({
          messages: updatedSession.messages,
          isStreaming: false,
          currentPhase: updatedSession.current_phase || 'greeting',
          clientInfo: updatedSession.client_info || {},
          businessContext: updatedSession.business_context || {},
          qualification: updatedSession.qualification || {},
        });
      }

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

  connectWebSocket: (sessionId: string | null) => {
    if (!sessionId) return;

    // Disconnect existing socket if any
    const { socket } = get();
    if (socket) {
      socket.disconnect();
    }

    // Create new WebSocket connection with reconnection logic
    const newSocket = io(`${import.meta.env.VITE_API_URL || 'http://localhost:8001'}/ws/chat`, {
      query: { session_id: sessionId },
      transports: ['websocket', 'polling'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5,
      timeout: 10000,
    });

    newSocket.on('connect', () => {
      console.log('WebSocket connected');
      set({ error: null });
    });

    newSocket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason);
      if (reason === 'io server disconnect') {
        // Server initiated disconnect, don't reconnect
        set({ error: 'Connection lost. Please refresh the page.' });
      } else {
        // Auto-reconnection will handle this
        set({ error: 'Connection lost. Reconnecting...' });
      }
    });

    newSocket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error);
      set({ error: 'Failed to connect to server' });
    });

    // Handle incoming messages
    newSocket.on('message_sent', (data) => {
      // User message was sent successfully
      console.log('Message sent:', data);
    });

    newSocket.on('message_stream', (data) => {
      // Handle streaming AI response
      const { messages, addMessage } = get();
      const { message } = data;

      // Find if this message already exists
      const existingMessageIndex = messages.findIndex(m => m.id === message.id);

      if (existingMessageIndex >= 0) {
        // Update existing message content
        const updatedMessages = [...messages];
        updatedMessages[existingMessageIndex] = {
          ...updatedMessages[existingMessageIndex],
          content: message.content,
          meta_data: { ...message.meta_data }
        };
        set({ messages: updatedMessages });
      } else {
        // Add new message
        addMessage({
          id: message.id,
          session_id: message.session_id,
          role: message.role as 'user' | 'assistant',
          content: message.content,
          meta_data: message.meta_data,
          created_at: message.created_at,
        });
      }

      // Stop streaming if message is complete
      if (message.is_complete) {
        set({ isStreaming: false });
      }
    });

    newSocket.on('typing_start', (data) => {
      set({ isStreaming: true });
    });

    newSocket.on('typing_stop', (data) => {
      set({ isStreaming: false });
    });

    newSocket.on('error', (data) => {
      set({ error: data.error || 'An error occurred' });
    });

    set({ socket: newSocket });
  },
}));
