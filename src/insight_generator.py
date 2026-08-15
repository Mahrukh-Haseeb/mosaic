# src/insight_generator.py
import anthropic
import json
import os
import re

class InsightGenerator:
    """Uses Claude API to generate personalized wellness insights."""
    
    def __init__(self, api_key: str):
        """Initialize with Claude API key."""
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def generate_weekly_insights(self, averages: dict, patterns: list, max_insights: int = 5) -> list:
        """Generate personalized insights based on user's weekly data."""
        # Format averages for the prompt
        avg_text = "\n".join([f"- {k}: {v:.1f}" for k, v in averages.items() if k in ['sleep', 'nutrition', 'movement', 'stress', 'relationships', 'environment', 'fun']])
        
        # Format patterns for the prompt
        pattern_text = ""
        if patterns:
            for p in patterns[:5]:
                pattern_text += f"- {p.get('description', f'Connection between {p.get(\"factor_a\")} and {p.get(\"factor_b\")}')}\n"
        else:
            pattern_text = "No strong patterns detected yet. Keep logging your data!"
        
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
            response = self.client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=300,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )
            
            insights_text = response.content[0].text
            json_match = re.search(r'\[.*\]', insights_text, re.DOTALL)
            if json_match:
                insights = json.loads(json_match.group())
                return insights
            else:
                lines = [line.strip('- ').strip() for line in insights_text.split('\n') if line.strip()]
                return lines[:max_insights]
                
        except Exception as e:
            print(f"Insight generation error: {e}")
            return [
                f"Your {max(averages.items(), key=lambda x: x[1] if x[0] != 'stress' else -x[1])[0]} is a strength. Keep it up!",
                "Small daily habits create big changes over time.",
                "Remember to be kind to yourself. Progress, not perfection."
            ]