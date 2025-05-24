# Flask Auth0 Integration App

This is a simple Flask web app demonstrating authentication using Auth0. It includes:

- Login with Auth0
- Protected route `/protected` that only authenticated users can access
- Logout functionality

---

## Demo

[Watch 5-minute demo on YouTube](https://youtu.be/wI68S55YwgA)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/dejalltime/Lab-1-Auth0.git
cd Lab-1-Auth0
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Auth0

- Go to [Auth0 Dashboard](https://manage.auth0.com/)
- Create a new application
- Set the following:
  - **Application Type**: Regular Web App
  - **Allowed Callback URLs**: `http://localhost:3000/callback, http://127.0.0.1:3000/callback`
  - **Allowed Logout URLs**: `http://localhost:3000, http://127.0.0.1:3000/`

---

## Environment Variables

Create a `.env` file in the root directory:

```env
AUTH0_CLIENT_ID=your-auth0-client-id
AUTH0_CLIENT_SECRET=your-auth0-client-secret
AUTH0_DOMAIN=your-auth0-domain.auth0.com
APP_SECRET_KEY=your-secret-session-key
PORT=3000
```

---

## Run the App Locally

```bash
python server.py
```

Then visit:
```
http://localhost:3000
```

---

## 🔐 Routes

| Route        | Description                      |
|--------------|----------------------------------|
| `/`          | Home page                        |
| `/login`     | Redirects to Auth0 login         |
| `/callback`  | Handles Auth0 redirect           |
| `/protected` | Protected route (requires login) |
| `/logout`    | Logs out and redirects to `/`    |

---

## What I Learned

- How to integrate Auth0 with a Python Flask application
- How to handle authentication tokens and sessions securely
- The importance of managing redirect URIs and OAuth flows
