# Banking System with Django REST API

This project is a comprehensive banking application built using Django Rest Framework (DRF). It provides features like user registration, role-based access control, external fund transfers, Currency exchange, Multitenant, Multiple timezone support  and reporting for admins.

---

## Features
- User Registration and Login with Two-Factor Authentication (2FA)
- Multiple Bank Accounts per User and Multitenant
- Transactions: Deposit, Withdrawal, Transfer
- Multi-Currency Support with Real-Time Conversion Rates
- Dynamic Roles and Permissions
- Admin Reporting Dashboard
- Security Features: CSRF Protection, Rate Limiting, HTTPS Support
- Pagination, Optimization, Redis Cache 

---

## Setup Instructions

### Prerequisites
1. Python 3.12
2. Redis (for caching)
3. Ubuntu 24.04 

---

### Step 1: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  

```


### Step 2: Clone the Repository
```bash
cd 
git clone https://github.com/Prithvi45/banking_system.git
cd banking_system
```

### Step 3: Install Dependencies
``` bash
pip install -r requirements.txt
```

### Step 4: Set Up Database
Ignore if you are using exiting SQLITE DB from repository (I have added dummy data to test application)
``` bash
python manage.py makemigrations
python manage.py migrate --fake 
```

### Step 5: Set Up Environment Vairables
create a .env file or use global env file at /etc/environment
``` bash
SECRET_KEY=your_secret_key
SENDGRID_API_KEY = sendgrid_api_key
```

### Step 6: Start the Developmenr server 
``` bash
python manage.py runserver (for local system)

or python manage.py runserver 0.0.0.0:8000 (for AWS EC2 instance)
```
Access the application at http://127.0.0.1:8000 or http://your-public-id:8000

### Step 7: Run Tests
``` bash
python manage.py test accounts
```






## Security Features

1. **Two-Factor Authentication (2FA):**
   - OTP-based authentication via email ensures secure logins
   - Generated OTP with expiry via Sendgrid API

2. **CSRF Protection:**
   - Enabled by default for all API views requiring session-based authentication.

3. **Secure Password Storage:**
   - Uses Django’s PBKDF2 password hashing with a salt.
   - By using set_password method

4. **Rate Limiting:**
   - Configured to limit requests and prevent abuse (e.g., brute force attacks):
     ```python
     REST_FRAMEWORK = {
         'DEFAULT_THROTTLE_CLASSES': [
             'rest_framework.throttling.AnonRateThrottle',
             'rest_framework.throttling.UserRateThrottle',
         ],
         'DEFAULT_THROTTLE_RATES': {
             'anon': '10/min',
             'user': '100/min',
         },
     }
     ```

5. **HTTPS Support:**
   - Enforced via `SECURE_SSL_REDIRECT` and other secure cookie settings:
     ```python
     SECURE_SSL_REDIRECT = True
     SESSION_COOKIE_SECURE = True
     CSRF_COOKIE_SECURE = True
     SECURE_HSTS_SECONDS = 3600
     ```

6. **HTTP Security Headers:**
   - Prevents clickjacking, XSS, and other attacks:
     ```python
     SECURE_BROWSER_XSS_FILTER = True
     SECURE_CONTENT_TYPE_NOSNIFF = True
     X_FRAME_OPTIONS = 'DENY'
     ```

---

## Performance Optimization

1. **Caching:**
   - Redis-based caching for frequently accessed data (e.g., transaction history):
     ```python
     CACHES = {
         'default': {
             'BACKEND': 'django_redis.cache.RedisCache',
             'LOCATION': 'redis://127.0.0.1:6379/1',
             'OPTIONS': {
                 'CLIENT_CLASS': 'django_redis.client.DefaultClient',
             }
         }
     }
     ```

2. **Optimized Database Queries:**
   - Use of `select_related` and `prefetch_related` to minimize database hits.
   - Example:
     ```python
     Transaction.objects.select_related('account', 'related_account').filter(account__user=request.user)
     ```

3. **Pagination for Large Data:**
   - Paginated endpoints to handle large datasets efficiently:
     ```python
     REST_FRAMEWORK = {
         'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
         'PAGE_SIZE': 10,
     }
     ```

4. **Indexing:**
   - Indexed frequently queried fields like `account_number` in the `BankAccount` model.



## API Documentation
Refer to the `docs` folder for detailed API specifications.

Alternatively, access:
- Swagger UI: `http://127.0.0.1:8000/api/accounts/docs/#/` (in your local server)

---

