from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import io

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24).hex()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///classified_docs.db'
app.config['UPLOAD_FOLDER'] = 'documents'

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Classification levels (higher number = higher clearance required)
CLASSIFICATION_LEVELS = {
    'UNCLASSIFIED': 0,
    'CONFIDENTIAL': 1,
    'SECRET': 2,
    'TOP_SECRET': 3
}

# Document types
DOCUMENT_TYPES = {
    'REPORT': {'label': 'Report', 'icon': 'report', 'color': '#3498db'},
    'MEMO': {'label': 'Memorandum', 'icon': 'memo', 'color': '#9b59b6'},
    'INTEL': {'label': 'Intelligence Brief', 'icon': 'intel', 'color': '#e74c3c'},
    'POLICY': {'label': 'Policy Document', 'icon': 'policy', 'color': '#2ecc71'},
    'OPERATION': {'label': 'Operation Plan', 'icon': 'operation', 'color': '#e67e22'},
    'CORRESPONDENCE': {'label': 'Correspondence', 'icon': 'correspondence', 'color': '#1abc9c'},
    'TECHNICAL': {'label': 'Technical Manual', 'icon': 'technical', 'color': '#34495e'},
    'PERSONNEL': {'label': 'Personnel File', 'icon': 'personnel', 'color': '#f39c12'},
    'FINANCIAL': {'label': 'Financial Record', 'icon': 'financial', 'color': '#27ae60'},
    'OTHER': {'label': 'Other', 'icon': 'other', 'color': '#7f8c8d'}
}

# Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    clearance_level = db.Column(db.String(20), default='UNCLASSIFIED')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def has_clearance(self, classification):
        user_level = CLASSIFICATION_LEVELS.get(self.clearance_level, 0)
        doc_level = CLASSIFICATION_LEVELS.get(classification, 0)
        return user_level >= doc_level


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    classification = db.Column(db.String(20), default='UNCLASSIFIED')
    doc_type = db.Column(db.String(20), default='OTHER')
    content = db.Column(db.LargeBinary)
    filename = db.Column(db.String(255))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    uploader = db.relationship('User', backref='documents')

    @property
    def type_info(self):
        return DOCUMENT_TYPES.get(self.doc_type, DOCUMENT_TYPES['OTHER'])


class AuditLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    action = db.Column(db.String(50))
    document_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='audit_logs')


def log_action(user_id, action, document_id=None, details=None):
    log = AuditLog(user_id=user_id, action=action, document_id=document_id, details=details)
    db.session.add(log)
    db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Routes
