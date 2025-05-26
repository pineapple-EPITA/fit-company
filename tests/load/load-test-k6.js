import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 5 },
    { duration: '1m', target: 5 },
    { duration: '30s', target: 0 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],
    http_req_failed: ['rate<0.01'],
  },
};

const token = __ENV.ACCESS_TOKEN?.trim();

export default function () {
  const url = 'http://127.0.0.1:5055/fitness/wod';

  const params = {
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
  };

  const res = http.get(url, params);

  console.log('STATUS:', res.status);
  console.log('BODY:', res.body);

  check(res, {
    'status is 200': (r) => r.status === 200,
    'response has exercises': (r) => r.body && r.body.includes('exercises'),
  });

  sleep(1);
}