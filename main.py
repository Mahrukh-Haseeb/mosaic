# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime

# Import your AI modules (we'll create these next)
from src.pattern_detection import PatternDetector
from src.what_if_simulator import WhatIfSimulator
from src.insight_generator import InsightGenerator

# Load environment variables
load_dotenv()

# Initialize FastAPI
app = FastAPI(title="MOSAIC AI Engine", version="1.0.0")

# Allow frontend to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development; restrict later
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
    created_at: str

# --- Helper to Generate Demo Data ---
def generate_demo_data():
    """Creates 30 days of sample wellness data for testing."""
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
        'mood': np.random.randint(20, 95, 30)
    }
    
    # Add some correlations for realism
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
    Returns correlations, connections, and trends.
    """
    # For now, use demo data. Later, we'll fetch from Supabase.
    df = generate_demo_data()
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

@app.post("/ai/simulate")
async def run_simulation(request: SimulationRequest):
    """
    Simulate the impact of changing one wellness factor.
    Example: What if I sleep 8 hours instead of 5?
    """
    # Use demo data for now
    df = generate_demo_data()
    simulator = WhatIfSimulator(df)
    
    result = simulator.run_simulation(
        changed_factor=request.factor,
        new_value=request.new_value
    )
    
    return result

@app.get("/ai/insights")
async def get_insights(user_id: str = "demo_user"):
    """
    Generate personalized weekly insights using Gemini API.
    Requires GEMINI_API_KEY in .env file.
    """
    # Load demo data
    df = generate_demo_data()
    detector = PatternDetector(df)
    connections = detector.find_hidden_connections(threshold=0.5)
    avg_data = df.mean().to_dict()
    
    # Initialize insight generator
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "error": "GEMINI_API_KEY not found in .env file",
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

@app.get("/ai/health")
async def health_check():
    """Health check endpoint for the AI service."""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MOSAIC AI Engine"
    }

# --- Run the Server ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)