#!/usr/bin/env python3
"""
Test script for NBA Analytics API
Run this to verify all functionality works correctly
"""

import requests
import json
import time
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check passed: {data}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_root():
    """Test the root endpoint"""
    print("\n🔍 Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Root endpoint working: {data['message']}")
            return True
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
        return False

def test_players_list():
    """Test the players list endpoint"""
    print("\n🔍 Testing players list endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/players?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Players list working: {data['total_players']} players found")
            print(f"   Sample players: {[p['PLAYER_NAME'] for p in data['players'][:3]]}")
            return True
        else:
            print(f"❌ Players list failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Players list error: {e}")
        return False

def test_hot_takes():
    """Test the hot takes endpoint"""
    print("\n🔍 Testing hot takes endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/hot-takes?num_takes=2")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Hot takes working: {len(data)} hot takes generated")
            if data:
                print(f"   Sample hot take: {data[0].get('statement', 'N/A')[:100]}...")
            return True
        else:
            print(f"❌ Hot takes failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Hot takes error: {e}")
        return False

def test_player_lookup():
    """Test the player lookup endpoint"""
    print("\n🔍 Testing player lookup endpoint...")
    try:
        # Test with a common player name
        response = requests.get(f"{BASE_URL}/player-lookup/LeBron James")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Player lookup working: {data['player_name']}")
            print(f"   Offensive Score: {data['calculated_scores']['offensive_score']}")
            print(f"   Defensive Score: {data['calculated_scores']['defensive_score']}")
            return True
        else:
            print(f"❌ Player lookup failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Player lookup error: {e}")
        return False

def test_advanced_analysis():
    """Test the advanced analysis endpoint"""
    print("\n🔍 Testing advanced analysis endpoint...")
    try:
        # Test league-wide analysis
        response = requests.get(f"{BASE_URL}/advanced-analysis")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Advanced analysis working: {data['analysis_scope']}")
            print(f"   AI insights length: {len(data['ai_insights'])} characters")
            return True
        else:
            print(f"❌ Advanced analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Advanced analysis error: {e}")
        return False

def test_team_analysis():
    """Test team-specific analysis"""
    print("\n🔍 Testing team analysis...")
    try:
        response = requests.get(f"{BASE_URL}/advanced-analysis?team=LAL")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Team analysis working: {data['analysis_scope']}")
            return True
        else:
            print(f"❌ Team analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Team analysis error: {e}")
        return False

def test_data_collection():
    """Test the data collection endpoint"""
    print("\n🔍 Testing data collection endpoint...")
    try:
        response = requests.post(f"{BASE_URL}/collect-data?use_sample=true")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Data collection working: {data['message']}")
            return True
        else:
            print(f"❌ Data collection failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Data collection error: {e}")
        return False

def run_all_tests():
    """Run all tests and provide summary"""
    print("🚀 Starting NBA Analytics API Tests\n")
    
    tests = [
        ("Health Check", test_health),
        ("Root Endpoint", test_root),
        ("Players List", test_players_list),
        ("Hot Takes", test_hot_takes),
        ("Player Lookup", test_player_lookup),
        ("Advanced Analysis", test_advanced_analysis),
        ("Team Analysis", test_team_analysis),
        ("Data Collection", test_data_collection),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Print summary
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        print("🎉 All tests passed! The API is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the server logs for details.")
    
    return passed == len(results)

if __name__ == "__main__":
    # Wait a moment for server to start if needed
    print("⏳ Waiting 3 seconds for server to be ready...")
    time.sleep(3)
    
    success = run_all_tests()
    exit(0 if success else 1)
