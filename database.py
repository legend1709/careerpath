import sqlite3
import os
import json
from datetime import datetime
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'database/career.db'

def get_db():
    """Get database connection"""
    db = sqlite3.connect(DATABASE_PATH)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Initialize database with all tables and default data"""
    # Create database directory if it doesn't exist
    os.makedirs('database', exist_ok=True)
    
    # Only initialize if database doesn't exist
    if not os.path.exists(DATABASE_PATH):
        create_tables()
        seed_careers()
        create_admin()

def create_tables():
    """Create all database tables"""
    db = get_db()
    cursor = db.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'student',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Careers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS careers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            required_skills TEXT,
            education TEXT,
            job_roles TEXT,
            salary_range TEXT,
            growth TEXT,
            icon TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Questions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question TEXT NOT NULL,
            category TEXT NOT NULL,
            options TEXT NOT NULL
        )
    ''')
    
    # Assessments table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS assessments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Answers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS answers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            question_id INTEGER NOT NULL,
            answer TEXT NOT NULL,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id),
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
    ''')
    
    # Recommendations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS recommendations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            assessment_id INTEGER NOT NULL,
            career_id INTEGER NOT NULL,
            score INTEGER,
            percentage REAL,
            FOREIGN KEY (assessment_id) REFERENCES assessments (id),
            FOREIGN KEY (career_id) REFERENCES careers (id)
        )
    ''')
    
    db.commit()
    db.close()

def seed_careers():
    """Insert default careers into database"""
    db = get_db()
    cursor = db.cursor()
    
    careers = [
        {
            'title': 'Software Developer',
            'category': 'Technology',
            'description': 'Design, build, and maintain software applications. Work with programming languages to create solutions for various platforms.',
            'required_skills': 'Python, Java, C++, JavaScript, Problem Solving, Data Structures',
            'education': 'Bachelor\'s in Computer Science or related field',
            'job_roles': 'Junior Developer, Senior Developer, Full-Stack Developer, Backend Developer',
            'salary_range': '$60,000 - $120,000',
            'growth': 'High demand, 15% job growth',
            'icon': 'fa-laptop-code'
        },
        {
            'title': 'Web Developer',
            'category': 'Technology',
            'description': 'Create and maintain websites and web applications. Specialize in front-end, back-end, or full-stack development.',
            'required_skills': 'HTML, CSS, JavaScript, React, Node.js, SQL, Web Design',
            'education': 'Bachelor\'s in Computer Science or Bootcamp Certificate',
            'job_roles': 'Frontend Developer, Backend Developer, Full-Stack Developer, Web Designer',
            'salary_range': '$50,000 - $110,000',
            'growth': 'Consistent demand, 13% job growth',
            'icon': 'fa-globe'
        },
        {
            'title': 'Data Analyst',
            'category': 'Analytics',
            'description': 'Analyze data to help businesses make informed decisions. Use statistical tools and visualization techniques.',
            'required_skills': 'SQL, Python, Excel, Tableau, Power BI, Statistical Analysis',
            'education': 'Bachelor\'s in Statistics, Mathematics, or Computer Science',
            'job_roles': 'Junior Data Analyst, Senior Data Analyst, Business Analyst, Analytics Manager',
            'salary_range': '$55,000 - $100,000',
            'growth': 'Very high demand, 25% job growth',
            'icon': 'fa-chart-bar'
        },
        {
            'title': 'Data Scientist',
            'category': 'Analytics',
            'description': 'Build machine learning models and predictive analytics. Extract insights from large datasets.',
            'required_skills': 'Python, R, Machine Learning, Statistics, SQL, Deep Learning',
            'education': 'Bachelor\'s/Master\'s in Computer Science, Mathematics, or Statistics',
            'job_roles': 'Junior Data Scientist, Senior Data Scientist, ML Engineer, Research Scientist',
            'salary_range': '$80,000 - $150,000',
            'growth': 'Extremely high demand, 35% job growth',
            'icon': 'fa-brain'
        },
        {
            'title': 'AI/ML Engineer',
            'category': 'Technology',
            'description': 'Develop and deploy artificial intelligence and machine learning solutions for complex problems.',
            'required_skills': 'Python, TensorFlow, PyTorch, Machine Learning, Deep Learning, Computer Vision',
            'education': 'Master\'s in Computer Science or Machine Learning',
            'job_roles': 'ML Engineer, Deep Learning Engineer, AI Researcher, NLP Engineer',
            'salary_range': '$90,000 - $180,000',
            'growth': 'Extreme growth, 50%+ expected',
            'icon': 'fa-microchip'
        },
        {
            'title': 'Cybersecurity Analyst',
            'category': 'Security',
            'description': 'Protect computer systems and networks from cyber threats. Monitor and respond to security incidents.',
            'required_skills': 'Networking, Linux, Security Protocols, Ethical Hacking, Firewalls',
            'education': 'Bachelor\'s in Cybersecurity or Computer Science',
            'job_roles': 'Security Analyst, Penetration Tester, Security Engineer, CISO',
            'salary_range': '$65,000 - $130,000',
            'growth': 'Critical demand, 33% job growth',
            'icon': 'fa-shield-alt'
        },
        {
            'title': 'Cloud Engineer',
            'category': 'Infrastructure',
            'description': 'Design and manage cloud infrastructure. Work with AWS, Azure, or Google Cloud platforms.',
            'required_skills': 'AWS, Azure, Kubernetes, DevOps, Linux, Docker',
            'education': 'Bachelor\'s in Computer Science + Cloud Certifications',
            'job_roles': 'Cloud Architect, DevOps Engineer, Cloud Administrator, Site Reliability Engineer',
            'salary_range': '$70,000 - $140,000',
            'growth': 'Very high demand, 25% job growth',
            'icon': 'fa-cloud'
        },
        {
            'title': 'UI/UX Designer',
            'category': 'Design',
            'description': 'Create intuitive and visually appealing user interfaces and experiences for digital products.',
            'required_skills': 'Figma, Adobe XD, Prototyping, User Research, Wireframing, CSS',
            'education': 'Bachelor\'s in Design or UX/UI Bootcamp',
            'job_roles': 'UI Designer, UX Designer, Product Designer, Design Lead',
            'salary_range': '$55,000 - $110,000',
            'growth': 'Growing demand, 13% job growth',
            'icon': 'fa-palette'
        },
        {
            'title': 'Mobile App Developer',
            'category': 'Technology',
            'description': 'Develop applications for mobile devices using iOS and Android platforms.',
            'required_skills': 'Swift, Kotlin, React Native, Java, Firebase, Mobile UI',
            'education': 'Bachelor\'s in Computer Science or Mobile Development Bootcamp',
            'job_roles': 'iOS Developer, Android Developer, Flutter Developer, Mobile Tech Lead',
            'salary_range': '$60,000 - $130,000',
            'growth': 'Consistent growth, 15% job growth',
            'icon': 'fa-mobile-alt'
        },
        {
            'title': 'Game Developer',
            'category': 'Gaming',
            'description': 'Create interactive video games for various platforms. Work with game engines and graphics.',
            'required_skills': 'C#, Unity, Unreal Engine, Game Design, 3D Graphics, Physics',
            'education': 'Bachelor\'s in Game Development or Computer Science',
            'job_roles': 'Game Programmer, Game Designer, Graphics Programmer, Technical Director',
            'salary_range': '$60,000 - $140,000',
            'growth': 'Growing market, 10% job growth',
            'icon': 'fa-gamepad'
        },
        {
            'title': 'Database Administrator',
            'category': 'Infrastructure',
            'description': 'Manage, secure, and maintain databases that store organizational data.',
            'required_skills': 'SQL, MySQL, PostgreSQL, MongoDB, Backup, Performance Tuning',
            'education': 'Bachelor\'s in Computer Science or Information Technology',
            'job_roles': 'Database Administrator, Database Developer, Database Architect, DBA Manager',
            'salary_range': '$60,000 - $120,000',
            'growth': 'Steady demand, 8% job growth',
            'icon': 'fa-database'
        },
        {
            'title': 'Network Engineer',
            'category': 'Infrastructure',
            'description': 'Design, implement, and manage computer networks for organizations.',
            'required_skills': 'Networking, Cisco, TCP/IP, Routing, Switching, Security Protocols',
            'education': 'Bachelor\'s in Computer Science or IT with networking focus',
            'job_roles': 'Network Administrator, Network Architect, Network Security Engineer, Systems Engineer',
            'salary_range': '$60,000 - $125,000',
            'growth': 'Steady demand, 5% job growth',
            'icon': 'fa-network-wired'
        },
        {
            'title': 'Digital Marketer',
            'category': 'Marketing',
            'description': 'Plan and execute digital marketing strategies across online platforms.',
            'required_skills': 'SEO, Social Media, Google Analytics, Content Marketing, Email Marketing',
            'education': 'Bachelor\'s in Marketing or Digital Marketing Bootcamp',
            'job_roles': 'Social Media Manager, SEO Specialist, Content Marketer, Growth Hacker',
            'salary_range': '$45,000 - $90,000',
            'growth': 'Strong growth, 10% job growth',
            'icon': 'fa-bullhorn'
        },
        {
            'title': 'Business Analyst',
            'category': 'Business',
            'description': 'Analyze business needs and translate them into technical solutions. Bridge business and IT.',
            'required_skills': 'Requirements Analysis, Process Modeling, SQL, Communication, Project Management',
            'education': 'Bachelor\'s in Business Administration or Computer Science',
            'job_roles': 'Business Analyst, Systems Analyst, Product Owner, Requirements Engineer',
            'salary_range': '$55,000 - $110,000',
            'growth': 'Growing demand, 12% job growth',
            'icon': 'fa-briefcase'
        },
        {
            'title': 'Graphic Designer',
            'category': 'Design',
            'description': 'Create visual content for various media including print, digital, and advertising.',
            'required_skills': 'Adobe Creative Suite, Photoshop, Illustrator, InDesign, Branding, Typography',
            'education': 'Bachelor\'s in Graphic Design or Art',
            'job_roles': 'Graphic Designer, Art Director, Visual Designer, Branding Specialist',
            'salary_range': '$40,000 - $85,000',
            'growth': 'Moderate growth, 3% job growth',
            'icon': 'fa-paint-brush'
        }
    ]
    
    for career in careers:
        cursor.execute('''
            INSERT INTO careers 
            (title, category, description, required_skills, education, job_roles, salary_range, growth, icon)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            career['title'],
            career['category'],
            career['description'],
            career['required_skills'],
            career['education'],
            career['job_roles'],
            career['salary_range'],
            career['growth'],
            career['icon']
        ))
    
    db.commit()
    db.close()

def create_admin():
    """Create default admin account"""
    db = get_db()
    cursor = db.cursor()
    
    admin_password_hash = generate_password_hash('admin123')
    
    try:
        cursor.execute('''
            INSERT INTO users (name, email, password, role)
            VALUES (?, ?, ?, ?)
        ''', ('Admin User', 'admin@careerpath.com', admin_password_hash, 'admin'))
        
        db.commit()
    except sqlite3.IntegrityError:
        # Admin already exists
        pass
    
    db.close()