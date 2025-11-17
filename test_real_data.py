#!/usr/bin/env python3
"""
Test script to verify multi-source NBA data collection
"""

import logging
from nba_data_collector import NBADataCollector

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_multi_source_data():
    """Test the multi-source data collection system"""
    print("🏀 Testing Multi-Source NBA Data Collection\n")
    
    # Initialize collector
    collector = NBADataCollector()
    
    # Test 1: Multi-source data collection
    print("1. Testing Multi-Source Data Collection...")
    try:
        all_data = collector.collect_all_data(use_sample_data=False)
        
        print(f"✅ Data collection completed!")
        print(f"📊 Data sources used: {len(all_data)}")
        
        for source, df in all_data.items():
            print(f"   - {source}: {len(df)} records")
        
        # Show sample data
        if 'current_season' in all_data and not all_data['current_season'].empty:
            current_data = all_data['current_season']
            
            print(f"\n📈 Sample Data Analysis:")
            print(f"   - Total players: {len(current_data)}")
            print(f"   - Columns available: {list(current_data.columns)}")
            
            # Show top scorers
            if 'PTS' in current_data.columns:
                top_scorers = current_data.nlargest(5, 'PTS')
                print(f"\n🏆 Top 5 Scorers:")
                for _, player in top_scorers.iterrows():
                    print(f"   {player['PLAYER_NAME']}: {player['PTS']:.1f} PPG")
            
            # Show top assist leaders
            if 'AST' in current_data.columns:
                top_assists = current_data.nlargest(5, 'AST')
                print(f"\n🎯 Top 5 Assist Leaders:")
                for _, player in top_assists.iterrows():
                    print(f"   {player['PLAYER_NAME']}: {player['AST']:.1f} APG")
            
            # Show shooting percentages
            if 'FG_PCT' in current_data.columns:
                top_shooters = current_data.nlargest(5, 'FG_PCT')
                print(f"\n📈 Top 5 FG% Leaders:")
                for _, player in top_shooters.iterrows():
                    print(f"   {player['PLAYER_NAME']}: {player['FG_PCT']:.3f} FG%")
            
            # Test 2: Data export
            print(f"\n2. Testing Data Export...")
            try:
                collector.save_to_csv(all_data)
                print("✅ Data exported to CSV successfully")
            except Exception as e:
                print(f"❌ Error exporting data: {e}")
        
    except Exception as e:
        print(f"❌ Error in data collection: {e}")

def test_individual_sources():
    """Test individual data sources"""
    print("\n🔧 Testing Individual Data Sources...")
    
    collector = NBADataCollector()
    
    # Test Basketball Reference
    print("\n1. Testing Basketball Reference...")
    try:
        br_data = collector.get_basketball_reference_stats("2023-24")
        if not br_data.empty:
            print(f"✅ Basketball Reference: {len(br_data)} players")
            print(f"   Sample: {br_data['PLAYER_NAME'].iloc[0]} - {br_data['PTS'].iloc[0]:.1f} PPG")
        else:
            print("❌ Basketball Reference: No data")
    except Exception as e:
        print(f"❌ Basketball Reference failed: {e}")
    
    # Test ESPN API
    print("\n2. Testing ESPN API...")
    try:
        espn_data = collector.get_espn_stats("2023-24")
        if not espn_data.empty:
            print(f"✅ ESPN API: {len(espn_data)} players")
            print(f"   Sample: {espn_data['PLAYER_NAME'].iloc[0]} - {espn_data['PTS'].iloc[0]:.1f} PPG")
        else:
            print("❌ ESPN API: No data")
    except Exception as e:
        print(f"❌ ESPN API failed: {e}")

if __name__ == "__main__":
    test_multi_source_data()
    test_individual_sources()
