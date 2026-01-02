# Session Resume via Email Link - E2E Test Suite

## Overview

This document provides comprehensive information about the session resume via email link functionality and its corresponding E2E test suite for the UnoBot chat application.

## Feature Description

The session resume via email link functionality allows users to:

1. **Start a conversation** with the chat widget
2. **Receive a session ID** automatically generated and stored in localStorage
3. **Generate a resume URL** with the session ID as a URL parameter
4. **Resume the conversation** by clicking the email link, which preserves:
   - Complete conversation history
   - Session context (phase, client info, business context)
   - Ability to continue the conversation
   - All session data integrity

## URL Format

The resume URL follows this format:
```
http://localhost:5173?session_id=SESSION_ID_HERE
```

## Test Suite Structure

### Test Files

- **Main Test File**: `/tests/e2e/test_session_resume_email.py`
- **Test Runner**: `/tests/e2e/test_session_resume_runner.py`
- **Configuration**: `/tests/e2e/conftest.py`

### Test Environment

- **Frontend URL**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **Browser**: Chromium (headless)
- **Viewport**: 1280x720
- **Timeout**: 5 minutes per test
- **Framework**: Playwright + Pytest

## Individual Test Cases

### 1. `test_session_resume_via_email_link`
**Purpose**: Basic session resume functionality test

