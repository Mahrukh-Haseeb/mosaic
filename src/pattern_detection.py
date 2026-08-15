# src/pattern_detection.py
import pandas as pd
import numpy as np
from scipy.stats import pearsonr

class PatternDetector:
    """
    Analyzes wellness data to find correlations, trends, and hidden connections.
    """
    
    def __init__(self, data: pd.DataFrame):
        """
        Initialize with user's check-in data.
        """
        self.factors = ['sleep', 'nutrition', 'movement', 'stress', 
                       'relationships', 'environment', 'fun', 'energy', 'mood']
        
        # Ensure all factors exist in the data
        available_factors = [f for f in self.factors if f in data.columns]
        self.data = data[available_factors].copy()
        
    def compute_correlations(self) -> pd.DataFrame:
        """Calculate correlation matrix between all wellness factors."""
        return self.data.corr()
    
    def find_hidden_connections(self, threshold: float = 0.6) -> list:
        """
        Find factor pairs with strong correlations (positive or negative).
        """
        corr_matrix = self.compute_correlations()
        connections = []
        factor_names = self.data.columns.tolist()
        
        for i in range(len(factor_names)):
            for j in range(i + 1, len(factor_names)):
                factor_a = factor_names[i]
                factor_b = factor_names[j]
                corr_value = corr_matrix.iloc[i, j]
                
                if abs(corr_value) >= threshold:
                    direction = "positive" if corr_value > 0 else "negative"
                    connections.append({
                        'factor_a': factor_a,
                        'factor_b': factor_b,
                        'correlation': round(corr_value, 2),
                        'direction': direction,
                        'strength': 'Strong' if abs(corr_value) > 0.7 else 'Moderate',
                        'description': f"Strong {direction} connection: When {factor_a} goes up, {factor_b} goes {'up' if direction == 'positive' else 'down'}."
                    })
        
        return connections
    
    def detect_trends(self) -> list:
        """
        Detect trends over time (e.g., "energy drops on Thursdays").
        """
        if 'created_at' not in self.data.columns:
            return []
        
        trends = []
        df_with_dow = self.data.copy()
        if 'created_at' in df_with_dow.columns:
            df_with_dow['day_of_week'] = pd.to_datetime(df_with_dow['created_at']).dt.day_name()
            
            for factor in ['energy', 'stress', 'mood']:
                if factor not in df_with_dow.columns:
                    continue
                    
                daily_avg = df_with_dow.groupby('day_of_week')[factor].mean()
                if len(daily_avg) < 3:
                    continue
                    
                min_day = daily_avg.idxmin()
                max_day = daily_avg.idxmax()
                range_val = daily_avg.max() - daily_avg.min()
                
                if range_val > 10:
                    trends.append({
                        'factor': factor,
                        'best_day': max_day,
                        'worst_day': min_day,
                        'range': round(range_val, 2),
                        'insight': f"Your {factor} is highest on {max_day} and lowest on {min_day}."
                    })
        
        return trends