import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend } from 'k6/metrics';

// Custom metrics
const errorRate = new Rate('errors');
const wodGenerationTime = new Trend('wod_generation_time');

export const options = {
  stages: [
    // Ramp up to 50 users over 1 minute
    { duration: '1m', target: 50 },
    // Stay at 50 users for 2 minutes
    { duration: '2m', target: 50 },
    // Ramp up to 100 users over 1 minute
    { duration: '1m', target: 100 },
    // Stay at 100 users for 2 minutes
    { duration: '2m', target: 100 },
    // Ramp down to 0 users over 1 minute
    { duration: '1m', target: 0 },
  ],
  thresholds: {
    'http_req_duration': ['p(95)<5000'], // 95% of requests should be below 5s
    'errors': ['rate<0.01'], // Error rate should be below 1%
    'wod_generation_time': ['p(95)<5000'], // 95% of WOD generations should be below 5s
  },
};

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8080';
const token = __ENV.ACCESS_TOKEN?.trim();

export default function () {
  const url = `${BASE_URL}/fitness/wod`;
  const params = {
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const startTime = new Date();
  const res = http.get(url, params);
  const endTime = new Date();
  
  // Record WOD generation time
  wodGenerationTime.add(endTime - startTime);

  // Log response details for debugging
  console.log(`Response time: ${res.timings.duration}ms`);
  console.log(`Status: ${res.status}`);
  
  const checks = check(res, {
    'status is 200': (r) => r.status === 200,
    'response has exercises': (r) => {
      try {
        const body = JSON.parse(r.body);
        return body && body.exercises && Array.isArray(body.exercises);
      } catch (e) {
        return false;
      }
    },
    'response time OK': (r) => r.timings.duration < 5000,
  });

  errorRate.add(!checks);

  // Add a random sleep between 1-3 seconds to simulate real user behavior
  sleep(Math.random() * 2 + 1);
}