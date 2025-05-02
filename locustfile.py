import random
from locust import FastHttpUser, TaskSet, task, between, tag

from core.constants import CASH_ON_DELIVERY

EMAIL="locust@holouly.com"
PASSWORD="passwordd"
SHIPPING_ADDRESS= 3
PAYMENT_METHOD= CASH_ON_DELIVERY

class OrdersTasks(TaskSet):
    def on_start(self):
        """
        Run at the start of the test. It logs in a user and stores the token for authenticated requests.
        """


        # self.client = httpx.Client(http2=True, verify=False, base_url=self.user.host)
        self.token = self.login()

    def login(self):
        """
        Log in as a user and retrieve the authentication token.
        """
        response = self.client.post(
            "/auth/jwt/create",
            json={"email": EMAIL, "password": PASSWORD},
        )
        if response.status_code == 200:
            return response.json().get("access")

        else:
            print("Error logging in")
            print(response.json())
            self.interrupt(reschedule=False)  # Stop the user

        return None

    def auth_headers(self):
        """
        Generate headers with the authentication token.
        """
        return {"Authorization": f"JWT {self.token}"}

    def add_to_cart(self):
        """
        Add random products to the user's cart.
        """
        response = self.client.post(
            "/cart/",
            headers=self.auth_headers(),
            json={"product_variant": random.randint(1, 20), "quantity": random.randint(1, 5)},
        )
        if response.status_code == 201:
            print("Product added to cart successfully")
        else:
            print("Error adding product to cart")
            print(response.json())

    @tag("list")
    @task
    def list_orders(self):
        """
        Test the orders listing API.
        """
        response = self.client.get("/orders/", headers=self.auth_headers(),)
        if response.status_code == 200:
            orders = response.json()
            if orders:
                self.order_id = orders.get("results")[0]["id"]  # Store an order ID for other tests.
                print(f"{len(orders)} Orders listed successfully")

            else:
                print("Error listing orders")
                print(response.json())

    @tag("create")
    @task
    def create_order(self):
        """
        Test the orders creation API.
        """

        # add items to cart
        for i in range(random.randint(1, 10)):
            self.add_to_cart()

        payload = {
            "shipping_address": SHIPPING_ADDRESS,
            "payment_method": PAYMENT_METHOD,
        }
        response = self.client.post(
            "/orders/", headers=self.auth_headers(),
            json=payload,
        )
        if response.status_code == 201:
            print("Order created successfully")
        else:
            print("Error creating order")
            print(response.json())

    @task
    def cancel_order(self):
        """
        Test the order cancellation API.
        """
        if hasattr(self, "order_id"):
            response = self.client.post(
                f"/orders/{self.order_id}/cancel/", headers=self.auth_headers())
            if response.status_code == 200:
                print("Order cancelled successfully")

    @task
    def return_order(self):
        """
        Test the order return API.
        """
        if hasattr(self, "order_id"):
            response = self.client.post(
                f"/orders/{self.order_id}/return/", headers=self.auth_headers())
            if response.status_code == 200:
                print("Order returned successfully")

    @task
    def confirm_payment(self):
        """
        Test the payment confirmation API.
        """
        payload = {
            "obj": {
                "payment_key_claims": {"extra": {"order_id": self.order_id}},
                "success": True,
                "is_voided": False,
                "is_refunded": False,
            }
        }
        hmac_signature = "fake_hmac_signature"  # Replace with an actual HMAC if needed.
        response = self.client.post(
            f"/orders/confirm-payment/?hmac={hmac_signature}",
            headers=self.auth_headers(),
            json=payload,
        )
        if response.status_code == 200:
            print("Payment confirmed successfully")


class OrdersUser(FastHttpUser):
    tasks = [OrdersTasks]
    host = "https://localhost:8443"
    # wait_time = between(0, 1)  # Wait between 1 and 3 seconds between tasks
