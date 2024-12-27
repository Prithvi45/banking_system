# Banking System with REST API

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
python manage.py migrate
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

