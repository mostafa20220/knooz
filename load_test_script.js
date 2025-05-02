import http from 'k6/http';
import { check, sleep, fail } from 'k6';
import { Rate } from 'k6/metrics';

// Configuration
const BASE_URL = 'https://localhost:8443';
// const BASE_URL = 'https://host.docker.internal:8443';
const EMAIL = 'locust@holouly.com';
const PASSWORD = 'passwordd';
const SHIPPING_ADDRESS = 3;
const PAYMENT_METHOD = 'CASH_ON_DELIVERY';

// Custom metrics
const errorRate = new Rate('errors');

export const options = {
  scenarios: {
    gradual_ramp: {
      executor: 'ramping-vus',
      stages: [
        { duration: '1m', target: 10 },    // Start slow
        { duration: '5m', target: 100},   // Gradually increase
        { duration: '1m', target: 0 },     // Graceful shutdown
      ],
    }
  }
};


function getRandomInt(min, max) {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function setup() {
  const loginPayload = JSON.stringify({
    email: EMAIL,
    password: PASSWORD
  });

  const params = {
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    timeout: '30s',
    http2: true,  // Correct way to enable HTTP/2
  };

  console.log(`Attempting login to ${BASE_URL}/auth/jwt/create`);

  try {
    const loginRes = http.post(
        `${BASE_URL}/auth/jwt/create`,
        loginPayload,
        params
    );

    console.log(`Login response status: ${loginRes.status}`);
    console.log(`Login response body: ${loginRes.body}`);

    const success = check(loginRes, {
      'login status is 200': (r) => r.status === 200,
      'response has access token': (r) => r.json('access') !== undefined,
    });

    if (!success) {
      fail(`Login failed: ${loginRes.status} ${loginRes.body}`);
    }

    const responseBody = JSON.parse(loginRes.body);
    return {
      token: responseBody.access,
    };
  } catch (err) {
    console.error(`Login error: ${err}`);
    fail(err);
  }
}

export default function (data) {
  if (!data || !data.token) {
    fail('No authentication token available');
    return;
  }

  // Base request parameters with HTTP/2 enabled
  const params = {
    headers: {
      'Authorization': `JWT ${data.token}`,
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Accept-Encoding': 'gzip, deflate, br'
    },
    http2: true  // Enable HTTP/2 for all requests
  };

  const addToCart = () => {
    const payload = JSON.stringify({
      product_variant: getRandomInt(1, 20),
      quantity: getRandomInt(1, 5)
    });

    try {
      const res = http.post(
          `${BASE_URL}/cart/`,
          payload,
          params
      );

      check(res, {
        'add to cart successful': (r) => r.status === 201,
      }) || errorRate.add(1);

      if (res.status !== 201) {
        console.log(`Add to cart failed: ${res.status} ${res.body}`);
      }
    } catch (err) {
      console.error(`Add to cart error: ${err}`);
      errorRate.add(1);
    }
  };

  const listOrders = () => {
    try {
      const res = http.get(
          `${BASE_URL}/orders/`,
          params
      );

      check(res, {
        'list orders successful': (r) => r.status === 200,
      }) || errorRate.add(1);

      if (res.status === 200) {
        const orders = JSON.parse(res.body);
        if (orders.results && orders.results.length > 0) {
          return orders.results[0].id;
        }
      } else {
        console.log(`List orders failed: ${res.status} ${res.body}`);
      }
    } catch (err) {
      console.error(`List orders error: ${err}`);
      errorRate.add(1);
    }
    return null;
  };

  const createOrder = () => {
    try {
      const itemCount = getRandomInt(1, 3);
      for (let i = 0; i < itemCount; i++) {
        addToCart();
      }

      const payload = JSON.stringify({
        shipping_address: SHIPPING_ADDRESS,
        payment_method: PAYMENT_METHOD,
      });

      const res = http.post(
          `${BASE_URL}/orders/`,
          payload,
          params
      );

      check(res, {
        'create order successful': (r) => r.status === 201,
      }) || errorRate.add(1);

      if (res.status === 201) {
        return JSON.parse(res.body).id;
      } else {
        console.log(`Create order failed: ${res.status} ${res.body}`);
      }
    } catch (err) {
      console.error(`Create order error: ${err}`);
      errorRate.add(1);
    }
    return null;
  };

  const confirmPayment = (orderId) => {
    if (!orderId) return;

    try {
      const payload = JSON.stringify({
        obj: {
          payment_key_claims: { extra: { order_id: orderId } },
          success: true,
          is_voided: false,
          is_refunded: false,
        }
      });

      const hmac_signature = 'fake_hmac_signature';
      const res = http.post(
          `${BASE_URL}/orders/confirm-payment/?hmac=${hmac_signature}`,
          payload,
          params
      );

      check(res, {
        'confirm payment successful': (r) => r.status === 200,
      }) || errorRate.add(1);
    } catch (err) {
      console.error(`Confirm payment error: ${err}`);
      errorRate.add(1);
    }
  };

  try {
    const scenario = Math.random();
    // if (scenario < 0.7) {
    //   const orderId = createOrder();
    //   if (orderId) {
    //     console.log(`Successfully created order: ${orderId}`);
    //     if (Math.random() < 0.5) {
    //       confirmPayment(orderId);
    //     }
    //   }
    // } else {
      const orderId = listOrders();
      if (orderId) {
        console.log(`Successfully retrieved order: ${orderId}`);
      }
    // }
  } catch (err) {
    console.error(`Scenario execution error: ${err}`);
    errorRate.add(1);
  }

  sleep(Math.random() * 2 + 1);
}
