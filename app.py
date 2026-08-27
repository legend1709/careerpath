from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from database import init_db, get_db, create_admin
from recommendation import RecommendationEngine

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production-12345'

# Initialize database on startup
init_db()

# ==================== DECORATORS ====================

def login_required(f):
    """Decorator to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first', 'warning')
            return redirect(url_for('login'))
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT role FROM users WHERE id = ?', (session['user_id'],))
        user = cursor.fetchone()
        db.close()
        
        if not user or user[0] != 'admin':
            flash('Access denied. Admin only.', 'danger')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function

# ==================== ROUTES - PUBLIC ====================

@app.route('/')
def index():
    """Home page"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM careers LIMIT 6')
    featured_careers = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('index.html', featured_careers=featured_careers)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('register'))
        
        if '@' not in email or '.' not in email:
            flash('Please enter a valid email', 'danger')
            return redirect(url_for('register'))
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            password_hash = generate_password_hash(password)
            cursor.execute('''
                INSERT INTO users (name, email, password, role)
                VALUES (?, ?, ?, ?)
            ''', (name, email, password_hash, 'student'))
            db.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already registered', 'danger')
        finally:
            db.close()
        
        return redirect(url_for('register'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password required', 'danger')
            return redirect(url_for('login'))
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT id, password, role FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        db.close()
        
        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['user_role'] = user[2]
            
            if user[2] == 'admin':
                flash('Welcome back, Admin!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password', 'danger')
        
        return redirect(url_for('login'))
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    """Logout user"""
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('index'))

# ==================== ROUTES - STUDENT ====================

@app.route('/dashboard')
@login_required
def dashboard():
    """Student dashboard"""
    db = get_db()
    cursor = db.cursor()
    
    # Get user info
    cursor.execute('SELECT name FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    
    # Get assessments count
    cursor.execute('SELECT COUNT(*) FROM assessments WHERE user_id = ?', 
                   (session['user_id'],))
    assessment_count = cursor.fetchone()[0]
    
    # Get latest assessment with recommendations
    cursor.execute('''
        SELECT a.id, a.created_at, r.career_id, r.percentage, c.title, c.icon
        FROM assessments a
        LEFT JOIN recommendations r ON a.id = r.assessment_id
        LEFT JOIN careers c ON r.career_id = c.id
        WHERE a.user_id = ? AND r.id IS NOT NULL
        ORDER BY a.id DESC LIMIT 1
    ''', (session['user_id'],))
    latest_assessment = cursor.fetchone()
    
    # Get top career recommendation
    cursor.execute('''
        SELECT c.title, c.icon, MAX(r.percentage) as percentage
        FROM assessments a
        JOIN recommendations r ON a.id = r.assessment_id
        JOIN careers c ON r.career_id = c.id
        WHERE a.user_id = ?
        GROUP BY c.id
        ORDER BY percentage DESC
        LIMIT 1
    ''', (session['user_id'],))
    top_career = cursor.fetchone()
    
    db.close()
    
    return render_template('dashboard.html',
                         user_name=user[0] if user else 'Student',
                         assessment_count=assessment_count,
                         latest_assessment=latest_assessment,
                         top_career=top_career)

@app.route('/assessment', methods=['GET', 'POST'])
@login_required
def assessment():
    """Career assessment questionnaire"""
    if request.method == 'POST':
        db = get_db()
        cursor = db.cursor()
        
        # Create new assessment
        cursor.execute('INSERT INTO assessments (user_id) VALUES (?)',
                      (session['user_id'],))
        db.commit()
        assessment_id = cursor.lastrowid
        
        # Save answers for each section
        interests = request.form.getlist('interests')
        skills = request.form.getlist('skills')
        subjects = request.form.getlist('subjects')
        strengths = request.form.getlist('strengths')
        preferences = request.form.getlist('preferences')
        
        # Store each as separate question-answer pair
        questions_answers = [
            (1, ','.join(interests) if interests else ''),
            (2, ','.join(skills) if skills else ''),
            (3, ','.join(subjects) if subjects else ''),
            (4, ','.join(strengths) if strengths else ''),
            (5, ','.join(preferences) if preferences else '')
        ]
        
        for q_id, answer in questions_answers:
            cursor.execute('''
                INSERT INTO answers (assessment_id, question_id, answer)
                VALUES (?, ?, ?)
            ''', (assessment_id, q_id, answer))
        
        db.commit()
        db.close()
        
        # Generate recommendations
        RecommendationEngine.calculate_recommendations(assessment_id)
        
        flash('Assessment submitted successfully!', 'success')
        return redirect(url_for('results', assessment_id=assessment_id))
    
    return render_template('questionnaire.html')

@app.route('/results/<int:assessment_id>')
@login_required
def results(assessment_id):
    """Display assessment results and recommendations"""
    db = get_db()
    cursor = db.cursor()
    
    # Verify assessment belongs to user
    cursor.execute('SELECT user_id FROM assessments WHERE id = ?', (assessment_id,))
    assessment = cursor.fetchone()
    
    if not assessment or assessment[0] != session['user_id']:
        flash('Assessment not found', 'danger')
        db.close()
        return redirect(url_for('dashboard'))
    
    # Get recommendations
    cursor.execute('''
        SELECT r.id, r.career_id, r.percentage, c.title, c.description, 
               c.required_skills, c.icon
        FROM recommendations r
        JOIN careers c ON r.career_id = c.id
        WHERE r.assessment_id = ?
        ORDER BY r.percentage DESC
    ''', (assessment_id,))
    
    recommendations = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('results.html',
                         assessment_id=assessment_id,
                         recommendations=recommendations)

@app.route('/career/<int:career_id>')
def career_details(career_id):
    """Display career details"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM careers WHERE id = ?', (career_id,))
    career = cursor.fetchone()
    
    if not career:
        flash('Career not found', 'danger')
        db.close()
        return redirect(url_for('careers'))
    
    # Get related careers (same category)
    cursor.execute('SELECT id, title, icon FROM careers WHERE category = ? AND id != ? LIMIT 3',
                   (career[2], career_id))
    related = [dict(row) for row in cursor.fetchall()]
    
    db.close()
    career_dict = dict(career)
    
    return render_template('career_details.html',
                         career=career_dict,
                         related=related)

@app.route('/careers')
def careers():
    """Browse all careers"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM careers ORDER BY title')
    all_careers = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('careers.html', careers=all_careers)

# ==================== ROUTES - ADMIN ====================

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    db = get_db()
    cursor = db.cursor()
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM users WHERE role = "student"')
    total_users = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM careers')
    total_careers = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM assessments')
    total_assessments = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM recommendations')
    total_recommendations = cursor.fetchone()[0]
    
    db.close()
    
    return render_template('admin/admin_dashboard.html',
                         total_users=total_users,
                         total_careers=total_careers,
                         total_assessments=total_assessments,
                         total_recommendations=total_recommendations)

@app.route('/admin/users')
@admin_required
def admin_users():
    """View all users"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, role, created_at FROM users ORDER BY created_at DESC')
    users = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('admin/users.html', users=users)

@app.route('/admin/careers')
@admin_required
def admin_careers():
    """Manage careers"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM careers ORDER BY title')
    careers = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('admin/careers.html', careers=careers)

@app.route('/admin/careers/add', methods=['GET', 'POST'])
@admin_required
def add_career():
    """Add new career"""
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        education = request.form.get('education')
        job_roles = request.form.get('job_roles')
        salary_range = request.form.get('salary_range')
        growth = request.form.get('growth')
        icon = request.form.get('icon')
        
        if not all([title, category, description]):
            flash('Title, category, and description are required', 'danger')
            return redirect(url_for('add_career'))
        
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            INSERT INTO careers (title, category, description, required_skills, 
                               education, job_roles, salary_range, growth, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, category, description, required_skills, education, 
              job_roles, salary_range, growth, icon))
        db.commit()
        db.close()
        
        flash('Career added successfully!', 'success')
        return redirect(url_for('admin_careers'))
    
    return render_template('admin/add_career.html')

@app.route('/admin/careers/edit/<int:career_id>', methods=['GET', 'POST'])
@admin_required
def edit_career(career_id):
    """Edit career"""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        description = request.form.get('description')
        required_skills = request.form.get('required_skills')
        education = request.form.get('education')
        job_roles = request.form.get('job_roles')
        salary_range = request.form.get('salary_range')
        growth = request.form.get('growth')
        icon = request.form.get('icon')
        
        if not all([title, category, description]):
            flash('Title, category, and description are required', 'danger')
            return redirect(url_for('edit_career', career_id=career_id))
        
        cursor.execute('''
            UPDATE careers 
            SET title=?, category=?, description=?, required_skills=?, 
                education=?, job_roles=?, salary_range=?, growth=?, icon=?
            WHERE id=?
        ''', (title, category, description, required_skills, education,
              job_roles, salary_range, growth, icon, career_id))
        db.commit()
        db.close()
        
        flash('Career updated successfully!', 'success')
        return redirect(url_for('admin_careers'))
    
    cursor.execute('SELECT * FROM careers WHERE id = ?', (career_id,))
    career = cursor.fetchone()
    db.close()
    
    if not career:
        flash('Career not found', 'danger')
        return redirect(url_for('admin_careers'))
    
    return render_template('admin/edit_career.html', career=dict(career))

@app.route('/admin/careers/delete/<int:career_id>')
@admin_required
def delete_career(career_id):
    """Delete career"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM careers WHERE id = ?', (career_id,))
    db.commit()
    db.close()
    
    flash('Career deleted successfully!', 'success')
    return redirect(url_for('admin_careers'))

@app.route('/admin/assessments')
@admin_required
def admin_assessments():
    """View assessments"""
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        SELECT a.id, a.created_at, u.name, u.email, c.title, r.percentage
        FROM assessments a
        JOIN users u ON a.user_id = u.id
        LEFT JOIN recommendations r ON a.id = r.assessment_id
        ORDER BY a.created_at DESC
    ''')
    assessments = [dict(row) for row in cursor.fetchall()]
    db.close()
    
    return render_template('admin/assessments.html', assessments=assessments)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('errors/500.html'), 500

if __name__ == '__main__':
    app.run(debug=True)