import { create } from 'zustand';
import { ChatStore, Message, CreateSessionRequest, MatchedExpert, TimeSlot, BookingCreateRequest, PRDResponse, ConversationSummaryResponse } from '../types';
import { api } from '../api/client';
import { wsClient } from '../api/websocket';

// Generate visitor ID
const getVisitorId = (): string => {
  const existing = localStorage.getItem('unobot_visitor_id');
  if (existing) return existing;

  const newId = `visitor_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
  localStorage.setItem('unobot_visitor_id', newId);
  return newId;
};

// Helper to setup WebSocket event listeners
const setupWebSocketListeners = (set: any, get: any) => {
  // Connection established
  wsClient.on('connected', (data) => {
    console.log('[WebSocket] Connected to session:', data.session_id);
    set({ isWebSocketConnected: true });
  });

  // Message received
  wsClient.on('message', (data) => {
    const { user_message, ai_message } = data;
    set((state: any) => ({
      messages: [...state.messages, user_message, ai_message],
      isStreaming: false,
    }));
  });

  // Streaming message received
  wsClient.on('streaming_message', (data) => {
    const { chunk, is_complete, message_id } = data;

    set((state: any) => {
      const { messages } = state;

      if (is_complete) {
        // Final message - replace the streaming message with complete message
        const updatedMessages = messages.map((msg: Message) => {
          if (msg.id === message_id) {
            return { ...msg, content: msg.content + chunk };
          }
          return msg;
        });

        return {
          messages: updatedMessages,
          isStreaming: false,
        };
      } else {
        // Streaming chunk - update or create streaming message
        let updatedMessages = [...messages];
        const lastMessage = messages[messages.length - 1];

        if (lastMessage && lastMessage.role === 'assistant' && lastMessage.content) {
          // Update existing assistant message
          updatedMessages[updatedMessages.length - 1] = {
            ...lastMessage,
            content: lastMessage.content + chunk
          };
        } else {
          // Create new assistant message
          const newMessage = {
            id: message_id || `stream_${Date.now()}`,
            session_id: get().sessionId || '',
            role: 'assistant',
            content: chunk,
            meta_data: {},
            created_at: new Date().toISOString(),
          };
          updatedMessages.push(newMessage);
        }

        return {
          messages: updatedMessages,
          isStreaming: true,
        };
      }
    });
  });

  // Typing indicators
  wsClient.on('typing_start', () => {
    set({ isTyping: true });
  });

  wsClient.on('typing_stop', () => {
    set({ isTyping: false });
  });

  // Phase change
  wsClient.on('phase_change', (data) => {
    set({ currentPhase: data.phase });
  });

  // PRD ready notification
  wsClient.on('prd_ready', (data) => {
    console.log('[WebSocket] PRD ready:', data.message);
    // Could trigger UI notification here
  });

  // PRD generated
  wsClient.on('prd_generated', (data) => {
    const preview = {
      id: data.prd_id,
      filename: data.filename,
      preview_text: data.preview_text,
      version: data.version,
      created_at: new Date().toISOString(),
    };
    set({ prdPreview: preview, isGeneratingPRD: false });

    // Add message to chat
    const prdMessage: Message = {
      id: `prd_${Date.now()}`,
      session_id: get().sessionId || '',
      role: 'assistant',
      content: `📄 Project Requirements Document generated!\n\n**${data.filename}**\n\nPreview: ${data.preview_text}\n\nUse the download button to save the full PRD.`,
      meta_data: { type: 'prd_generated', prd_id: data.prd_id },
      created_at: new Date().toISOString(),
    };
    set((state: any) => ({ messages: [...state.messages, prdMessage] }));
  });

  // Experts matched
  wsClient.on('experts_matched', (data) => {
    const matchedExperts: MatchedExpert[] = data.experts.map((expert, index) => ({
      id: expert.id,
      name: expert.name,
      email: expert.email,
      role: expert.role,
      bio: expert.bio,
      photo_url: expert.photo_url,
      specialties: expert.specialties,
      services: expert.services,
      match_score: data.match_scores[index] || 0,
    }));
    set({ matchedExperts, isMatchingExperts: false });
  });

  // Availability received
  wsClient.on('availability', (data) => {
    // Update selected expert's availability in the store
    // This would be handled by the booking flow
    console.log('[WebSocket] Availability received:', data);
  });

  // Booking confirmed
  wsClient.on('booking_confirmed', (data) => {
    const { selectedExpert } = get();
    const bookingMessage: Message = {
      id: `booking_${Date.now()}`,
      session_id: get().sessionId || '',
      role: 'assistant',
      content: `✅ Booking confirmed with ${selectedExpert?.name}!\n\nDate: ${new Date(data.start_time).toLocaleDateString()}\nTime: ${new Date(data.start_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}\n\nCheck the confirmation card for details.`,
      meta_data: { type: 'booking_confirmed', booking_id: data.booking_id },
      created_at: new Date().toISOString(),
    };

    set((state: any) => ({
      messages: [...state.messages, bookingMessage],
      createdBooking: data,
      bookingState: 'completed',
      isCreatingBooking: false,
    }));
  });

  // Error handling
  wsClient.on('error', (data) => {
    console.error('[WebSocket] Error:', data.message);
    set({ error: data.message, isStreaming: false });
  });
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
  // Summary state
  conversationSummary: null,
  isGeneratingSummary: false,
  isReviewingSummary: false,
  // Booking flow state
  bookingState: 'idle',
  selectedExpert: null,
  selectedTimeSlot: null,
  createdBooking: null,
  isCreatingBooking: false,
  isCancellingBooking: false,
  // WebSocket state
  isWebSocketConnected: false,
  isTyping: false,
  // Sound notifications state - load from localStorage
  soundNotificationsEnabled: localStorage.getItem('unobot_sound_notifications') === 'true',
  // Widget position state - load from localStorage, default to 'right'
  widgetPosition: (localStorage.getItem('unobot_widget_position') as 'left' | 'right') || 'right',

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
      const { sessionId, addMessage } = get();

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

  // Send message with streaming (preferred method)
  sendStreamingMessage: (content: string) => {
    const { sessionId, addMessage } = get();

    if (!sessionId) {
      console.error('No session available');
      return;
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

    // Send via WebSocket with streaming
    wsClient.sendStreamingMessage(content);
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

  /**
   * Generate a session resume URL for email links
   */
  generateSessionResumeUrl: (): string | null => {
    const { sessionId } = get();
    if (!sessionId) return null;
    return api.generateSessionResumeUrl(sessionId);
  },

  // Booking flow actions
  startBookingFlow: (expert: MatchedExpert) => {
    set({
      selectedExpert: expert,
      bookingState: 'selecting_time',
      selectedTimeSlot: null,
      createdBooking: null,
      error: null,
    });
  },

  selectTimeSlot: async (slot: TimeSlot) => {
    set({
      selectedTimeSlot: slot,
      bookingState: 'confirming',
    });
  },

  confirmBooking: async (clientName: string, clientEmail: string) => {
    try {
      const { sessionId, selectedExpert, selectedTimeSlot } = get();

      if (!sessionId || !selectedExpert || !selectedTimeSlot) {
        throw new Error('Missing booking information');
      }

      set({ isCreatingBooking: true, error: null });

      // Step 1: Refresh availability to ensure slot is still available
      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const availabilityResponse = await fetch(
        `${API_BASE_URL}/api/v1/bookings/experts/${selectedExpert.id}/availability?timezone=${encodeURIComponent(selectedTimeSlot.timezone)}`
      );

      if (!availabilityResponse.ok) {
        throw new Error('Failed to verify availability');
      }

      const availabilityData = await availabilityResponse.json();

      // Step 2: Check if the selected slot is still available
      const isSlotAvailable = availabilityData.slots.some(
        (slot: any) => slot.start_time === selectedTimeSlot.start_time
      );

      if (!isSlotAvailable) {
        // Slot is no longer available - show error with alternative slots
        const alternativeSlots = availabilityData.slots.slice(0, 3);
        let errorMsg = 'This time slot is no longer available. Please select another time.';

        if (alternativeSlots.length > 0) {
          const slotTimes = alternativeSlots.map((s: any) => s.display_time).join(', ');
          errorMsg += ` Alternatives: ${slotTimes}`;
        }

        throw new Error(errorMsg);
      }

      // Step 3: Proceed with booking creation
      const bookingData: BookingCreateRequest = {
        expert_id: selectedExpert.id,
        start_time: selectedTimeSlot.start_time,
        end_time: selectedTimeSlot.end_time,
        timezone: selectedTimeSlot.timezone,
        client_name: clientName,
        client_email: clientEmail,
      };

      const booking = await api.createBooking(sessionId, bookingData);

      // Add message to chat
      const bookingMessage: Message = {
        id: `booking_${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: `✅ Booking confirmed with ${selectedExpert.name}!\n\nDate: ${new Date(booking.start_time).toLocaleDateString()}\nTime: ${new Date(booking.start_time).toLocaleTimeString([], {hour: '2-digit', minute: '2-digit'})}\n\nCheck the confirmation card for details.`,
        meta_data: { type: 'booking_confirmed', booking_id: booking.id },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, bookingMessage],
        createdBooking: booking,
        bookingState: 'completed',
        isCreatingBooking: false,
      }));
    } catch (error) {
      set({
        isCreatingBooking: false,
        error: error instanceof Error ? error.message : 'Failed to create booking',
      });
      console.error('Booking creation error:', error);
    }
  },

  resetBookingFlow: () => {
    set({
      bookingState: 'idle',
      selectedExpert: null,
      selectedTimeSlot: null,
      createdBooking: null,
      isCreatingBooking: false,
      isCancellingBooking: false,
      error: null,
    });
  },

  cancelBooking: async (reason?: string) => {
    try {
      const { createdBooking, sessionId } = get();

      if (!createdBooking) {
        throw new Error('No booking to cancel');
      }

      set({ isCancellingBooking: true, error: null });

      // Call API to cancel booking
      await api.cancelBooking(createdBooking.id, reason);

      // Add message to chat
      const cancelMessage: Message = {
        id: `cancel_${Date.now()}`,
        session_id: sessionId || '',
        role: 'assistant',
        content: `❌ Booking cancelled.\n\nYour appointment with ${createdBooking.client_name} has been cancelled.\n\nIf you need to book again, you can start a new booking flow.`,
        meta_data: { type: 'booking_cancelled', booking_id: createdBooking.id },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, cancelMessage],
        bookingState: 'cancelled',
        isCancellingBooking: false,
        createdBooking: null,
      }));
    } catch (error) {
      set({
        isCancellingBooking: false,
        error: error instanceof Error ? error.message : 'Failed to cancel booking',
      });
      console.error('Booking cancellation error:', error);
    }
  },

  // Summary actions
  generateSummary: async () => {
    try {
      const { sessionId } = get();
      if (!sessionId) {
        throw new Error('No session available');
      }

      set({ isGeneratingSummary: true, isReviewingSummary: false, error: null });

      // Generate summary
      const response = await api.generateSummary(sessionId);

      set({
        conversationSummary: response.summary,
        isGeneratingSummary: false,
        isReviewingSummary: true,
      });

      // Add a message to the chat indicating summary was generated
      const summaryMessage: Message = {
        id: `summary_${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: `📋 Conversation Summary generated!\n\nPlease review the summary below and confirm if it accurately captures your requirements. You can approve it or request a regeneration before we proceed with PRD generation.\n\n**Summary:**\n${response.summary}`,
        meta_data: { type: 'summary_generated' },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, summaryMessage],
      }));

    } catch (error) {
      set({
        isGeneratingSummary: false,
        error: error instanceof Error ? error.message : 'Failed to generate summary'
      });
      console.error('Summary generation error:', error);
    }
  },

  approveSummary: async () => {
    try {
      const { sessionId, conversationSummary } = get();
      if (!sessionId || !conversationSummary) {
        throw new Error('No session or summary available');
      }

      set({ isGeneratingPRD: true, isReviewingSummary: false, error: null });

      // Approve summary and generate PRD
      const response = await api.approveSummaryAndGeneratePRD({
        session_id: sessionId,
        summary: conversationSummary,
        approve: true,
      });

      // When approve=true, API returns PRDResponse
      const prdResponse = response as PRDResponse;

      // Get preview
      const preview = await api.getPRDPreview(prdResponse.id);

      set({
        prdPreview: preview,
        isGeneratingPRD: false,
        conversationSummary: null,
        isReviewingSummary: false,
      });

      // Add a success message to the chat
      const successMessage: Message = {
        id: `summary_approved_${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: `✅ Summary approved!\n\n📄 Project Requirements Document generated!\n\n**${preview.filename}**\n\nPreview: ${preview.preview_text}\n\nUse the download button to save the full PRD.`,
        meta_data: { type: 'summary_approved', prd_id: prdResponse.id },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, successMessage],
      }));

    } catch (error) {
      set({
        isGeneratingPRD: false,
        isReviewingSummary: false,
        error: error instanceof Error ? error.message : 'Failed to approve summary'
      });
      console.error('Summary approval error:', error);
    }
  },

  rejectSummary: async () => {
    try {
      const { sessionId, conversationSummary } = get();
      if (!sessionId || !conversationSummary) {
        throw new Error('No session or summary available');
      }

      set({ isGeneratingSummary: true, error: null });

      // Reject and regenerate
      const response = await api.approveSummaryAndGeneratePRD({
        session_id: sessionId,
        summary: conversationSummary,
        approve: false,
      });

      // When approve=false, response is ConversationSummaryResponse
      const summaryResponse = response as ConversationSummaryResponse;

      set({
        conversationSummary: summaryResponse.summary,
        isGeneratingSummary: false,
        isReviewingSummary: true,
      });

      // Add a message to the chat
      const regenerateMessage: Message = {
        id: `summary_regen_${Date.now()}`,
        session_id: sessionId,
        role: 'assistant',
        content: `🔄 New summary generated!\n\n**New Summary:**\n${summaryResponse.summary}\n\nDo you approve this revised summary?`,
        meta_data: { type: 'summary_regenerated' },
        created_at: new Date().toISOString(),
      };

      set((state) => ({
        messages: [...state.messages, regenerateMessage],
      }));

    } catch (error) {
      set({
        isGeneratingSummary: false,
        isReviewingSummary: false,
        error: error instanceof Error ? error.message : 'Failed to regenerate summary'
      });
      console.error('Summary rejection error:', error);
    }
  },

  clearSummary: () => {
    set({ conversationSummary: null, isGeneratingSummary: false, isReviewingSummary: false });
  },

  // WebSocket actions
  initializeWebSocket: () => {
    const { sessionId } = get();
    if (!sessionId) {
      console.error('[WebSocket] Cannot initialize: no session ID');
      return;
    }

    // Setup listeners only once
    if (!wsClient.areListenersInitialized()) {
      setupWebSocketListeners(set, get);
    }

    // Connect
    wsClient.connect(sessionId);
  },

  disconnectWebSocket: () => {
    wsClient.disconnect();
    set({ isWebSocketConnected: false, isTyping: false });
  },

  // WebSocket-based message sending
  sendMessageViaWebSocket: (content: string) => {
    const { sessionId, addMessage } = get();

    if (!sessionId) {
      throw new Error('No session available');
    }

    if (!wsClient.isConnected()) {
      throw new Error('WebSocket not connected');
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

    // Send via WebSocket
    wsClient.sendMessage(content);
  },

  // WebSocket-based PRD generation
  generatePRDViaWebSocket: () => {
    const { sessionId } = get();
    if (!sessionId) {
      throw new Error('No session available');
    }

    if (!wsClient.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    set({ isGeneratingPRD: true, error: null });
    wsClient.generatePRD();
  },

  // WebSocket-based expert matching
  matchExpertsViaWebSocket: () => {
    const { sessionId } = get();
    if (!sessionId) {
      throw new Error('No session available');
    }

    if (!wsClient.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    set({ isMatchingExperts: true, error: null });
    wsClient.matchExperts();
  },

  // WebSocket-based availability check
  getAvailabilityViaWebSocket: (expertId: string, timezone: string = 'UTC') => {
    if (!wsClient.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    wsClient.getAvailability(expertId, timezone);
  },

  // WebSocket-based booking creation
  createBookingViaWebSocket: (data: {
    expert_id: string;
    start_time: string;
    end_time: string;
    timezone: string;
    client_name: string;
    client_email: string;
  }) => {
    const { sessionId } = get();
    if (!sessionId) {
      throw new Error('No session available');
    }

    if (!wsClient.isConnected()) {
      throw new Error('WebSocket not connected');
    }

    set({ isCreatingBooking: true, error: null });
    wsClient.createBooking(data);
  },

  // Helper to check if WebSocket is available
  isWebSocketAvailable: () => {
    return wsClient.isConnected();
  },

  // Sound notification actions
  toggleSoundNotifications: () => {
    set((state: any) => {
      const newEnabled = !state.soundNotificationsEnabled;
      localStorage.setItem('unobot_sound_notifications', newEnabled.toString());
      return { soundNotificationsEnabled: newEnabled };
    });
  },

  setSoundNotificationsEnabled: (enabled: boolean) => {
    localStorage.setItem('unobot_sound_notifications', enabled.toString());
    set({ soundNotificationsEnabled: enabled });
  },

  playNotificationSound: (type: 'message' | 'booking' | 'prd' = 'message') => {
    const { soundNotificationsEnabled } = get();
    if (!soundNotificationsEnabled) {
      return;
    }

    // Create audio context and play notification sound
    // Using Web Audio API to generate a simple beep
    try {
      const audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      const oscillator = audioContext.createOscillator();
      const gainNode = audioContext.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(audioContext.destination);

      // Different frequencies for different notification types
      const frequencies = {
        message: 800,    // Higher pitch for messages
        booking: 600,    // Medium pitch for bookings
        prd: 500,        // Lower pitch for PRD
      };

      oscillator.frequency.value = frequencies[type] || 800;
      oscillator.type = 'sine';

      // Volume envelope
      gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);

      oscillator.start(audioContext.currentTime);
      oscillator.stop(audioContext.currentTime + 0.1);
    } catch (error) {
      console.warn('Could not play notification sound:', error);
    }
  },

  // Widget position actions
  setWidgetPosition: (position: 'left' | 'right') => {
    localStorage.setItem('unobot_widget_position', position);
    set({ widgetPosition: position });
  },

  toggleWidgetPosition: () => {
    set((state: any) => {
      const newPosition = state.widgetPosition === 'left' ? 'right' : 'left';
      localStorage.setItem('unobot_widget_position', newPosition);
      return { widgetPosition: newPosition };
    });
  },
}));
