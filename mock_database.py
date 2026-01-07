"""
MOCK DATABASE
20 Students with distinct behavioral patterns to test the Analytics Engine.
"""

STUDENT_DB = [
    # --- GROUP A: THE HIGH PERFORMERS (Consistent & Engagement) ---
    {
        "id": "S001",
        "name": "Alice Chen",
        "scores": [95, 92, 98, 96, 99],
        "quizzes_taken": 5,
        "attendance": 100
    },
    {
        "id": "S002",
        "name": "Marcus Johnson",
        "scores": [88, 90, 89, 92],
        "quizzes_taken": 4,
        "attendance": 95
    },
    {
        "id": "S003",
        "name": "Elena Rodriguez",
        "scores": [90, 95, 100, 98, 92],
        "quizzes_taken": 5,
        "attendance": 98
    },
    {
        "id": "S004",
        "name": "David Kim",
        "scores": [85, 88, 87, 90],
        "quizzes_taken": 4,
        "attendance": 92
    },

    # --- GROUP B: THE IMPROVERS (Low Start -> High End) ---
    # These should get a "Momentum Bonus" in your analytics
    {
        "id": "S005",
        "name": "Sarah Smith",
        "scores": [45, 60, 75, 85, 92], # Steady climb
        "quizzes_taken": 5,
        "attendance": 90
    },
    {
        "id": "S006",
        "name": "James Wilson",
        "scores": [50, 55, 70, 80],
        "quizzes_taken": 4,
        "attendance": 85
    },
    {
        "id": "S007",
        "name": "Priya Patel",
        "scores": [60, 65, 75, 88, 95],
        "quizzes_taken": 5,
        "attendance": 92
    },

    # --- GROUP C: THE SLACKERS (High Start -> Low End) ---
    # These should get a "Momentum Penalty"
    {
        "id": "S008",
        "name": "Michael Brown",
        "scores": [95, 85, 70, 60, 40], # Crashing down
        "quizzes_taken": 5,
        "attendance": 70
    },
    {
        "id": "S009",
        "name": "Emily Davis",
        "scores": [90, 80, 65, 50],
        "quizzes_taken": 4,
        "attendance": 65
    },

    # --- GROUP D: THE ERRATIC / CHAOS (High Standard Deviation) ---
    # These should get a "Consistency Penalty"
    {
        "id": "S010",
        "name": "Ryan Martinez",
        "scores": [100, 20, 95, 30, 85], # All over the place
        "quizzes_taken": 5,
        "attendance": 60
    },
    {
        "id": "S011",
        "name": "Jessica Taylor",
        "scores": [50, 90, 40, 85],
        "quizzes_taken": 4,
        "attendance": 75
    },

    # --- GROUP E: THE GHOSTS (Low Engagement) ---
    # Penalized for taking too few quizzes
    {
        "id": "S012",
        "name": "Tom Anderson",
        "scores": [85], # Only 1 quiz
        "quizzes_taken": 1,
        "attendance": 30
    },
    {
        "id": "S013",
        "name": "Lisa Thomas",
        "scores": [70, 75], # Only 2 quizzes
        "quizzes_taken": 2,
        "attendance": 40
    },

    # --- GROUP F: AVERAGE STUDENTS ---
    {
        "id": "S014",
        "name": "Kevin White",
        "scores": [75, 72, 78, 74],
        "quizzes_taken": 4,
        "attendance": 88
    },
    {
        "id": "S015",
        "name": "Amanda Martin",
        "scores": [65, 68, 70, 66, 69],
        "quizzes_taken": 5,
        "attendance": 85
    },
    {
        "id": "S016",
        "name": "Jason Lee",
        "scores": [70, 72, 71, 73],
        "quizzes_taken": 4,
        "attendance": 82
    },
    {
        "id": "S017",
        "name": "Rebecca Scott",
        "scores": [80, 78, 82, 79],
        "quizzes_taken": 4,
        "attendance": 89
    },
    {
        "id": "S018",
        "name": "Brian Green",
        "scores": [60, 62, 58, 61],
        "quizzes_taken": 4,
        "attendance": 80
    },
    {
        "id": "S019",
        "name": "Laura Adams",
        "scores": [88, 85, 87, 86],
        "quizzes_taken": 4,
        "attendance": 91
    },
    {
        "id": "S020",
        "name": "Justin Nelson",
        "scores": [55, 58, 56, 57],
        "quizzes_taken": 4,
        "attendance": 78
    }
]

def get_student_db():
    return STUDENT_DB