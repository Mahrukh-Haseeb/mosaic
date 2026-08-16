# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime
from supabase import create_client, Client

# Import your AI modules
from src.pattern_detection import PatternDetector
from src.what_if_simulator import WhatIfSimulator
from src.insight_generator import InsightGenerator

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="MOSAIC AI Engine", version="1.0.0")

# Initialize Supabase Client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_ANON_KEY")

if not supabase_url or not supabase_key:
    print("⚠️ Warning: Supabase credentials not found. Using mock data.")
    supabase = None
else:
    try:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("✅ Connected to Supabase")
    except Exception as e:
        print(f"❌ Supabase connection failed: {e}")
        supabase = None

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Request/Response Models ---
class SimulationRequest(BaseModel):
    factor: str
    new_value: float
    user_id: str

class CheckInData(BaseModel):
    sleep: float
    nutrition: float
    movement: float
    stress: float
    relationships: float
    environment: float
    fun: float
    energy: float
    mood: float
    screen_time: float
    created_at: str

# --- Helper to Fetch Real Data from Supabase ---
def fetch_user_check_ins(user_id: str, days: int = 30) -> pd.DataFrame:
    """Fetch real check-ins from Supabase for a given user."""
    if not supabase:
        print("⚠️ Supabase not connected. Using mock data.")
        return generate_mock_data()
    
    try:
        # Query Supabase
        response = supabase.table('check_ins')\
            .select('*')\
            .eq('user_id', user_id)\
            .order('created_at', ascending=True)\
            .execute()
        
        if response.data:
            df = pd.DataFrame(response.data)
            
            # Ensure all required columns exist
            required_cols = ['sleep', 'nutrition', 'movement', 'stress', 
                            'relationships', 'environment', 'fun', 'energy', 'mood', 'screen_time']
            for col in required_cols:
                if col not in df.columns:
                    df[col] = 50  # Default value if missing
            
            # Convert created_at to datetime
            if 'created_at' in df.columns:
                df['created_at'] = pd.to_datetime(df['created_at'])
            
            print(f"✅ Fetched {len(df)} check-ins for user {user_id}")
            return df
        else:
            print(f"⚠️ No check-ins found for user {user_id}. Using mock data.")
            return generate_mock_data()
            
    except Exception as e:
        print(f"❌ Error fetching from Supabase: {e}")
        return generate_mock_data()

def generate_mock_data() -> pd.DataFrame:
    """Generate mock data as fallback when Supabase is unavailable."""
    import numpy as np
    np.random.seed(42)
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    
    data = {
        'created_at': dates,
        'sleep': np.random.randint(4, 9, 30),
        'nutrition': np.random.randint(30, 95, 30),
        'movement': np.random.randint(10, 80, 30),
        'stress': np.random.randint(10, 90, 30),
        'relationships': np.random.randint(30, 95, 30),
        'environment': np.random.randint(20, 90, 30),
        'fun': np.random.randint(10, 90, 30),
        'energy': np.random.randint(20, 90, 30),
        'mood': np.random.randint(20, 95, 30),
        'screen_time': np.random.randint(2, 12, 30)
    }
    
    # Add correlations for realism
    for i in range(len(data['sleep'])):
        if data['sleep'][i] < 6:
            data['stress'][i] = min(95, data['stress'][i] + 20)
            data['energy'][i] = max(20, data['energy'][i] - 15)
        elif data['sleep'][i] > 7:
            data['stress'][i] = max(10, data['stress'][i] - 15)
            data['energy'][i] = min(90, data['energy'][i] + 10)
    
    return pd.DataFrame(data)

# --- API Endpoints ---

@app.get("/")
async def root():
    return {"message": "MOSAIC AI Engine is running!", "status": "healthy"}

@app.get("/ai/patterns")
async def get_patterns(user_id: str = "demo_user"):
    """
    Analyze user's check-in data and find hidden connections between wellness factors.
    """
    try:
        df = fetch_user_check_ins(user_id)
        
        if df.empty:
            return {
                "error": "No data found for this user. Please log some check-ins first.",
                "user_id": user_id,
                "connections": [],
                "total_patterns": 0
            }
        
        detector = PatternDetector(df)
        
        correlations = detector.compute_correlations().to_dict()
        connections = detector.find_hidden_connections(threshold=0.5)
        trends = detector.detect_trends()
        
        return {
            "user_id": user_id,
            "correlations": correlations,
            "connections": connections,
            "trends": trends,
            "total_patterns": len(connections)
        }
    except Exception as e:
        print(f"Error in /ai/patterns: {e}")
        return {
            "error": "Failed to analyze patterns",
            "message": str(e),
            "connections": [],
            "total_patterns": 0
        }

@app.post("/ai/simulate")
async def run_simulation(request: SimulationRequest):
    """
    Simulate the impact of changing one wellness factor.
    """
    try:
        df = fetch_user_check_ins(request.user_id)
        
        if df.empty:
            return {
                "error": "No data found for this user. Please log some check-ins first."
            }
        
        simulator = WhatIfSimulator(df)
        result = simulator.run_simulation(
            changed_factor=request.factor,
            new_value=request.new_value
        )
        
        return result
    except Exception as e:
        print(f"Error in /ai/simulate: {e}")
        return {
            "error": "Simulation failed",
            "message": str(e)
        }

@app.get("/ai/insights")
async def get_insights(user_id: str = "demo_user"):
    """
    Generate personalized weekly insights using Gemini API.
    """
    try:
        df = fetch_user_check_ins(user_id)
        
        if df.empty:
            return {
                "error": "No data found for this user. Please log some check-ins first.",
                "user_id": user_id,
                "insights": ["Log your wellness data to get personalized insights."]
            }
        
        detector = PatternDetector(df)
        connections = detector.find_hidden_connections(threshold=0.5)
        avg_data = df.mean().to_dict()
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return {
                "error": "GEMINI_API_KEY not found",
                "weekly_averages": avg_data,
                "insights": ["Add your Gemini API key to get personalized insights."]
            }
        
        generator = InsightGenerator(api_key)
        insights = generator.generate_weekly_insights(avg_data, connections)
        
        return {
            "user_id": user_id,
            "weekly_averages": avg_data,
            "insights": insights
        }
    except Exception as e:
        print(f"Error in /ai/insights: {e}")
        # Always return fallback insights
        return {
            "error": "AI service temporarily unavailable",
            "weekly_averages": avg_data if 'avg_data' in locals() else {},
            "insights": [
                "Your sleep and stress levels are connected. Try a small recovery action today.",
                "Movement can boost your mood. A short walk could help.",
                "Your social connections matter. Reach out to someone you value.",
                "Small consistent actions create lasting change.",
                "Your environment affects your wellbeing. Create a calm space."
            ]
        }

@app.get("/ai/health")
async def health_check():
    """Health check endpoint for the AI service."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MOSAIC AI Engine",
        "supabase_connected": supabase is not None
    }

# --- Run the Server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)