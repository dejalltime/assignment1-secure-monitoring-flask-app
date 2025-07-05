import json
import logging
from os import environ as env
from urllib.parse import quote_plus, urlencode
from datetime import datetime

from authlib.integrations.flask_client import OAuth
from dotenv import find_dotenv, load_dotenv
from flask import Flask, redirect, render_template, session, url_for, request, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix

# Load .env
ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)

# Initialize Flask
app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# Secure the session cookie
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_SAMESITE='Lax'
)

app.secret_key = env.get("APP_SECRET_KEY")

# Configure structured logging
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter(
    '{"time":"%(asctime)s","level":"%(levelname)s","message":"%(message)s"}'
))
app.logger.setLevel(logging.INFO)
app.logger.addHandler(handler)

# OAuth setup
oauth = OAuth(app)
oauth.register(
    "auth0",
    client_id=env.get("AUTH0_CLIENT_ID"),
    client_secret=env.get("AUTH0_CLIENT_SECRET"),
    client_kwargs={"scope": "openid profile email"},
    server_metadata_url=f'https://{env.get("AUTH0_DOMAIN")}/.well-known/openid-configuration'
)

# Home route
@app.route("/")
def home():
    return render_template(
        "home.html",
        session=session.get('user'),
        pretty=json.dumps(session.get('user'), indent=4)
    )

# Login route
@app.route("/login")
def login():
    redirect_to = url_for("callback", _external=True)
    app.logger.info(f"Auth0 redirect_uri → {redirect_to}")
    return oauth.auth0.authorize_redirect(redirect_uri=redirect_to)

# Callback route
@app.route("/callback", methods=["GET", "POST"])
def callback():
    token = oauth.auth0.authorize_access_token()
    userinfo = oauth.auth0.userinfo(token=token)
    session["user"] = userinfo
    # Log successful login
    app.logger.info(f'login: {{"user_id":"{userinfo.get("sub")}","email":"{userinfo.get("email")}","timestamp":"{datetime.utcnow().isoformat()}"}}')
    return redirect(url_for("protected"))

# Authorization decorator
def requires_auth(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user' not in session:
            # Log unauthorized attempt
            app.logger.warning(f'unauthorized_attempt: {{"path":"{request.path}","timestamp":"{datetime.utcnow().isoformat()}"}}')
            return redirect(url_for("home"))
        return f(*args, **kwargs)
    return decorated

# Protected route
@app.route("/protected")
@requires_auth
def protected():
    user = session.get("user")
    # Log access to protected endpoint
    app.logger.info(f'protected_access: {{"user_id":"{user.get("sub")}","email":"{user.get("email")}","timestamp":"{datetime.utcnow().isoformat()}"}}')
    return render_template(
        "protected.html",
        session=user,
        pretty=json.dumps(user, indent=4)
    )

# Logout route
@app.route("/logout")
def logout():
    session.clear()
    return redirect(
        f'https://{env.get("AUTH0_DOMAIN")}/v2/logout?' + urlencode({
            "returnTo": url_for("home", _external=True),
            "client_id": env.get("AUTH0_CLIENT_ID")
        }, quote_via=quote_plus)
    )

# Health endpoint
@app.route("/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(env.get("PORT", 3000)))