@app.route('/')
@login_required
def index():
    user_level = CLASSIFICATION_LEVELS.get(current_user.clearance_level, 0)
    allowed_classifications = [k for k, v in CLASSIFICATION_LEVELS.items() if v <= user_level]

    # Filter by type if specified
    filter_type = request.args.get('type')
    query = Document.query.filter(Document.classification.in_(allowed_classifications))
    if filter_type and filter_type in DOCUMENT_TYPES:
        query = query.filter(Document.doc_type == filter_type)

    documents = query.order_by(Document.created_at.desc()).all()
    return render_template('index.html', documents=documents, levels=CLASSIFICATION_LEVELS,
                          doc_types=DOCUMENT_TYPES, filter_type=filter_type)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            log_action(user.id, 'LOGIN', details=f'User {username} logged in')
            flash('Logged in successfully.', 'success')
            return redirect(url_for('index'))
        flash('Invalid username or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    log_action(current_user.id, 'LOGOUT', details=f'User {current_user.username} logged out')
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if User.query.filter_by(username=username).first():
            flash('Username already exists.', 'error')
            return redirect(url_for('register'))

        user = User(
            username=username,
            password_hash=generate_password_hash(password),
            clearance_level='UNCLASSIFIED'
        )
        db.session.add(user)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        classification = request.form.get('classification', 'UNCLASSIFIED')
        doc_type = request.form.get('doc_type', 'OTHER')
        file = request.files.get('file')

        if not current_user.has_clearance(classification):
            flash('You do not have clearance to create documents at this classification level.', 'error')
            return redirect(url_for('upload'))

        content = file.read() if file else None
        filename = file.filename if file else None

        doc = Document(
            title=title,
            description=description,
            classification=classification,
            doc_type=doc_type,
            content=content,
            filename=filename,
            uploaded_by=current_user.id
        )
        db.session.add(doc)
        db.session.commit()

        log_action(current_user.id, 'UPLOAD', doc.id, f'Uploaded document: {title} [{classification}] ({doc_type})')
        flash('Document uploaded successfully.', 'success')
        return redirect(url_for('index'))

    user_level = CLASSIFICATION_LEVELS.get(current_user.clearance_level, 0)
    allowed_levels = {k: v for k, v in CLASSIFICATION_LEVELS.items() if v <= user_level}
    return render_template('upload.html', levels=allowed_levels, doc_types=DOCUMENT_TYPES)


@app.route('/document/<int:doc_id>')
@login_required
def view_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if not current_user.has_clearance(doc.classification):
        log_action(current_user.id, 'ACCESS_DENIED', doc_id, f'Attempted to access {doc.title}')
        flash('Access denied. Insufficient clearance level.', 'error')
        return redirect(url_for('index'))

    log_action(current_user.id, 'VIEW', doc_id, f'Viewed document: {doc.title}')
    return render_template('document.html', doc=doc, doc_types=DOCUMENT_TYPES)


@app.route('/download/<int:doc_id>')
@login_required
def download_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if not current_user.has_clearance(doc.classification):
        log_action(current_user.id, 'DOWNLOAD_DENIED', doc_id, f'Attempted to download {doc.title}')
        flash('Access denied. Insufficient clearance level.', 'error')
        return redirect(url_for('index'))

    if not doc.content:
        flash('No file attached to this document.', 'error')
        return redirect(url_for('view_document', doc_id=doc_id))

    log_action(current_user.id, 'DOWNLOAD', doc_id, f'Downloaded document: {doc.title}')
    return send_file(io.BytesIO(doc.content), download_name=doc.filename, as_attachment=True)


@app.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete_document(doc_id):
    doc = Document.query.get_or_404(doc_id)

    if not current_user.has_clearance(doc.classification):
        flash('Access denied. Insufficient clearance level.', 'error')
        return redirect(url_for('index'))

    title = doc.title
    db.session.delete(doc)
    db.session.commit()

    log_action(current_user.id, 'DELETE', doc_id, f'Deleted document: {title}')
    flash('Document deleted successfully.', 'success')
    return redirect(url_for('index'))


@app.route('/audit')
@login_required
def audit_log():
    if current_user.clearance_level != 'TOP_SECRET':
        flash('Access denied. TOP SECRET clearance required.', 'error')
        return redirect(url_for('index'))

    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(100).all()
    return render_template('audit.html', logs=logs)


@app.route('/admin/users')
@login_required
def admin_users():
    if current_user.clearance_level != 'TOP_SECRET':
        flash('Access denied. TOP SECRET clearance required.', 'error')
        return redirect(url_for('index'))

    users = User.query.all()
    return render_template('users.html', users=users, levels=CLASSIFICATION_LEVELS)


@app.route('/admin/users/<int:user_id>/clearance', methods=['POST'])
@login_required
def update_clearance(user_id):
    if current_user.clearance_level != 'TOP_SECRET':
        flash('Access denied.', 'error')
        return redirect(url_for('index'))

    user = User.query.get_or_404(user_id)
    new_clearance = request.form.get('clearance')

    if new_clearance in CLASSIFICATION_LEVELS:
        old_clearance = user.clearance_level
        user.clearance_level = new_clearance
        db.session.commit()
        log_action(current_user.id, 'CLEARANCE_CHANGE', details=f'Changed {user.username} from {old_clearance} to {new_clearance}')
        flash(f'Updated clearance for {user.username}.', 'success')

    return redirect(url_for('admin_users'))


def init_db():
    with app.app_context():
        db.create_all()

        # Create admin user if not exists
        if not User.query.filter_by(username='admin').first():
            admin = User(
                username='admin',
                password_hash=generate_password_hash('admin123'),
                clearance_level='TOP_SECRET'
            )
            db.session.add(admin)
            db.session.commit()
            print('Admin user created: admin / admin123')


if __name__ == '__main__':
    init_db()
    print('\n=== Classified Documents Management System ===')
    print('Default admin credentials: admin / admin123')
    print('Access the system at: http://127.0.0.1:5000\n')
    app.run(debug=True, host='0.0.0.0', port=5000)
