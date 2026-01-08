"""
Summarisation module for generating structured learning summaries.
Creates study notes based on student profile and retrieved context.
"""

from typing import List, Dict


def generate_summary(student_profile: Dict, retrieved_chunks: List[str]) -> str:
    """
    Generate a structured learning summary based on student profile and retrieved chunks.
    
    The summary includes:
    - Topics covered by the student
    - Topics that need more attention (partially understood)
    - Key explanations in simple language
    - Short bullet points for quick review
    - Identified gaps in understanding
    
    Args:
        student_profile (Dict): Student knowledge profile containing:
            - topics_covered: List of topics discussed
            - confidence_level: "low", "medium", or "high"
            - understanding_indicators: List of positive/negative signals
            - message_count: Number of interactions
        retrieved_chunks (List[str]): Relevant text chunks from learning materials
    
    Returns:
        str: Formatted Markdown-style summary string
    """
    
    # Extract topics from student profile
    topics_covered = student_profile.get("topics_covered", [])
    confidence_level = student_profile.get("confidence_level", "low")
    understanding_indicators = student_profile.get("understanding_indicators", [])
    
    # Analyze understanding indicators to categorize topics
    recent_indicators = understanding_indicators[-10:] if len(understanding_indicators) > 10 else understanding_indicators
    positive_count = recent_indicators.count("positive")
    negative_count = recent_indicators.count("negative")
    
    # Determine which topics are well-understood vs partially understood
    # Simple heuristic: if confidence is high and positive signals dominate, topics are well-understood
    well_understood_topics = []
    partially_understood_topics = []
    
    if confidence_level == "high" and positive_count > negative_count * 2:
        well_understood_topics = topics_covered
    elif confidence_level == "medium" or (positive_count > negative_count):
        # Split topics: some understood, some need work
        well_understood_topics = topics_covered[:len(topics_covered)//2] if topics_covered else []
        partially_understood_topics = topics_covered[len(topics_covered)//2:] if topics_covered else []
    else:
        partially_understood_topics = topics_covered
    
    # Extract key points from retrieved chunks
    key_explanations = _extract_key_points(retrieved_chunks)
    
    # Identify gaps in understanding
    gaps = _identify_gaps(confidence_level, negative_count, positive_count, topics_covered)
    
    # Build the summary structure
    summary_parts = []
    
    # Header
    summary_parts.append("# Learning Summary\n")
    summary_parts.append("*Generated study notes based on your learning session*\n")
    
    # Topics covered section
    summary_parts.append("## Topics Covered\n")
    if topics_covered:
        for topic in topics_covered:
            status = "✓" if topic in well_understood_topics else "⚠"
            summary_parts.append(f"- {status} **{topic.title()}**")
        summary_parts.append("")
    else:
        summary_parts.append("*No specific topics identified yet.*\n")
    
    # Well-understood topics section
    if well_understood_topics:
        summary_parts.append("## Topics You Understand Well ✓\n")
        for topic in well_understood_topics:
            summary_parts.append(f"- **{topic.title()}**: You've demonstrated good understanding of this concept.")
        summary_parts.append("")
    
    # Partially understood topics section
    if partially_understood_topics:
        summary_parts.append("## Topics Needing More Practice ⚠\n")
        for topic in partially_understood_topics:
            summary_parts.append(f"- **{topic.title()}**: Review this topic and practice with examples.")
        summary_parts.append("")
    
    # Key explanations section
    if key_explanations:
        summary_parts.append("## Key Explanations\n")
        summary_parts.append("*Important concepts explained simply:*\n")
        for i, explanation in enumerate(key_explanations, 1):
            summary_parts.append(f"{i}. {explanation}")
        summary_parts.append("")
    
    # Quick review bullets section
    if retrieved_chunks:
        summary_parts.append("## Quick Review Points\n")
        review_points = _generate_review_bullets(retrieved_chunks, topics_covered)
        for point in review_points:
            summary_parts.append(f"- {point}")
        summary_parts.append("")
    
    # Gaps in understanding section
    if gaps:
        summary_parts.append("## Gaps in Understanding\n")
        summary_parts.append("*Areas to focus on for better comprehension:*\n")
        for gap in gaps:
            summary_parts.append(f"- {gap}")
        summary_parts.append("")
    
    # Study recommendations section
    summary_parts.append("## Study Recommendations\n")
    recommendations = _generate_recommendations(confidence_level, topics_covered, negative_count)
    for rec in recommendations:
        summary_parts.append(f"- {rec}")
    summary_parts.append("")
    
    # Footer
    summary_parts.append("---\n")
    summary_parts.append(f"*Confidence Level: {confidence_level.upper()}* | ")
    summary_parts.append(f"*Topics Discussed: {len(topics_covered)}* | ")
    summary_parts.append(f"*Session Interactions: {student_profile.get('message_count', 0)}*")
    
    return "\n".join(summary_parts)


def _extract_key_points(retrieved_chunks: List[str]) -> List[str]:
    """
    Extract key explanation points from retrieved chunks.
    Simplifies complex text into student-friendly explanations.
    
    Args:
        retrieved_chunks: List of text chunks from learning materials
    
    Returns:
        List of simplified key explanation strings
    """
    key_points = []
    
    for chunk in retrieved_chunks[:5]:  # Limit to top 5 chunks
        # Extract first sentence or key phrase (simple heuristic)
        sentences = chunk.split('.')
        if sentences:
            # Take the first complete sentence, limit length
            first_sentence = sentences[0].strip()
            if len(first_sentence) > 20 and len(first_sentence) < 200:
                key_points.append(first_sentence)
        
        # Also look for definition-like patterns (e.g., "X is Y", "X refers to Y")
        if " is " in chunk.lower() or " refers to " in chunk.lower():
            # Extract definition-like phrases
            for sentence in sentences[:2]:
                if (" is " in sentence.lower() or " refers to " in sentence.lower()) and len(sentence) < 150:
                    simplified = sentence.strip()
                    if simplified not in key_points:
                        key_points.append(simplified)
                        break
    
    return key_points[:5]  # Return top 5 key points


def _generate_review_bullets(retrieved_chunks: List[str], topics_covered: List[str]) -> List[str]:
    """
    Generate short bullet points for quick review.
    Focuses on exam-relevant information.
    
    Args:
        retrieved_chunks: List of text chunks
        topics_covered: List of topics the student has covered
    
    Returns:
        List of concise bullet point strings
    """
    bullets = []
    
    # Create topic-focused bullets
    for topic in topics_covered[:5]:  # Limit to 5 topics
        bullets.append(f"**{topic.title()}**: Core concept to remember for exams")
    
    # Extract important facts from chunks
    for chunk in retrieved_chunks[:3]:
        # Look for important patterns (numbers, definitions, comparisons)
        if any(keyword in chunk.lower() for keyword in ["important", "key", "essential", "remember"]):
            # Extract a short phrase
            words = chunk.split()[:15]  # First 15 words
            if len(words) > 5:
                bullet = " ".join(words) + "..."
                bullets.append(bullet)
    
    return bullets[:8]  # Return max 8 bullets


def _identify_gaps(confidence_level: str, negative_count: int, positive_count: int, topics_covered: List[str]) -> List[str]:
    """
    Identify gaps in student understanding based on profile data.
    
    Args:
        confidence_level: Student's overall confidence level
        negative_count: Number of negative understanding indicators
        positive_count: Number of positive understanding indicators
        topics_covered: List of topics covered
    
    Returns:
        List of gap description strings
    """
    gaps = []
    
    # Low confidence indicates general gaps
    if confidence_level == "low":
        gaps.append("Overall understanding needs strengthening - review fundamental concepts")
        if topics_covered:
            gaps.append(f"Need more practice with: {', '.join([t.title() for t in topics_covered])}")
    
    # More negative than positive signals indicates confusion
    if negative_count > positive_count:
        gaps.append("Some concepts are causing confusion - seek clarification on unclear points")
    
    # Missing topics might indicate incomplete coverage
    if len(topics_covered) == 0:
        gaps.append("Limited topic coverage - expand learning to cover more material")
    elif len(topics_covered) < 3:
        gaps.append("Narrow topic range - consider exploring related concepts")
    
    # Medium confidence suggests partial understanding
    if confidence_level == "medium":
        gaps.append("Mixed understanding - focus on areas where you feel less confident")
    
    return gaps


def _generate_recommendations(confidence_level: str, topics_covered: List[str], negative_count: int) -> List[str]:
    """
    Generate study recommendations based on student profile.
    Exam-oriented and actionable advice.
    
    Args:
        confidence_level: Student's confidence level
        topics_covered: List of topics covered
        negative_count: Number of negative understanding indicators
    
    Returns:
        List of recommendation strings
    """
    recommendations = []
    
    # Confidence-based recommendations
    if confidence_level == "low":
        recommendations.append("Start with foundational concepts and build up gradually")
        recommendations.append("Practice with simple examples before tackling complex problems")
    elif confidence_level == "medium":
        recommendations.append("Review topics where you had questions or confusion")
        recommendations.append("Test your understanding with practice problems")
    else:
        recommendations.append("Maintain your understanding with regular review")
        recommendations.append("Challenge yourself with advanced applications")
    
    # Topic-based recommendations
    if topics_covered:
        recommendations.append(f"Focus exam preparation on: {', '.join([t.title() for t in topics_covered[:3]])}")
    
    # Negative signals indicate need for review
    if negative_count > 0:
        recommendations.append("Revisit areas where you expressed confusion or uncertainty")
    
    # General exam tips
    recommendations.append("Create flashcards for key definitions and concepts")
    recommendations.append("Practice explaining concepts in your own words")
    
    return recommendations[:6]  # Return max 6 recommendations
