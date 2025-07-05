# Secure Monitoring Flask App

This repository contains a Flask application integrated with Auth0 for authentication and structured logging to Azure Log Analytics. It demonstrates:

- **SSO with Auth0** for secure user login
- **Protected routes** with access control
- **Structured logging** of key events (logins, protected route access, unauthorized attempts)
- **Azure App Service** deployment
- **Azure Monitor + KQL** for detecting excessive access activity
- **Alerting** when thresholds are exceeded

---

## Demo Video

A walkthrough of the deployed app, log generation, KQL queries, and alert setup:

[Watch on YouTube](https://youtu.be/MpbIgoLpjzQ)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/dejalltime/assignment1-secure-monitoring-flask-app.git
cd assignment1-secure-monitoring-flask-app
```

### 2. Create & Activate Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate    # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
# Then edit .env:
# APP_SECRET_KEY=your_flask_secret_key
# AUTH0_CLIENT_ID=...
# AUTH0_CLIENT_SECRET=...
# AUTH0_DOMAIN=your-auth0-domain.auth0.com
# PORT=3000
```

---

## Running Locally

```bash
python server.py
```

Navigate to `http://localhost:3000` in your browser.

### Available Routes

| Route        | Method | Description                                |
|--------------|--------|--------------------------------------------|
| `/`          | GET    | Home page                                  |
| `/login`     | GET    | Redirects to Auth0 for login               |
| `/callback`  | GET    | Auth0 callback handler                     |
| `/protected` | GET    | Protected route (requires logged-in user)  |
| `/logout`    | GET    | Logs out and returns to home               |
| `/health`    | GET    | Health check endpoint                      |

---

## Structured Logging

The app logs three key events to stdout (streamed to Azure Log Analytics):

1. **Login**
   ```json
   {"time":"...","level":"INFO","message":"login: {"user_id":"...","email":"...","timestamp":"..."}"}
   ```
2. **Protected Route Access**
   ```json
   {"time":"...","level":"INFO","message":"protected_access: {"user_id":"...","email":"...","timestamp":"..."}"}
   ```
3. **Unauthorized Attempt**
   ```json
   {"time":"...","level":"WARNING","message":"unauthorized_attempt: {"path":"/protected","timestamp":"..."}"}
   ```

These logs are routed to Azure via **AppServiceConsoleLogs**.

---

## Monitoring & Detection

### KQL Query for Excessive Access

```kql
AppServiceConsoleLogs
| where TimeGenerated > ago(1h)
| where ResultDescription has "protected_access"
// non-greedy capture of the first {…}
| extend rawPayload = extract(@"protected_access: (\{.*?\})", 1, ResultDescription, typeof(string))
| where isnotempty(rawPayload)
// now rawPayload is exactly {"user_id":…,"email":…,"timestamp":…}
| extend payload = parse_json(rawPayload)
// aggregate per user
| summarize
    Count     = count(),
    FirstSeen = min(TimeGenerated),
    LastSeen  = max(TimeGenerated)
    by UserID = tostring(payload.user_id)
| where Count > 10
| project UserID, Count, FirstSeen, LastSeen
| render table
```

### Alert Rule

- **Scope**: Log Analytics Workspace
- **Condition**: Custom log search (above KQL) > 0 results
- **Frequency**: every 5 minutes over a 15-minute window
- **Action**: Email notification via Action Group
- **Severity**: 3 (Low)

---

## Next Steps & Improvements

- Add user-agent and IP logging for richer context
- Implement rate-limiting or IP blocking on excessive failures
- Expand KQL to detect other suspicious patterns