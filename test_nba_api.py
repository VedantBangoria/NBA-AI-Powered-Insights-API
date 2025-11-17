#!/usr/bin/env python3
"""
Test script to verify NBA Stats API integration with enhanced fallback
"""

import logging
from nba_data_collector import NBADataCollector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_nba_api():
    """Test the NBA Stats API integration with fallback"""
    print("🏀 Testing NBA Stats API Integration with Enhanced Fallback\n")
    
    # Initialize collector
    collector = NBADataCollector()
    
    # Test 1: API Connection
    print("1. Testing API Connection...")
    if collector.test_api_connection():
        print("✅ API connection successful!")
    else:
        print("❌ API connection failed!")
        print("   This is normal - NBA Stats API has strict anti-bot measures")
        print("   The system will use enhanced sample data instead\n")
    
    # Test 2: Full Data Collection (with fallback)
    print("2. Testing Full Data Collection with Fallback...")
    try:
        all_data = collector.collect_all_data(use_sample_data=False)
        print(f"✅ Collected data from {len(all_data)} sources:")
        for source, df in all_data.items():
            print(f"   - {source}: {len(df)} records")
            
        # Show sample of the data
        if 'current_season' in all_data and not all_data['current_season'].empty:
            print(f"\n📊 Sample Data (first 5 players):")
            sample_data = all_data['current_season'].head(5)
            for _, player in sample_data.iterrows():
                print(f"   {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}): "
                      f"{player['PTS']:.1f} PPG, {player['AST']:.1f} APG, {player['REB']:.1f} RPG")
        
        # Test 3: Save to CSV
        print(f"\n3. Testing Data Export...")
        try:
            collector.save_to_csv(all_data)
            print("✅ Data saved to CSV successfully")
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            
    except Exception as e:
        print(f"❌ Error in full data collection: {e}")
        print("   Trying sample data fallback...")
        try:
            all_data = collector.collect_all_data(use_sample_data=True)
            print(f"✅ Sample data collected: {len(all_data)} sources")
        except Exception as e2:
            print(f"❌ Sample data also failed: {e2}")

def test_enhanced_sample_data():
    """Test the enhanced sample data generation"""
    print("\n🔧 Testing Enhanced Sample Data Generation...")
    
    collector = NBADataCollector()
    
    try:
        # Test enhanced sample data
        enhanced_data = collector.create_enhanced_sample_data()
        
        print(f"✅ Enhanced sample data created with {len(enhanced_data)} players")
        print(f"📊 Data columns: {list(enhanced_data.columns)}")
        
        # Show some realistic stats
        print(f"\n🏆 Top 5 Scorers:")
        top_scorers = enhanced_data.nlargest(5, 'PTS')
        for _, player in top_scorers.iterrows():
            print(f"   {player['PLAYER_NAME']}: {player['PTS']:.1f} PPG")
        
        print(f"\n🎯 Top 5 Assist Leaders:")
        top_assists = enhanced_data.nlargest(5, 'AST')
        for _, player in top_assists.iterrows():
            print(f"   {player['PLAYER_NAME']}: {player['AST']:.1f} APG")
        
        print(f"\n📈 Shooting Percentages (Top 5 FG%):")
        top_shooters = enhanced_data.nlargest(5, 'FG_PCT')
        for _, player in top_shooters.iterrows():
            print(f"   {player['PLAYER_NAME']}: {player['FG_PCT']:.3f} FG%")
            
    except Exception as e:
        print(f"❌ Error creating enhanced sample data: {e}")

if __name__ == "__main__":
    test_nba_api()
    test_enhanced_sample_data()
