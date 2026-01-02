/**
 * E2E Tests for Health Check Endpoint (Feature 161)
 *
 * Tests feature 161 from the feature list:
 * - Feature 161: Health check endpoint returns status
 *
 * Verifies that the health check endpoint:
 * - Returns 200 status code
 * - Returns proper JSON with status information
 * - Includes database and Redis status
 */

import { test, expect } from '@playwright/test';

test.describe('Feature 161: Health Check Endpoint', () => {

  test.describe('GET /api/v1/health', () => {

    test('should return 200 status code', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');

      expect(response.status()).toBe(200);
    });

    test('should return JSON with status field', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      expect(data).toHaveProperty('status');
      expect(typeof data.status).toBe('string');
      expect(['operational', 'degraded', 'down']).toContain(data.status);
    });

    test('should include version field', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      expect(data).toHaveProperty('version');
      expect(typeof data.version).toBe('string');
    });

    test('should include timestamp field', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      expect(data).toHaveProperty('timestamp');
      expect(typeof data.timestamp).toBe('string');

      // Verify timestamp is a valid ISO date string
      const timestamp = new Date(data.timestamp);
      expect(timestamp.getTime()).toBeLessThan(Date.now() + 1000);
      expect(timestamp.getTime()).toBeGreaterThan(Date.now() - 60000); // Within last minute
    });

    test('should include database status', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      expect(data).toHaveProperty('database');
      expect(typeof data.database).toBe('string');
      expect(['healthy', 'unhealthy', 'unavailable']).toContain(data.database);
    });

    test('should include redis status', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      expect(data).toHaveProperty('redis');
      expect(typeof data.redis).toBe('string');
      expect(['healthy', 'unavailable', 'unhealthy']).toContain(data.redis);
    });

    test('should return all required fields together', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      // Verify all required fields are present
      expect(data).toMatchObject({
        status: expect.any(String),
        version: expect.any(String),
        timestamp: expect.any(String),
        database: expect.any(String),
        redis: expect.any(String),
      });

      // Verify response structure
      expect(Object.keys(data)).toContain('status');
      expect(Object.keys(data)).toContain('version');
      expect(Object.keys(data)).toContain('timestamp');
      expect(Object.keys(data)).toContain('database');
      expect(Object.keys(data)).toContain('redis');
    });

    test('should respond quickly (under 1 second)', async ({ request }) => {
      const startTime = Date.now();
      await request.get('http://localhost:8000/api/v1/health');
      const endTime = Date.now();

      const responseTime = endTime - startTime;
      expect(responseTime).toBeLessThan(1000);

      console.log(`Health check response time: ${responseTime}ms`);
    });

    test('should handle concurrent requests', async ({ request }) => {
      // Make 10 concurrent requests
      const requests = Array(10).fill(null).map(() =>
        request.get('http://localhost:8000/api/v1/health')
      );

      const responses = await Promise.all(requests);

      // All should succeed
      for (const response of responses) {
        expect(response.status()).toBe(200);
      }

      // All should have valid data
      const dataPromises = responses.map(r => r.json());
      const dataItems = await Promise.all(dataPromises);

      for (const data of dataItems) {
        expect(data).toHaveProperty('status');
        expect(data).toHaveProperty('version');
        expect(data).toHaveProperty('database');
        expect(data).toHaveProperty('redis');
      }
    });

    test('should return consistent data structure', async ({ request }) => {
      // Make multiple requests and verify structure is consistent
      const response1 = await request.get('http://localhost:8000/api/v1/health');
      const data1 = await response1.json();

      const response2 = await request.get('http://localhost:8000/api/v1/health');
      const data2 = await response2.json();

      // Should have same keys
      expect(Object.keys(data1)).toEqual(Object.keys(data2));

      // Both should have required fields
      expect(Object.keys(data1)).toContain('status');
      expect(Object.keys(data1)).toContain('version');
      expect(Object.keys(data1)).toContain('timestamp');
      expect(Object.keys(data1)).toContain('database');
      expect(Object.keys(data1)).toContain('redis');
    });

  });

  test.describe('Health Check Integration', () => {

    test('should be accessible from application root', async ({ page }) => {
      // Navigate to app
      await page.goto('http://localhost:5173');

      // Health check should still work via API
      const response = await page.request.get('http://localhost:8000/api/v1/health');
      expect(response.status()).toBe(200);
    });

    test('should reflect database connection state', async ({ request }) => {
      const response = await request.get('http://localhost:8000/api/v1/health');
      const data = await response.json();

      // Database should be healthy (we have SQLite/PostgreSQL running)
      expect(data.database).toBe('healthy');

      console.log(`Database status: ${data.database}`);
    });

  });

});

test.describe('Feature 161: Complete Health Check Flow', () => {

  test('complete health check verification', async ({ request }) => {
    // Step 1: GET /api/v1/health
    const response = await request.get('http://localhost:8000/api/v1/health');

    // Step 2: Verify 200 response
    expect(response.status()).toBe(200);
    console.log('✓ Step 1: GET request sent');
    console.log('✓ Step 2: 200 response received');

    // Step 3: Verify status JSON returned
    const contentType = response.headers()['content-type'];
    expect(contentType).toContain('application/json');
    console.log('✓ Step 3: JSON response verified');

    const data = await response.json();
    expect(data).toHaveProperty('status');

    // Step 4: Verify includes DB/Redis status
    expect(data).toHaveProperty('database');
    expect(data).toHaveProperty('redis');
    console.log('✓ Step 4: DB/Redis status included');
    console.log(`  - Status: ${data.status}`);
    console.log(`  - Database: ${data.database}`);
    console.log(`  - Redis: ${data.redis}`);
    console.log(`  - Version: ${data.version}`);

    console.log('✅ Feature 161: All steps passed!');
  });

});
