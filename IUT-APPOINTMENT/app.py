import os
from flask import Flask, redirect, url_for, render_template
from flask_login import LoginManager, current_user
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_mail import Mail
from flask_migrate import Migrate
from models import db, User
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'iut_secret_key_2026'
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database', 'university.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Session timeout — 30 minutes of inactivity
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)

# Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = os.environ.get('MAIL_USERNAME', 'noreply@iut-dhaka.edu')

CSRFProtect(app)
db.init_app(app)
migrate = Migrate(app, db)
bcrypt = Bcrypt(app)
mail = Mail(app)

login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

with app.app_context():
    db_dir = os.path.join(basedir, 'database')
    if not os.path.exists(db_dir):
        os.makedirs(db_dir)
    db.create_all()

# ── Session timeout middleware ─────────────────────────────────────────────────
from flask import session, request as flask_request
from flask_login import logout_user

@app.before_request
def check_session_timeout():
    if current_user.is_authenticated:
        last = session.get('last_activity')
        now = datetime.utcnow().timestamp()
        if last and (now - last) > 30 * 60:
            logout_user()
            session.clear()
            from flask import flash
            flash('Your session expired due to inactivity. Please log in again.', 'warning')
            return redirect(url_for('auth.login'))
        session['last_activity'] = now
        session.permanent = True
        # Update last_seen
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

# ── Time slot generator ───────────────────────────────────────────────────────
def generate_time_slots(start_str="08:00", end_str="17:00"):
    slots = []
    fmt = "%H:%M"
    current = datetime.strptime(start_str, fmt)
    end = datetime.strptime(end_str, fmt)
    while current < end:
        nxt = current + timedelta(hours=1)
        slots.append(f"{current.strftime('%I:%M %p')} - {nxt.strftime('%I:%M %p')}")
        current = nxt
    return slots

# ── Error pages ───────────────────────────────────────────────────────────────
@app.errorhandler(404)
def not_found(e):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('errors/500.html'), 500

@app.errorhandler(403)
def forbidden(e):
    return render_template('errors/403.html'), 403

# ── Blueprints ────────────────────────────────────────────────────────────────
from routes.auth import auth_bp
from routes.student import student_bp
from routes.admin import admin_bp

app.register_blueprint(auth_bp)
app.register_blueprint(student_bp)
app.register_blueprint(admin_bp)

@app.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        return redirect(url_for('student.dashboard'))
    return render_template('home.html')

if __name__ == '__main__':
    app.run(debug=True)
