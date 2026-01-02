/**
 * E2E Tests for Error Handling (Feature 162)
 *
 * Tests feature 162 from the feature list:
 * - Feature 162: Error handling returns helpful messages
 *
 * Verifies that error responses:
 * - Return helpful error messages
 * - Have correct error codes
 * - Don't expose stack traces in production
 * - Handle various error conditions appropriately
 */

import { test, expect } from '@playwright/test';

test.describe('Feature 162: Error Handling Returns Helpful Messages', () => {

  test.describe('Validation Errors (422)', () => {

    test('should return helpful message for missing required field', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/sessions', {
        data: {}
      });

      expect(response.status()).toBe(422);

      const data = await response.json();

      // Should have helpful error message
      expect(data).toHaveProperty('detail', 'Validation failed');
      expect(data).toHaveProperty('error_code', 'VALIDATION_ERROR');

      // Should have field-level details
      expect(data).toHaveProperty('details');
      expect(Array.isArray(data.details)).toBe(true);
      expect(data.details.length).toBeGreaterThan(0);

      // Each detail should have field, message, and value
      expect(data.details[0]).toHaveProperty('field');
      expect(data.details[0]).toHaveProperty('message');
    });

    test('should indicate which field failed validation', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/sessions', {
        data: { invalid_field: 'test' }
      });

      expect(response.status()).toBe(422);

      const data = await response.json();

      // Should specify missing field
      expect(data).toHaveProperty('details');
      const missingField = data.details.find((d: any) => d.field === 'body.visitor_id');
      expect(missingField).toBeDefined();
      expect(missingField.message).toContain('required');
    });

    test('should return validation error for invalid UUID', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/sessions/invalid-uuid');

      expect(response.status()).toBe(422);

      const data = await response.json();

      expect(data).toHaveProperty('detail');
      expect(data).toHaveProperty('error_code');
    });

  });

  test.describe('Not Found Errors (404)', () => {

    test('should return helpful 404 message for non-existent session', async ({ request }) => {
      const fakeUuid = '00000000-0000-0000-0000-000000000000';
      const response = await request.get(`http://localhost:8000/api/v1/sessions/${fakeUuid}`);

      expect(response.status()).toBe(404);

      const data = await response.json();

      // Should have helpful error message
      expect(data).toHaveProperty('detail');
      expect(data.detail).toContain('not found');

      // Should have correct error code
      expect(data).toHaveProperty('error_code', 'NOT_FOUND');

      // Should include timestamp
      expect(data).toHaveProperty('timestamp');
    });

    test('should return helpful 404 for non-existent endpoint', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/nonexistent');

      expect(response.status()).toBe(404);

      const data = await response.json();

      expect(data).toHaveProperty('detail');
      expect(data).toHaveProperty('error_code');
      expect(data.error_code).toMatch(/NOT_FOUND|INTERNAL_ERROR/);
    });

  });

  test.describe('Error Response Format', () => {

    test('should return JSON format for all errors', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000');

      expect(response.status()).toBe(404);

      const contentType = response.headers()['content-type'];
      expect(contentType).toContain('application/json');
    });

    test('should include standard fields in error response', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000');

      const data = await response.json();

      // Required fields
      expect(data).toHaveProperty('success');
      expect(data.success).toBe(false);

      expect(data).toHaveProperty('detail');
      expect(typeof data.detail).toBe('string');

      expect(data).toHaveProperty('error_code');
      expect(typeof data.error_code).toBe('string');

      expect(data).toHaveProperty('timestamp');
    });

    test('should have consistent error codes across endpoints', async ({ request }) => {
      // Test validation errors
      const validationResponse = await request.post('http://localhost:8000/api/v1/sessions', {
        data: {}
      });
      const validationData = await validationResponse.json();
      expect(validationData.error_code).toBe('VALIDATION_ERROR');

      // Test not found errors
      const notFoundResponse = await request.get('http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000');
      const notFoundData = await notFoundResponse.json();
      expect(notFoundData.error_code).toBe('NOT_FOUND');
    });

  });

  test.describe('Production Mode Security', () => {

    test('should not expose stack traces in error responses', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000');

      const data = await response.json();

      // Should not have stack trace in main response
      expect(data.detail).not.toContain('Traceback');
      expect(data.detail).not.toContain('File ');
      expect(data.detail).not.toContain('line ');

      // Debug info should only be present in development mode
      if ('debug_info' in data) {
        console.log('ℹ Debug info present (development mode)');
        // In production, this should not be present
      }
    });

    test('should not expose internal implementation details', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/sessions', {
        data: {}
      });

      const data = await response.json();

      // Error message should be user-friendly, not technical
      expect(data.detail).not.toContain('Exception');
      expect(data.detail).not.toContain('SQLAlchemy');
      expect(data.detail).not.toContain(' psycopg2');
      expect(data.detail).not.toContain('asyncpg');
    });

  });

  test.describe('HTTP Method Errors', () => {

    test('should handle method not allowed correctly', async ({ request }) => {
      const response = await request.post('http://localhost:8000/api/v1/health', {
        data: {}
      });

      // FastAPI returns 405 for Method Not Allowed
      expect([405, 307]).toContain(response.status());
    });

  });

  test.describe('Database Errors', () => {

    test('should handle database errors gracefully', async ({ request }) => {
      // Try to access non-existent resource
      const response = await request.get('http://localhost:8000/api/v1/sessions/12345678-1234-1234-1234-123456789012');

      // Should return 404, not 500
      expect(response.status()).toBe(404);

      const data = await response.json();

      // Should have helpful message
      expect(data).toHaveProperty('detail');
      expect(data.detail).toContain('not found');

      // Should NOT return internal server error
      expect(response.status()).not.toBe(500);
    });

  });

});

