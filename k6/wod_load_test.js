import { check, sleep } from "k6";
import http from "k6/http";
import { Rate } from "k6/metrics";

const errorRate = new Rate("errors");

// Get host from environment variable or default to localhost
const HOST = __ENV.HOST || "localhost";
const BASE_URL = `http://${HOST}:5000`;

const USER_EMAIL = "john.doe@mail.com";
const USER_PASSWORD = __ENV.USER_PASSWORD;

// Test configuration
export const options = {
  scenarios: {
    load_test: {
      executor: "ramping-vus",
      startVUs: 10,
      stages: [{ duration: "30s", target: 200 }],
      gracefulRampDown: "30s",
    },
  },
};

// Helper function to get auth token
function getAuthToken() {
  const loginRes = http.post(
    `${BASE_URL}/oauth/token`,
    JSON.stringify({
      email: USER_EMAIL,
      password: USER_PASSWORD,
    }),
    {
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  check(loginRes, {
    "login successful": (r) => r.status === 200,
  });

  if (loginRes.status === 200) {
    return loginRes.json().access_token;
  }
  throw new Error("Failed to get auth token");
}

// Setup code (runs once per VU)
export function setup() {
  const token = getAuthToken();
  return { token }; // Return token as part of data object
}

// Main test function
export default function (data) {
  const { token } = data; // Get token from data passed from setup

  // Get WOD
  const wodRes = http.get(`${BASE_URL}/fitness/wod`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
    tags: { type: "get_wod" },
  });

  // Check if request was successful
  const success = check(wodRes, {
    "WOD status is 200": (r) => r.status === 200,
    "WOD has exercises": (r) => r.json().exercises.length > 0,
  });

  // Record errors
  errorRate.add(!success);

  // Sleep between 1 and 3 seconds to simulate real user behavior
  sleep(Math.random() * 2 + 1);
}
