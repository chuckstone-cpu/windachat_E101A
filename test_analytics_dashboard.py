from mock_database import get_student_db
from student_analytics import StudentAnalyzer

# Initialize
db = get_student_db()
analyzer = StudentAnalyzer()

print("\n" + "="*85)
print(f"{'NAME':<20} | {'SCORES':<20} | {'AVG':<5} | {'RATING':<6} | {'INSIGHT'}")
print("="*85)

for student in db:
    # 1. Run the Analytics Engine Logic
    rating, insight = analyzer.calculate_hidden_rating({
        'scores': student['scores'],
        'quizzes_taken': student['quizzes_taken']
    })
    
    # 2. Calculate simple average just to compare
    avg = sum(student['scores']) / len(student['scores'])
    scores_str = str(student['scores'])
    
    # 3. Print the Row
    print(f"{student['name']:<20} | {scores_str:<20} | {int(avg):<5} | {rating:<6} | {insight}")

print("="*85 + "\n")