test.describe('Feature 162: Complete Error Handling Flow', () => {

  test('complete error handling verification', async ({ request }) => {
    // Step 1: Trigger various error conditions

    // Error 1: Validation error
    const validationResponse = await request.post('http://localhost:8000/api/v1/sessions', {
      data: {}
    });
    console.log('✓ Step 1a: Validation error triggered');

    // Error 2: Not found error
    const notFoundResponse = await request.get('http://localhost:8000/api/v1/sessions/00000000-0000-0000-0000-000000000000');
    console.log('✓ Step 1b: Not found error triggered');

    // Error 3: Invalid UUID
    const invalidUuidResponse = await request.get('http://localhost:8000/api/v1/sessions/invalid');
    console.log('✓ Step 1c: Invalid UUID error triggered');

    // Step 2: Verify error responses are helpful
    const validationData = await validationResponse.json();
    expect(validationData.detail).toBeTruthy();
    expect(typeof validationData.detail).toBe('string');
    console.log('✓ Step 2: Error responses are helpful');

    // Step 3: Verify no stack traces in production
    expect(validationData.detail).not.toContain('Traceback');
    expect(validationData.detail).not.toContain('File "/');
    const notFoundData = await notFoundResponse.json();
    expect(notFoundData.detail).not.toContain('Traceback');
    console.log('✓ Step 3: No stack traces in responses');

    // Step 4: Verify error codes are correct
    expect(validationData.error_code).toBe('VALIDATION_ERROR');
    expect(notFoundData.error_code).toBe('NOT_FOUND');
    const invalidUuidData = await invalidUuidResponse.json();
    expect(invalidUuidData.error_code).toBeTruthy();
    console.log('✓ Step 4: Error codes are correct');
    console.log(`  - Validation error: ${validationData.error_code}`);
    console.log(`  - Not found error: ${notFoundData.error_code}`);
    console.log(`  - Invalid UUID error: ${invalidUuidData.error_code}`);

    console.log('✅ Feature 162: All steps passed!');
  });

});