**Test Steps**:
1. Navigate to main page (http://localhost:5173)
2. Open chat widget and start conversation
3. Send test messages to create conversation history
4. Get session ID from localStorage
5. Generate resume URL with session ID
6. Close browser (simulate user action)
7. Open resume URL in fresh browser session
8. Verify session ID is preserved
9. Verify conversation history is intact

**Assertions**:
- Session ID remains the same after resume
- Conversation history contains original messages
- User can continue the conversation

---

### 2. `test_session_resume_preserves_conversation_history`
**Purpose**: Comprehensive conversation history preservation

**Test Steps**:
1. Create detailed conversation with multiple messages
2. Record initial conversation state
3. Resume session via email link
4. Compare message counts and content
5. Verify both user and bot messages are preserved

**Assertions**:
- Exact message count preservation
- Specific user message content preservation
- Bot response preservation
- Message order integrity

---

### 3. `test_session_resume_preserves_session_context`
**Purpose**: Verify session context preservation

**Test Steps**:
1. Create conversation with context-establishing messages
2. Send client information (name, company, industry)
3. Send business requirements
4. Resume session via email link
5. Verify context information is preserved

**Assertions**:
- Client information preserved in conversation
- Business context maintained
- Session phase information retained
- User identity information preserved

---

### 4. `test_session_resume_with_empty_conversation`
**Purpose**: Test minimal conversation scenario

**Test Steps**:
1. Create session with only welcome message
2. Resume session via email link
3. Verify minimal history is preserved

**Assertions**:
- Welcome message preserved
- Message count consistency
- Session ID preservation

---

### 5. `test_session_resume_url_generation`
**Purpose**: Verify resume URL generation functionality

**Test Steps**:
1. Create session and generate resume URL
2. Verify URL format and parameters
3. Test URL functionality
4. Verify session resumption via generated URL

**Assertions**:
- URL contains correct session_id parameter
- URL uses current origin domain
- URL functionality verified
- Session properly resumed

---

### 6. `test_session_resume_multiple_times`
**Purpose**: Test multiple resume scenarios

**Test Steps**:
1. Create initial session with conversation
2. Resume session multiple times (3 times)
3. Verify consistency across all resume attempts
4. Check conversation history consistency

**Assertions**:
- Multiple resume attempts successful
- Conversation history consistent across resumes
- Session data integrity maintained
- No data corruption or loss

---

### 7. `test_session_resume_chat_widget_behavior`
**Purpose**: Verify chat widget behavior after resume

**Test Steps**:
1. Create session and close chat widget
2. Resume session via email link
3. Test chat widget behavior
4. Verify ability to send new messages

**Assertions**:
- Chat widget closed initially after resume
- Chat opens correctly on button click
- Conversation visible after opening
- New messages can be sent
- Session continuity maintained

---

### 8. `test_session_resume_url_parameter_handling`
**Purpose**: Test URL parameter processing

**Test Steps**:
1. Navigate to URL with test session ID parameter
2. Verify session ID stored in localStorage
3. Test parameter parsing

**Assertions**:
- URL parameter correctly parsed
- Session ID stored in localStorage
- Parameter handling robust

---

### 9. `test_session_resume_without_parameter`
**Purpose**: Test normal session creation without parameters

**Test Steps**:
1. Navigate to root URL without session_id parameter
2. Verify no session exists initially
3. Open chat to create new session
4. Verify normal session creation

**Assertions**:
- No session exists without parameter
- New session created when chat opened
- Normal flow preserved

## Key Test Components

### Browser Automation
- **Page Navigation**: Navigate to URLs and wait for load
- **Widget Interaction**: Click chat buttons and interact with UI
- **Message Handling**: Type messages and verify responses
- **Storage Verification**: Check localStorage for session data

### Session Management
- **Session ID Tracking**: Monitor session ID creation and preservation
- **Conversation History**: Track message count and content
- **Context Preservation**: Verify session state maintenance
- **URL Generation**: Test resume URL creation and functionality

### Error Handling
- **Network Failures**: Handle API timeouts and errors
- **Session Expiry**: Test expired or invalid session handling
- **Browser Issues**: Handle browser automation errors
- **State Inconsistency**: Detect session data corruption

## Test Execution

### Prerequisites
1. Backend API running on localhost:8000
2. Frontend application running on localhost:5173
3. Database migrations applied
4. Required dependencies installed

### Running Tests

```bash
# Run all session resume tests
python tests/e2e/test_session_resume_runner.py

# Run specific test
pytest tests/e2e/test_session_resume_email.py::test_session_resume_via_email_link -v

# Run with browser visible (for debugging)
pytest tests/e2e/test_session_resume_email.py -v --headed
```

### Expected Output
The test runner provides:
- Real-time test execution progress
- Detailed pass/fail status
- Summary statistics and success rate
- Technical recommendations
- Detailed error information for failures

## Test Data and Scenarios

### Test Messages
- "Hi, I need help with a business consultation"
- "Can you tell me about your services?"
- "Hello, I'm interested in AI consulting services"
- "My name is John Smith"
- "I work at Acme Corp in the healthcare industry"

### Session States Tested
- **New Session**: Fresh session creation
- **Active Session**: Session with ongoing conversation
- **Resumed Session**: Session restored from email link
- **Multiple Resumes**: Same session resumed multiple times

### Edge Cases
- Empty conversation history
- Long conversation history
- Session with complex context
- Multiple browser sessions

## Integration Points

### Frontend Components
- **ChatWidget**: Main widget component
- **ChatWindow**: Chat interface
- **useChatStore**: Zustand store for session management
- **URL Parameter Handling**: App.tsx parameter processing

### Backend API
- **Session Creation**: POST /api/v1/sessions
- **Session Resume**: POST /api/v1/sessions/{session_id}/resume
- **Message Handling**: POST /api/v1/sessions/{session_id}/messages
- **Session Retrieval**: GET /api/v1/sessions/{session_id}

### Database
- **Session Storage**: ConversationSession table
- **Message Storage**: Message table
- **State Persistence**: Session state and context

## Troubleshooting

### Common Issues
1. **Backend Not Running**: Ensure API server is running on localhost:8000
2. **Frontend Not Running**: Ensure development server is running on localhost:5173
3. **Database Issues**: Run migrations and ensure database is accessible
4. **Browser Issues**: Install browser dependencies via `playwright install`

### Debug Tips
- Use `--headed` flag to see browser during tests
- Check console logs for API errors
- Verify localStorage content manually
- Test URL generation manually in browser

## Performance Considerations

### Test Optimization
- Parallel test execution
- Efficient browser reuse
- Minimal test overhead
- Timeout management

### Real-world Scenarios
- Multiple concurrent sessions
- Large conversation histories
- Network latency simulation
- Browser compatibility testing

## Future Enhancements

### Additional Test Cases
- Cross-browser compatibility
- Mobile responsive testing
- Session expiry and cleanup
- Performance under load

### Monitoring Integration
- Test result reporting
- Performance metrics
- Automated regression detection
- Continuous integration setup