"""
The 'Cortex' of the application.
Decides the Pedagogical Strategy based on user metrics.
"""

class AdaptiveEngine:
    
    @staticmethod
    def derive_pedagogical_strategy(student_data):
        """
        Maps Mastery Score -> Teaching Strategy
        """
        score = student_data['mastery']
        
        if score < 45:
            return {
                "strategy": "SCAFFOLDING",
                "instruction": (
                    "The user is struggling (Novice). Use the 'Scaffolding' technique:\n"
                    "1. Break down every concept into atomic parts.\n"
                    "2. Use concrete analogies (e.g., 'like a water pipe').\n"
                    "3. Verify understanding after every paragraph.\n"
                    "4. Tone: Encouraging, patient, simple vocabulary."
                )
            }
        elif score < 75:
            return {
                "strategy": "APPLICATION",
                "instruction": (
                    "The user is competent (Intermediate). Use the 'Application' technique:\n"
                    "1. Briefly define concepts, then immediately switch to real-world use cases.\n"
                    "2. Connect new information to previous context.\n"
                    "3. Tone: Professional, practical, engaging."
                )
            }
        else:
            return {
                "strategy": "SYNTHESIS",
                "instruction": (
                    "The user is an expert (Master). Use the 'Synthesis' technique:\n"
                    "1. Skip definitions; assume foundational knowledge.\n"
                    "2. Focus on edge cases, limitations, and system architecture.\n"
                    "3. Use high-density technical jargon.\n"
                    "4. Tone: Academic, concise, peer-to-peer."
                )
            }

    @staticmethod
    def get_dashboard_metrics(student_data):
        """
        Returns data for the UI visualization.
        """
        return {
            "score": student_data['mastery'],
            "status": "Critical" if student_data['mastery'] < 40 else "Stable" if student_data['mastery'] < 80 else "Optimal",
            "next_step": "Foundational Review" if student_data['mastery'] < 50 else "Complex Problem Solving"
        }