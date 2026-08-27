from database import get_db

class RecommendationEngine:
    """
    Rule-based recommendation engine that matches user answers with careers
    """
    
    # Career scoring profiles - keywords and their weights
    CAREER_PROFILES = {
        1: {  # Software Developer
            'Programming': 10,
            'Problem Solving': 8,
            'Computer Science': 8,
            'Logical Thinking': 10,
            'Python': 5,
            'C++': 5,
            'Java': 5,
            'JavaScript': 5,
            'Working with computers': 8,
            'Building products': 8,
            'Technology': 10
        },
        2: {  # Web Developer
            'Programming': 9,
            'Design': 7,
            'JavaScript': 10,
            'HTML/CSS': 10,
            'Communication': 6,
            'Creativity': 7,
            'Working with computers': 9,
            'Building products': 8,
            'Technology': 9
        },
        3: {  # Data Analyst
            'Mathematics': 8,
            'Statistics': 10,
            'Data Analysis': 10,
            'Analytical Thinking': 10,
            'Python': 6,
            'SQL': 8,
            'Attention to Detail': 7,
            'Problem Solving': 7,
            'Research': 6
        },
        4: {  # Data Scientist
            'Mathematics': 10,
            'Statistics': 10,
            'Data Analysis': 10,
            'Analytical Thinking': 10,
            'Python': 8,
            'Research': 8,
            'Logical Thinking': 8,
            'Problem Solving': 8,
            'Technology': 8
        },
        5: {  # AI/ML Engineer
            'Programming': 10,
            'Python': 10,
            'Mathematics': 9,
            'Problem Solving': 10,
            'Logical Thinking': 10,
            'Research': 7,
            'Computer Science': 9,
            'Working with computers': 9
        },
        6: {  # Cybersecurity Analyst
            'Networking': 10,
            'Problem Solving': 8,
            'Computer Science': 8,
            'Logical Thinking': 8,
            'Java': 6,
            'Python': 6,
            'Research': 6,
            'Technology': 9
        },
        7: {  # Cloud Engineer
            'Programming': 8,
            'Problem Solving': 8,
            'Computer Science': 8,
            'Technology': 10,
            'Networking': 7,
            'Java': 6,
            'Python': 6,
            'Working with computers': 9
        },
        8: {  # UI/UX Designer
            'Design': 10,
            'Creativity': 10,
            'Photoshop': 8,
            'Communication': 5,
            'Attention to Detail': 8,
            'Problem Solving': 5,
            'Working with people': 6,
            'Logical Thinking': 4
        },
        9: {  # Mobile App Developer
            'Programming': 10,
            'Java': 8,
            'JavaScript': 7,
            'C++': 6,
            'Problem Solving': 8,
            'Design': 6,
            'Working with computers': 9,
            'Building products': 8,
            'Technology': 9
        },
        10: {  # Game Developer
            'Programming': 10,
            'C++': 10,
            'Java': 8,
            'Creativity': 8,
            'Problem Solving': 8,
            'Physics': 7,
            'Mathematics': 7,
            'Logical Thinking': 8,
            'Gaming': 10
        },
        11: {  # Database Administrator
            'SQL': 10,
            'Mathematics': 6,
            'Computer Science': 8,
            'Problem Solving': 7,
            'Attention to Detail': 8,
            'Logical Thinking': 8,
            'Technology': 8,
            'Working with computers': 9
        },
        12: {  # Network Engineer
            'Networking': 10,
            'Computer Science': 8,
            'Problem Solving': 7,
            'Logical Thinking': 8,
            'Communication': 6,
            'Technology': 9,
            'Working with computers': 9,
            'Working with people': 5
        },
        13: {  # Digital Marketer
            'Communication': 9,
            'Creativity': 8,
            'Business': 8,
            'Working with people': 8,
            'Problem Solving': 6,
            'Technology': 5,
            'Research': 5,
            'Leadership': 6
        },
        14: {  # Business Analyst
            'Problem Solving': 8,
            'Communication': 8,
            'Business': 9,
            'Analytical Thinking': 8,
            'Working with people': 7,
            'Technology': 6,
            'Leadership': 6,
            'Attention to Detail': 7
        },
        15: {  # Graphic Designer
            'Design': 10,
            'Creativity': 10,
            'Photoshop': 9,
            'Attention to Detail': 8,
            'Communication': 6,
            'Artistic': 9,
            'Working with computers': 7,
            'Problem Solving': 5
        }
    }
    
    @staticmethod
    def calculate_recommendations(assessment_id):
        """
        Calculate career recommendations based on assessment answers
        Returns top 5 careers with scores and percentages
        """
        db = get_db()
        cursor = db.cursor()
        
        # Get all answers for this assessment
        cursor.execute('''
            SELECT a.answer FROM answers a
            WHERE a.assessment_id = ?
        ''', (assessment_id,))
        
        answers = [row[0] for row in cursor.fetchall()]
        
        # Flatten all answers into a single list of keywords
        all_keywords = []
        for answer in answers:
            if isinstance(answer, str):
                # Split multiple selections
                keywords = [k.strip() for k in answer.split(',')]
                all_keywords.extend(keywords)
        
        # Calculate scores for each career
        career_scores = {}
        
        cursor.execute('SELECT id FROM careers')
        careers = cursor.fetchall()
        
        for career in careers:
            career_id = career[0]
            score = 0
            
            # Get profile for this career
            profile = RecommendationEngine.CAREER_PROFILES.get(career_id, {})
            
            # Calculate matching score
            for keyword in all_keywords:
                if keyword in profile:
                    score += profile[keyword]
            
            career_scores[career_id] = score
        
        # Find max score to normalize
        max_score = max(career_scores.values()) if career_scores else 1
        max_score = max(max_score, 1)  # Avoid division by zero
        
        # Create recommendations
        sorted_careers = sorted(
            career_scores.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Insert top 5 recommendations
        rank = 0
        for career_id, score in sorted_careers[:5]:
            percentage = (score / max_score) * 100
            
            cursor.execute('''
                INSERT INTO recommendations (assessment_id, career_id, score, percentage)
                VALUES (?, ?, ?, ?)
            ''', (assessment_id, career_id, score, round(percentage, 1)))
            
            rank += 1
        
        db.commit()
        db.close()
        
        return sorted_careers[:5]
    
    @staticmethod
    def get_recommendations_for_assessment(assessment_id):
        """Get stored recommendations for an assessment"""
        db = get_db()
        cursor = db.cursor()
        
        cursor.execute('''
            SELECT r.id, r.career_id, r.score, r.percentage, c.title, c.description, 
                   c.required_skills, c.icon
            FROM recommendations r
            JOIN careers c ON r.career_id = c.id
            WHERE r.assessment_id = ?
            ORDER BY r.percentage DESC
        ''', (assessment_id,))
        
        recommendations = [dict(row) for row in cursor.fetchall()]
        db.close()
        
        return recommendations