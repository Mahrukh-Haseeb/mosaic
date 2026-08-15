# tests/test_ai.py
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from src.pattern_detection import PatternDetector
from src.what_if_simulator import WhatIfSimulator
from src.database import Database

def test_pattern_detection():
    """Test that pattern detection works."""
    print("Testing Pattern Detection...")
    
    db = Database()
    df = db.get_check_ins("demo_user", days=30)
    
    if df.empty:
        print("❌ No data found")
        return False
    
    detector = PatternDetector(df)
    correlations = detector.compute_correlations()
    connections = detector.find_hidden_connections()
    trends = detector.detect_trends()
    
    print(f"✅ Found {len(connections)} connections")
    print(f"✅ Found {len(trends)} trends")
    return True

def test_what_if_simulator():
    """Test that the simulator works."""
    print("\nTesting What-If Simulator...")
    
    db = Database()
    df = db.get_check_ins("demo_user", days=30)
    
    if df.empty:
        print("❌ No data found")
        return False
    
    simulator = WhatIfSimulator(df)
    result = simulator.run_simulation('sleep', 8.0)
    
    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    
    print(f"✅ Wellness improvement: {result['predicted_impact']['wellness_score']['improvement']:.2f} points")
    return True

if __name__ == "__main__":
    print("Running AI Engine Tests...\n")
    
    success1 = test_pattern_detection()
    success2 = test_what_if_simulator()
    
    if success1 and success2:
        print("\n🎉 All tests passed!")
    else:
        print("\n❌ Some tests failed. Check the output above.")