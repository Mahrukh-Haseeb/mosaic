# src/insight_generator.py
from google import genai
import json
import os
import re

class InsightGenerator:
    """Uses Gemini API to generate personalized wellness insights."""
    
    def __init__(self, api_key: str):
        """
        Initialize with Gemini API key.
        
        Args:
            api_key: Your Google AI Studio API key from https://ai.google.dev/
        """
        self.client = genai.Client(api_key=api_key)
        # gemini-2.5-flash is being retired (shutdown Oct 16, 2026) and was
        # already returning "model no longer available" errors ahead of that
        # date. gemini-3.6-flash is the current stable, generally-available
        # replacement as of August 2026.
        self.model_name = 'gemini-3.6-flash'
    
    def generate_weekly_insights(self, averages: dict, patterns: list, max_insights: int = 5) -> list:
        """
        Generate personalized insights based on user's weekly data.
        
        Args:
            averages: Dictionary of weekly averages for each factor
            patterns: List of significant correlations found
            max_insights: Maximum number of insights to generate
            
        Returns:
            List of insight strings
        """
        # Format averages for the prompt
        avg_text = "\n".join([f"- {k}: {v:.1f}" for k, v in averages.items() if k in ['sleep', 'nutrition', 'movement', 'stress', 'relationships', 'environment', 'fun', 'screen_time']])
        
        # Format patterns for the prompt
        pattern_text = ""
        if patterns:
            for p in patterns[:5]:
                factor_a = p.get('factor_a', 'unknown')
                factor_b = p.get('factor_b', 'unknown')
                desc = p.get('description', f'Connection between {factor_a} and {factor_b}')
                pattern_text += f"- {desc}\n"
        else:
            pattern_text = "No strong patterns detected yet. Keep logging your data!"
        
        # Build the prompt
        prompt = f"""Based on this user's weekly wellness data, generate {max_insights} personalized, actionable insights.

Weekly averages:
{avg_text}

Significant patterns found:
{pattern_text}

Requirements for each insight:
1. Be specific and reference their actual data
2. Be actionable (give concrete advice)
3. Be encouraging and non-judgmental
4. Focus on connections between factors
5. Keep it warm and human-sounding
6. Format as a JSON list of strings

Return ONLY a JSON list of insight strings, nothing else.
Example format: ["Insight 1", "Insight 2", ...]
"""
        
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            insights_text = response.text
            
            # Extract JSON from the response
            json_match = re.search(r'\[.*\]', insights_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                return insights
            else:
                # Fallback: split by line and clean up
                lines = [line.strip('- ').strip() for line in insights_text.split('\n') if line.strip()]
                return lines[:max_insights]
                
        except Exception as e:
            print(f"Insight generation error: {e}")
            # Return fallback insights
            return [
                f"Your {max(averages.items(), key=lambda x: x[1] if x[0] != 'stress' else -x[1])[0]} is a strength. Keep it up!",
                "Small daily habits create big changes over time.",
                "Remember to be kind to yourself. Progress, not perfection."
            ]