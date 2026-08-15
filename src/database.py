# src/database.py
import pandas as pd
from datetime import datetime, timedelta
import os
from supabase import create_client

class Database:
    """Handles database operations for the AI engine."""
    
    def __init__(self):
        """Initialize database connection."""
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.supabase = None
        
        if self.supabase_url and self.supabase_key:
            try:
                self.supabase = create_client(self.supabase_url, self.supabase_key)
                print("Connected to Supabase")
            except Exception as e:
                print(f"Supabase connection failed: {e}")
                self.supabase = None
        else:
            print("No Supabase credentials found. Using mock data.")
    
    def get_check_ins(self, user_id: str, days: int = 30) -> pd.DataFrame:
        """Fetch user's check-in data from the database."""
        if self.supabase:
            try:
                cutoff = datetime.now() - timedelta(days=days)
                response = self.supabase.table('check_ins')\
                    .select('*')\
                    .eq('user_id', user_id)\
                    .gte('created_at', cutoff.isoformat())\
                    .order('created_at', ascending=True)\
                    .execute()
                
                if response.data:
                    return pd.DataFrame(response.data)
                else:
                    return pd.DataFrame()
            except Exception as e:
                print(f"Error fetching from Supabase: {e}")
                return pd.DataFrame()
        else:
            return self._generate_mock_data(days)
    
    def _generate_mock_data(self, days: int = 30) -> pd.DataFrame:
        """Generate mock check-in data for testing."""
        import numpy as np
        np.random.seed(42)
        
        dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
        
        data = {
            'created_at': dates,
            'sleep': np.random.randint(4, 9, days),
            'nutrition': np.random.randint(30, 95, days),
            'movement': np.random.randint(10, 80, days),
            'stress': np.random.randint(10, 90, days),
            'relationships': np.random.randint(30, 95, days),
            'environment': np.random.randint(20, 90, days),
            'fun': np.random.randint(10, 90, days),
            'energy': np.random.randint(20, 90, days),
            'mood': np.random.randint(20, 95, days)
        }
        
        for i in range(len(data['sleep'])):
            if data['sleep'][i] < 6:
                data['stress'][i] = min(95, data['stress'][i] + 20)
                data['energy'][i] = max(20, data['energy'][i] - 15)
            elif data['sleep'][i] > 7:
                data['stress'][i] = max(10, data['stress'][i] - 15)
                data['energy'][i] = min(90, data['energy'][i] + 10)
        
        return pd.DataFrame(data)