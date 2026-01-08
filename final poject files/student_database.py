"""
Advanced Student Memory System.
Uses Weighted Moving Averages (WMA) for real-time mastery tracking.
"""
import json
from datetime import datetime

class StudentDatabase:
    def __init__(self):
        self.students = {}
        self._load_advanced_mock_data()

    def _load_advanced_mock_data(self):
        # We create "Archetypes" to demonstrate the AI's range
        self.students = {
            "S01": {
                "name": "Alice (The Architect)", 
                "mastery": 92.5, 
                "history": [],
                "learning_style": "Constructivist", # Prefers building mental models
                "traits": "Prefers high-density technical information. Dislikes fluff."
            },
            "S02": {
                "name": "Bob (The Explorer)", 
                "mastery": 35.0, 
                "history": [],
                "learning_style": "Scaffolding", # Needs support structures
                "traits": "Easily overwhelmed. Needs analogies and step-by-step breakdown."
            },
            "S03": {
                "name": "Charlie (The Pragmatist)", 
                "mastery": 68.0, 
                "history": [],
                "learning_style": "Socratic", # Learns by questioning
                "traits": "Prefers practical examples over theory."
            },
        }

    def get_student_list(self):
        return list(self.students.values())

    def get_student_by_name(self, name):
        for sid, data in self.students.items():
            if data['name'] == name:
                return sid, data
        return None, None

    def update_mastery(self, student_id, interaction_score):
        """
        Updates mastery using an Exponential Moving Average (EMA).
        New Score = (Old * 0.8) + (Interaction * 0.2)
        This allows the AI to adapt to sudden changes in understanding.
        """
        if student_id not in self.students: return
        
        current = self.students[student_id]['mastery']
        # 80% weight to history, 20% to new interaction
        new_mastery = (current * 0.8) + (interaction_score * 0.2)
        self.students[student_id]['mastery'] = round(new_mastery, 1)

    def get_psychometric_profile(self, student_id):
        """
        Generates a sophisticated profile string for the LLM.
        """
        s = self.students.get(student_id)
        if not s: return "User: Guest"
        
        return (
            f"USER METADATA:\n"
            f"- Name: {s['name']}\n"
            f"- Current Mastery Index: {s['mastery']}/100\n"
            f"- Cognitive Style: {s['learning_style']}\n"
            f"- Behavioral Traits: {s['traits']}"
        )