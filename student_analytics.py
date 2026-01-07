import statistics

class StudentAnalyzer:
    def __init__(self):
        print("📊 Analytics Engine Initialized")

    def calculate_hidden_rating(self, history):
        """
        Input: history (dict) containing:
            - 'scores': list of integers (e.g., [10, 80, 90])
            - 'quizzes_taken': int
        Output: rating (0-100), insight (str)
        """
        scores = history.get('scores', [])
        
        # 1. HANDLE EDGE CASE: No Data
        if not scores:
            return 50, "New Student - No Data yet."

        # --- COMPONENT 1: RAW PERFORMANCE (60%) ---
        avg_score = statistics.mean(scores)
        perf_score = avg_score * 0.60

        # --- COMPONENT 2: TREND MOMENTUM (20%) ---
        if len(scores) > 1:
            recent = scores[-1]
            first = scores[0]
            improvement = recent - first
            
            if improvement > 0:
                trend_score = 20  # Max points for improving
            elif improvement == 0:
                trend_score = 15  # Good points for maintaining
            else:
                trend_score = 5   # Penalty for falling off
        else:
            trend_score = 15 

        # --- COMPONENT 3: CONSISTENCY (10%) ---
        if len(scores) > 1:
            stdev = statistics.stdev(scores)
            # Low stdev (consistent) = High score
            consistency_score = max(0, 10 - (stdev / 5)) 
        else:
            consistency_score = 10

        # --- COMPONENT 4: ENGAGEMENT (10%) ---
        count = history.get('quizzes_taken', 0)
        engagement_score = min(10, count * 2)

        # --- FINAL CALCULATION ---
        final_rating = perf_score + trend_score + consistency_score + engagement_score
        final_rating = max(0, min(100, int(final_rating)))

        # --- INSIGHTS ---
        if final_rating > 85:
            insight = "🌟 Top Performer"
        elif final_rating > 70:
            insight = "✅ Solid Student"
        elif final_rating > 50:
            insight = "⚠️ At Risk"
        else:
            insight = "🚨 Critical Attention Needed"

        return final_rating, insight