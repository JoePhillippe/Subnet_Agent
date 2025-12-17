"""
═══════════════════════════════════════════════════════════════════════
    NETWORKING TUTOR SUITE - MAIN APP FOR RENDER
═══════════════════════════════════════════════════════════════════════

Main Flask application that registers all agent blueprints.

LOGIN: Student12345 / 12345FTCC!@#$%

Deploy to Render:
  1. Upload all files to GitHub
  2. Set ANTHROPIC_API_KEY in Render environment variables
  3. Build: pip install -r requirements.txt
  4. Start: python app.py

═══════════════════════════════════════════════════════════════════════
"""

from flask import Flask, render_template_string, request, session, redirect, url_for
from functools import wraps
import os
import secrets

# Import agent blueprints
from agent1_blueprint import agent1_bp
from agent2_blueprint import agent2_bp
from agent3_blueprint import agent3_bp
from agent4_blueprint import agent4_bp

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# Initialize Anthropic client (shared by all agents)
from anthropic import Anthropic
client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Authentication
USERNAME = "Student12345"
PASSWORD = "12345FTCC!@#$%"

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Register blueprints
app.register_blueprint(agent1_bp, url_prefix='/agent1')
app.register_blueprint(agent2_bp, url_prefix='/agent2')
app.register_blueprint(agent3_bp, url_prefix='/agent3')
app.register_blueprint(agent4_bp, url_prefix='/agent4')

#═══════════════════════════════════════════════════════════════════════
# LOGIN & MENU
#═══════════════════════════════════════════════════════════════════════

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Login - Networking Tutor</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .login-box {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            width: 400px;
        }
        .login-box h1 { text-align: center; color: #667eea; margin-bottom: 30px; }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 5px; font-weight: bold; }
        .form-group input {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 1em;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
        }
        .error { color: #d32f2f; margin-bottom: 15px; text-align: center; }
    </style>
</head>
<body>
    <div class="login-box">
        <h1>🌐 Network Tutor Login</h1>
        {% if error %}<div class="error">{{ error }}</div>{% endif %}
        <form method="POST">
            <div class="form-group">
                <label>Username</label>
                <input type="text" name="username" required autofocus>
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required>
            </div>
            <button type="submit" class="btn">Login</button>
        </form>
    </div>
</body>
</html>
"""

MENU_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Networking Tutor Suite</title>
    <meta charset="utf-8">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: white;
            padding: 40px;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            position: relative;
        }
        .header h1 { color: #667eea; font-size: 2.5em; margin-bottom: 10px; }
        .logout {
            position: absolute;
            top: 20px;
            right: 20px;
            padding: 8px 16px;
            background: #f44336;
            color: white;
            text-decoration: none;
            border-radius: 6px;
            font-weight: bold;
        }
        .agents {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 25px;
        }
        .agent-card {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            text-decoration: none;
            color: inherit;
            transition: transform 0.3s;
        }
        .agent-card:hover { transform: translateY(-5px); }
        .agent-num {
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            font-weight: bold;
            margin-bottom: 15px;
        }
        .agent-title { font-size: 1.4em; font-weight: bold; margin-bottom: 10px; }
        .agent-desc { color: #666; line-height: 1.6; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="{{ url_for('logout') }}" class="logout">Logout</a>
            <h1>🌐 Networking Tutor Suite</h1>
            <p>Master Subnetting with AI-Powered Tutoring</p>
        </div>
        <div class="agents">
            <a href="{{ url_for('agent1.home') }}" class="agent-card">
                <div class="agent-num">1</div>
                <div class="agent-title">Basic Subnetting</div>
                <div class="agent-desc">Binary conversion, IP classes, fundamental subnetting. 80 questions across 8 topics.</div>
            </a>
            <a href="{{ url_for('agent2.home') }}" class="agent-card">
                <div class="agent-num">2</div>
                <div class="agent-title">Custom Subnet Masks</div>
                <div class="agent-desc">Calculate custom subnet masks. 6 problems with 10 parts each.</div>
            </a>
            <a href="{{ url_for('agent3.home') }}" class="agent-card">
                <div class="agent-num">3</div>
                <div class="agent-title">Subnet Ranges</div>
                <div class="agent-desc">Ranges, broadcasts, assignable addresses. 6 problems with 12 parts each.</div>
            </a>
            <a href="{{ url_for('agent4.home') }}" class="agent-card">
                <div class="agent-num">4</div>
                <div class="agent-title">VLSM</div>
                <div class="agent-desc">Variable Length Subnet Masking. 3 complete network design scenarios.</div>
            </a>
        </div>
    </div>
</body>
</html>
"""

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username == USERNAME and password == PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('menu'))
        return render_template_string(LOGIN_HTML, error="Invalid credentials")
    return render_template_string(LOGIN_HTML, error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def menu():
    return render_template_string(MENU_HTML)

#═══════════════════════════════════════════════════════════════════════
# RUN APP
#═══════════════════════════════════════════════════════════════════════

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    host = '0.0.0.0' if os.environ.get('PORT') else 'localhost'
    
    print("="*70)
    print("NETWORKING TUTOR SUITE - RENDER DEPLOYMENT")
    print("="*70)
    print(f"\nRunning on http://{host}:{port}")
    print(f"\nLogin: {USERNAME} / {PASSWORD}")
    print("\n" + "="*70)
    
    app.run(debug=False, host=host, port=port)
