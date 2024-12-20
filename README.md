
# Knooz Project
Welcome to **Knooz**, an e-commerce platform built using Django, offering a seamless shopping experience with robust features for customers, sellers, and administrators.
This README provides an overview of the project, its features, and the technical implementation.

---

[//]: # (map of the project)
## Table of Contents

- [Features](#features)
- [Installation and Setup](#installation-and-setup)
- [Project Structure](#project-structure)
- [License](#license)
- [Contact](#contact)

---

## Features

### Authentication and User Management

- **JWT Authentication**: Secure token-based authentication for all users.
- **Social Media Login**: Google OAuth integration for easy account creation and login.
- **Password Management**:
  - Reset Password.
  - Forgot Password.
- **Email Verification**: New account verification via email.
- **User Profile**: Users can view and update their profile information.

### Product Management

- **View Products**:
  - Filters: Filter products by ID, category, price range, colors, brands, etc.
  - Search: Search for products by name with additional filters.
- **Product Variants**: Support for product variants such as sizes, colors, and variant-specific pricing.
- **CRUD for Cart**: Add, update, delete, and view items in the cart.
- **Product Reviews**: Customers can leave reviews for purchased products.
- **Wish list**: Customers can maintain a list of desired products.

### User Roles

1. **Customer**:
   - Manage carts.
   - Place and view order history with detailed status.
   - Cancel orders (if not shipped).
   - Manage multiple shipping addresses.
   - Review products.
2. **Seller**:
   - Add new products.
   - Update product data and quantity.
3. **Admin**:
   - Manage brands, categories, coupon codes, colors, etc.
   - Access and control most resources via Django Admin (enhanced with Jazzmin).

### Coupons

- **Global or Specific**: Coupons can apply to all products or specific categories.
- **Flexible Settings**:
  - Minimum order value.
  - Maximum discount amount and percentage.
  - Start and end date for validity.
  - General usage limit and per-user usage limit.
- **Deactivation**: Admins can deactivate coupons via the dashboard.

### Payment and Orders

- **Payment Gateways**:
  - Integration with Paymob for online payments.
  - Support for Cash on Delivery (COD).
- **Order Management**:
  - View order history.
  - Auto cancellation and restocking of unpaid orders after 1 hour using Celery and Celery Beat.
  - Status updates via email (e.g., placed, in shipping, delivered, cancelled, returned).

### Notifications and Emails

- Automated email notifications for:
  - Registration and account verification.
  - Login alerts.
  - Password resets and forgotten passwords.
  - Order placement, cancellations, and status updates.
  - Warnings for unpaid orders nearing cancellation.

### Infrastructure and Tools

- **Nginx**: Reverse proxy and static/media file server.
- **Ngrok**: Provides an HTTPS static link for Paymob integration.
- **PostgreSQL**: Primary database running in a Docker container.
- **Redis**: Message broker for Celery tasks.
- **Celery Worker**: Executes offloaded tasks like emails and scheduled jobs.
- **Celery Beat**: Schedules periodic tasks such as auto-canceling unpaid orders.
- **Silk**: Tracks and analyzes database queries and requests.
- **Docker Compose**: Manages containers and services.

---

## Installation and Setup


1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mostafa20220/knooz.git
   cd knooz
   ```

2. **Set Up Environment Variables**.
   - Create a `.env` file in the project root.
   - Add the following environment variables:
     ```env 
     JWT_ACCESS_EXPIRES_IN_MINUTES=
     JWT_REFRESH_EXPIRES_IN_DAYS=
     
     DEBUG=
     SECRET_KEY=
     CSRF_TRUSTED_ORIGINS=
     ALLOWED_HOSTS=

     SQL_DATABASE=
     SQL_USER=
     SQL_PASSWORD=
     SQL_HOST=
     SQL_PORT=
 
     PAYMOB_API_KEY=
     PAYMOB_SECRET_KEY=
     PAYMOB_PUBLIC_KEY=
     PAYMOB_PAYMENT_METHODS_IDS=
 
     NGROK_AUTHTOKEN=
     NGROK_STATIC_DOMAIN=
       ```

3. **Run Docker Compose**:

   ```bash
   docker-compose up --build
   ```

4. **Apply Migrations**:

   ```bash
   docker-compose exec -it django python manage.py migrate
   ```

5. **Create Superuser**:

   ```bash
   docker-compose exec -it django python manage.py createsuperuser
   ```

6. **Access the Application**:

   - Web App: [http://localhost:8080](http://localhost:8080)
   - Pg Admin: [http://localhost:5434](http://localhost:5434)
   - Admin Dashboard: [http://localhost:8080/admin](http://localhost:8080/admin)
   - Silk Dashboard: [http://localhost:8080/silk](http://localhost:8080/silk)

---

## Project Structure

```
knooz/
├── carts/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   ├── views.py
│   └── migrations/
├── core/
│   ├── asgi.py
│   ├── celery.py
│   ├── constants.py
│   ├── permissions.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── coupons/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── orders/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── products/
│   ├── admin.py
│   ├── apps.py
│   ├── filters.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── reviews/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── users/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── wishlists/
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── manage.py
├── requirements.txt
├── docker-compose.yaml
├── Dockerfile
└── media/
    └── product_images/
        └── ...
```

---

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.

---

## Contact

For questions or suggestions, please contact the project maintainer at 
- Email: [mostafa.hesham.cs@gmail.com](mostafa.hesham.cs@gmail.com)
- LinkedIn: [linkedin.com/in/mostafa--hesham/](https://www.linkedin.com/in/mostafa--hesham/)



