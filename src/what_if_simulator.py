# src/what_if_simulator.py
import pandas as pd
import numpy as np

class WhatIfSimulator:
    """
    Simulates the impact of changing wellness factors on overall wellbeing.
    """
    
    def __init__(self, history: pd.DataFrame):
        """
        Initialize with user's historical check-in data.
        """
        self.factors = ['sleep', 'nutrition', 'movement', 'stress', 
                       'relationships', 'environment', 'fun']
        self.history = history[self.factors].copy() if all(f in history.columns for f in self.factors) else history
        
        # Calculate correlations from historical data
        if len(self.history) > 1:
            self.correlations = self.history.corr()
        else:
            self.correlations = pd.DataFrame(1.0, index=self.factors, columns=self.factors)
        
    def predict_impact(self, changed_factor: str, new_value: float) -> dict:
        """
        Predict new values for all factors when one factor changes.
        """
        current_avg = self.history.mean().to_dict()
        
        if changed_factor not in current_avg:
            return {"error": f"Factor '{changed_factor}' not found"}
        
        current_val = current_avg.get(changed_factor, 50)
        if abs(new_value - current_val) < 0.1:
            return current_avg
        
        predicted = {}
        for factor in self.factors:
            if factor == changed_factor:
                predicted[factor] = new_value
            else:
                corr = self.correlations.loc[changed_factor, factor] if changed_factor in self.correlations.index and factor in self.correlations.columns else 0
                change_ratio = (new_value - current_val) / (current_val + 0.01)
                impact = change_ratio * corr * 0.3
                new_val = current_avg.get(factor, 50) * (1 + impact)
                
                if factor == 'stress':
                    new_val = current_avg.get(factor, 50) - (new_value - current_val) * 0.5
                
                if factor == 'sleep':
                    new_val = max(2, min(12, new_val))
                else:
                    new_val = max(0, min(100, new_val))
                
                predicted[factor] = new_val
        
        return predicted
    
    def calculate_wellness_score(self, factors: dict) -> float:
        """Calculate overall wellness score (0-100) from factor values."""
        weights = {
            'sleep': 1.2,
            'nutrition': 1.0,
            'movement': 1.1,
            'stress': 1.3,
            'relationships': 1.0,
            'environment': 0.8,
            'fun': 0.9
        }
        
        score = 0
        total_weight = 0
        
        for factor, value in factors.items():
            if factor in weights and factor in factors:
                val = 100 - value if factor == 'stress' else value
                score += val * weights[factor]
                total_weight += weights[factor]
        
        return score / total_weight if total_weight > 0 else 50
    
    def run_simulation(self, changed_factor: str, new_value: float) -> dict:
        """Complete simulation with predicted impacts and wellness score."""
        predicted = self.predict_impact(changed_factor, new_value)
        
        if 'error' in predicted:
            return predicted
        
        current_avg = self.history.mean().to_dict()
        current_wellness = self.calculate_wellness_score(current_avg)
        predicted_wellness = self.calculate_wellness_score(predicted)
        
        changes = {}
        for factor in self.factors:
            if factor in predicted and factor in current_avg:
                current_val = current_avg.get(factor, 0)
                predicted_val = predicted.get(factor, 0)
                delta = predicted_val - current_val
                
                if abs(delta) > 0.01:
                    changes[factor] = {
                        'current': round(current_val, 2),
                        'predicted': round(predicted_val, 2),
                        'delta': round(delta, 2),
                        'percent_change': round((delta / (current_val + 0.01)) * 100, 2)
                    }
        
        return {
            'factors_changed': {changed_factor: new_value},
            'predicted_impact': {
                'current_state': {k: round(v, 2) for k, v in current_avg.items() if k in self.factors},
                'predicted_state': {k: round(v, 2) for k, v in predicted.items() if k in self.factors},
                'changes': changes,
                'wellness_score': {
                    'current': round(current_wellness, 2),
                    'predicted': round(predicted_wellness, 2),
                    'improvement': round(predicted_wellness - current_wellness, 2)
                }
            }
        }