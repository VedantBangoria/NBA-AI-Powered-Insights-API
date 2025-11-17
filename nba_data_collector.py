import requests
import pandas as pd
import logging
from typing import Dict, List, Optional
from datetime import datetime
import os
import time
import json
from bs4 import BeautifulSoup
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBADataCollector:
    def __init__(self):
        """Initialize NBA Data Collector with multiple API endpoints and headers"""
        # NBA Stats API base URL
        self.nba_stats_base = "https://stats.nba.com/stats"
        
        # Basketball Reference base URL
        self.basketball_ref_base = "https://www.basketball-reference.com"
        
        # ESPN API base URL
        self.espn_api_base = "https://site.api.espn.com/apis/site/v2/sports/basketball/nba"
        
        # Enhanced headers for NBA Stats API (more realistic browser headers)
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://www.nba.com/stats/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'DNT': '1',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"'
        }
        
        # Session for better connection handling
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
        # Enhanced rate limiting and retry settings
        self.request_delay = 2.0  # Increased delay between requests
        self.max_retries = 3
        self.timeout = 15  # Increased timeout
        
    def _make_api_request(self, url: str, params: Dict = None) -> Optional[Dict]:
        """Make API request with proper error handling, rate limiting, and retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Making request to: {url} (attempt {attempt + 1}/{self.max_retries})")
                logger.info(f"Parameters: {params}")
                
                # Add delay to respect rate limits (longer delay for retries)
                delay = self.request_delay * (attempt + 1)
                time.sleep(delay)
                
                response = self.session.get(url, params=params, timeout=self.timeout)
                
                # Log response status
                logger.info(f"Response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    logger.info(f"Successfully retrieved data with {len(data.get('resultSets', []))} result sets")
                    return data
                elif response.status_code == 429:
                    logger.warning(f"Rate limited (429). Waiting {delay * 2} seconds before retry...")
                    time.sleep(delay * 2)
                    continue
                elif response.status_code == 403:
                    logger.error("Access forbidden (403). NBA Stats API may have blocked the request.")
                    return None
                else:
                    logger.error(f"API request failed with status {response.status_code}")
                    logger.error(f"Response text: {response.text[:500]}")
                    if attempt < self.max_retries - 1:
                        continue
                    return None
                    
            except requests.exceptions.Timeout:
                logger.warning(f"Request timed out (attempt {attempt + 1}). Retrying...")
                if attempt < self.max_retries - 1:
                    continue
                logger.error("All retry attempts timed out")
                return None
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error: {e}")
                return None
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {e}")
                return None
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                return None
        
        return None

    def get_current_season_players(self) -> pd.DataFrame:
        """Get current season per-game stats from NBA Stats API"""
        logger.info("Fetching current season player stats...")
        
        url = f"{self.nba_stats_base}/leaguedashplayerstats"
        params = {
            'PerMode': 'PerGame',
            'Season': '2023-24',
            'SeasonType': 'Regular Season',
            'LeagueID': '00',  # NBA
            'MeasureType': 'Base',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Outcome': '',
            'Location': '',
            'Month': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'OpponentTeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'TeamID': '0',
            'Conference': '',
            'Division': '',
            'GameSegment': '',
            'Period': '0',
            'ShotClockRange': '',
            'LastNGames': '0'
        }
        
        data = self._make_api_request(url, params)
        
        if data and 'resultSets' in data and len(data['resultSets']) > 0:
            result_set = data['resultSets'][0]
            headers = result_set['headers']
            rows = result_set['rowSet']
            
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"Retrieved {len(df)} current season player records")
            return df
        else:
            logger.warning("No data retrieved from NBA Stats API")
            return pd.DataFrame()

    def get_advanced_stats(self) -> pd.DataFrame:
        """Get advanced per-game stats from NBA Stats API"""
        logger.info("Fetching advanced player stats...")
        
        url = f"{self.nba_stats_base}/leaguedashplayerstats"
        params = {
            'PerMode': 'PerGame',
            'Season': '2023-24',
            'SeasonType': 'Regular Season',
            'LeagueID': '00',
            'MeasureType': 'Advanced',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Outcome': '',
            'Location': '',
            'Month': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'OpponentTeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'TeamID': '0',
            'Conference': '',
            'Division': '',
            'GameSegment': '',
            'Period': '0',
            'ShotClockRange': '',
            'LastNGames': '0'
        }
        
        data = self._make_api_request(url, params)
        
        if data and 'resultSets' in data and len(data['resultSets']) > 0:
            result_set = data['resultSets'][0]
            headers = result_set['headers']
            rows = result_set['rowSet']
            
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"Retrieved {len(df)} advanced stats records")
            return df
        else:
            logger.warning("No advanced stats data retrieved")
            return pd.DataFrame()

    def get_defensive_stats(self) -> pd.DataFrame:
        """Get defensive per-game stats from NBA Stats API"""
        logger.info("Fetching defensive player stats...")
        
        url = f"{self.nba_stats_base}/leaguedashplayerstats"
        params = {
            'PerMode': 'PerGame',
            'Season': '2023-24',
            'SeasonType': 'Regular Season',
            'LeagueID': '00',
            'MeasureType': 'Defense',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Outcome': '',
            'Location': '',
            'Month': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'OpponentTeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'TeamID': '0',
            'Conference': '',
            'Division': '',
            'GameSegment': '',
            'Period': '0',
            'ShotClockRange': '',
            'LastNGames': '0'
        }
        
        data = self._make_api_request(url, params)
        
        if data and 'resultSets' in data and len(data['resultSets']) > 0:
            result_set = data['resultSets'][0]
            headers = result_set['headers']
            rows = result_set['rowSet']
            
            df = pd.DataFrame(rows, columns=headers)
            logger.info(f"Retrieved {len(df)} defensive stats records")
            return df
        else:
            logger.warning("No defensive stats data retrieved")
            return pd.DataFrame()

    def get_historical_data(self, seasons: List[str] = None) -> pd.DataFrame:
        """Get historical data for multiple seasons"""
        if seasons is None:
            seasons = ['2022-23', '2021-22', '2020-21']
        
        logger.info(f"Fetching historical data for seasons: {seasons}")
        
        all_data = []
        
        for season in seasons:
            logger.info(f"Fetching data for season: {season}")
            
            url = f"{self.nba_stats_base}/leaguedashplayerstats"
            params = {
                'PerMode': 'PerGame',
                'Season': season,
                'SeasonType': 'Regular Season',
                'LeagueID': '00',
                'MeasureType': 'Base',
                'PlusMinus': 'N',
                'PaceAdjust': 'N',
                'Rank': 'N',
                'Outcome': '',
                'Location': '',
                'Month': '0',
                'SeasonSegment': '',
                'DateFrom': '',
                'DateTo': '',
                'OpponentTeamID': '0',
                'VsConference': '',
                'VsDivision': '',
                'TeamID': '0',
                'Conference': '',
                'Division': '',
                'GameSegment': '',
                'Period': '0',
                'ShotClockRange': '',
                'LastNGames': '0'
            }
            
            data = self._make_api_request(url, params)
            
            if data and 'resultSets' in data and len(data['resultSets']) > 0:
                result_set = data['resultSets'][0]
                headers = result_set['headers']
                rows = result_set['rowSet']
                
                df = pd.DataFrame(rows, columns=headers)
                df['SEASON'] = season  # Add season column
                all_data.append(df)
                logger.info(f"Retrieved {len(df)} records for {season}")
            else:
                logger.warning(f"No data retrieved for season {season}")
        
        if all_data:
            combined_df = pd.concat(all_data, ignore_index=True)
            logger.info(f"Combined historical data: {len(combined_df)} total records")
            return combined_df
        else:
            logger.warning("No historical data retrieved")
            return pd.DataFrame()
    
    def create_sample_data(self) -> pd.DataFrame:
        """Create sample NBA player data for testing when APIs are unavailable"""
        logger.info("Creating sample NBA player data...")
        
        # Create exactly 50 players with consistent data
        players = [
            'LeBron James', 'Kevin Durant', 'Stephen Curry', 'Giannis Antetokounmpo', 'Nikola Jokic',
            'Joel Embiid', 'Luka Doncic', 'Damian Lillard', 'Jayson Tatum', 'Devin Booker',
            'Anthony Davis', 'Jimmy Butler', 'Kawhi Leonard', 'Paul George', 'Russell Westbrook',
            'Chris Paul', 'Kyrie Irving', 'Bradley Beal', 'Donovan Mitchell', 'Zion Williamson',
            'Ja Morant', 'Trae Young', 'De\'Aaron Fox', 'Shai Gilgeous-Alexander', 'Tyrese Haliburton',
            'Bam Adebayo', 'Julius Randle', 'Pascal Siakam', 'Domantas Sabonis', 'Rudy Gobert',
            'Karl-Anthony Towns', 'Anthony Edwards', 'Cade Cunningham', 'Jalen Green', 'Scottie Barnes',
            'Franz Wagner', 'Evan Mobley', 'Josh Giddey', 'Jalen Suggs', 'Jonathan Kuminga',
            'Keegan Murray', 'Paolo Banchero', 'Jabari Smith Jr.', 'Chet Holmgren', 'Victor Wembanyama',
            'Scoot Henderson', 'Brandon Miller', 'Amen Thompson', 'Ausar Thompson', 'Cam Whitmore'
        ]
        
        teams = ['LAL', 'PHX', 'GSW', 'MIL', 'DEN', 'PHI', 'DAL', 'MIL', 'BOS', 'PHX',
                'LAL', 'MIA', 'LAC', 'LAC', 'LAC', 'GSW', 'DAL', 'PHX', 'CLE', 'NOP',
                'MEM', 'ATL', 'SAC', 'OKC', 'IND', 'MIA', 'NYK', 'TOR', 'SAC', 'MIN',
                'MIN', 'MIN', 'DET', 'HOU', 'TOR', 'ORL', 'CLE', 'OKC', 'ORL', 'GSW',
                'SAC', 'ORL', 'HOU', 'OKC', 'SAS', 'POR', 'CHA', 'HOU', 'DET', 'DET']
        
        # Create data with consistent lengths
        data = []
        for i in range(50):
            player_data = {
                'PLAYER_ID': i + 1,
                'PLAYER_NAME': players[i],
                'TEAM_ABBREVIATION': teams[i],
                'AGE': 25 + (i % 15),  # Ages 25-39
                'GP': 60 + (i % 20),   # Games 60-79
                'MIN': 30.0 + (i % 10), # Minutes 30-39
                'PTS': 15.0 + (i % 20), # Points 15-34
                'REB': 5.0 + (i % 8),   # Rebounds 5-12
                'AST': 3.0 + (i % 8),   # Assists 3-10
                'STL': 0.5 + (i % 2),   # Steals 0.5-2.5
                'BLK': 0.3 + (i % 2),   # Blocks 0.3-2.3
                'TOV': 2.0 + (i % 3),   # Turnovers 2-4
                'FG_PCT': 0.40 + (i % 20) * 0.01,  # FG% 0.40-0.59
                'FG3_PCT': 0.30 + (i % 20) * 0.01, # 3P% 0.30-0.49
                'FT_PCT': 0.70 + (i % 20) * 0.01,  # FT% 0.70-0.89
                'DREB': 3.0 + (i % 6),  # Defensive rebounds 3-8
                'PF': 2.0 + (i % 3),    # Personal fouls 2-4
                'EFF': 15.0 + (i % 15)  # Efficiency 15-29
            }
            data.append(player_data)
        
        df = pd.DataFrame(data)
        logger.info(f"Created sample data with {len(df)} players")
        return df
    
    def test_api_connection(self) -> bool:
        """Test if NBA Stats API is accessible with enhanced error handling"""
        logger.info("Testing NBA Stats API connection...")
        
        # Try a simpler endpoint first
        test_url = "https://stats.nba.com/stats/leaguedashplayerstats"
        test_params = {
            'PerMode': 'PerGame',
            'Season': '2023-24',
            'SeasonType': 'Regular Season',
            'LeagueID': '00',
            'MeasureType': 'Base',
            'PlusMinus': 'N',
            'PaceAdjust': 'N',
            'Rank': 'N',
            'Outcome': '',
            'Location': '',
            'Month': '0',
            'SeasonSegment': '',
            'DateFrom': '',
            'DateTo': '',
            'OpponentTeamID': '0',
            'VsConference': '',
            'VsDivision': '',
            'TeamID': '0',
            'Conference': '',
            'Division': '',
            'GameSegment': '',
            'Period': '0',
            'ShotClockRange': '',
            'LastNGames': '0'
        }
        
        try:
            # First, try a simple connection test
            logger.info("Testing basic connectivity...")
            response = self.session.get("https://stats.nba.com", timeout=5)
            if response.status_code != 200:
                logger.warning(f"Basic connectivity test failed: {response.status_code}")
            
            # Now test the actual API endpoint
            logger.info("Testing API endpoint...")
            response = self.session.get(test_url, params=test_params, timeout=self.timeout)
            
            if response.status_code == 200:
                logger.info("✅ NBA Stats API connection successful")
                return True
            elif response.status_code == 429:
                logger.warning("⚠️ NBA Stats API is rate limiting requests")
                return False
            elif response.status_code == 403:
                logger.error("❌ NBA Stats API access forbidden - may require authentication")
                return False
            else:
                logger.warning(f"⚠️ NBA Stats API returned status {response.status_code}")
                return False
                
        except requests.exceptions.Timeout:
            logger.error("❌ NBA Stats API connection timed out - server may be overloaded")
            return False
        except requests.exceptions.ConnectionError as e:
            logger.error(f"❌ NBA Stats API connection failed: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ NBA Stats API connection failed: {e}")
            return False

    def collect_all_data(self, use_sample_data: bool = False) -> Dict[str, pd.DataFrame]:
        """Collect all NBA data from multiple sources and return as a dictionary of DataFrames"""
        data = {}
        
        if use_sample_data:
            logger.info("Using sample data for testing")
            sample_df = self.create_sample_data()
            data['current_season'] = sample_df
            data['advanced_stats'] = sample_df  # Simplified for sample
            data['defensive_stats'] = sample_df  # Simplified for sample
            data['historical'] = sample_df  # Simplified for sample
        else:
            logger.info("Collecting real NBA data from multiple sources...")
            
            # Try multiple data sources in order of preference
            current_season_data = None
            
            # Source 1: Try NBA Stats API first
            logger.info("🔄 Attempting NBA Stats API...")
            if self.test_api_connection():
                logger.info("✅ NBA Stats API is accessible")
                try:
                    current_season_data = self.get_current_season_players()
                    if not current_season_data.empty:
                        logger.info(f"✅ Retrieved {len(current_season_data)} players from NBA Stats API")
                    else:
                        logger.warning("⚠️ NBA Stats API returned empty data")
                except Exception as e:
                    logger.warning(f"⚠️ NBA Stats API failed: {e}")
            else:
                logger.warning("⚠️ NBA Stats API is not accessible")
            
            # Source 2: Try Basketball Reference if NBA Stats failed
            if current_season_data is None or current_season_data.empty:
                logger.info("🔄 Attempting Basketball Reference...")
                try:
                    current_season_data = self.get_basketball_reference_stats("2023-24")
                    if not current_season_data.empty:
                        logger.info(f"✅ Retrieved {len(current_season_data)} players from Basketball Reference")
                    else:
                        logger.warning("⚠️ Basketball Reference returned empty data")
                except Exception as e:
                    logger.warning(f"⚠️ Basketball Reference failed: {e}")
            
            # Source 3: Try ESPN API if previous sources failed
            if current_season_data is None or current_season_data.empty:
                logger.info("🔄 Attempting ESPN API...")
                try:
                    current_season_data = self.get_espn_stats("2023-24")
                    if not current_season_data.empty:
                        logger.info(f"✅ Retrieved {len(current_season_data)} players from ESPN API")
                    else:
                        logger.warning("⚠️ ESPN API returned empty data")
                except Exception as e:
                    logger.warning(f"⚠️ ESPN API failed: {e}")
            
            # Source 4: Fallback to enhanced sample data if all real sources failed
            if current_season_data is None or current_season_data.empty:
                logger.warning("⚠️ All real data sources failed")
                logger.info("🔄 Falling back to enhanced sample data with realistic NBA statistics")
                
                current_season_data = self.create_enhanced_sample_data()
                logger.info("✅ Enhanced sample data created successfully")
            
            # Store the data
            data['current_season'] = current_season_data
            data['advanced_stats'] = current_season_data  # Use same data for now
            data['defensive_stats'] = current_season_data  # Use same data for now
            data['historical'] = current_season_data  # Use same data for now
            
            # Log summary
            logger.info(f"📊 Final data summary:")
            logger.info(f"   - Total players: {len(current_season_data)}")
            logger.info(f"   - Data source: {'Real NBA Data' if 'NBA Stats API' in str(current_season_data) or 'Basketball Reference' in str(current_season_data) or 'ESPN API' in str(current_season_data) else 'Enhanced Sample Data'}")
            
            # Show sample of top players
            if not current_season_data.empty:
                top_scorers = current_season_data.nlargest(3, 'PTS')
                scorer_list = []
                for _, player in top_scorers.iterrows():
                    scorer_list.append(f"{player['PLAYER_NAME']} ({player['PTS']:.1f} PPG)")
                logger.info(f"   - Top scorers: {', '.join(scorer_list)}")
        
        return data

    def create_enhanced_sample_data(self) -> pd.DataFrame:
        """Create enhanced sample data that more closely mimics real NBA statistics"""
        logger.info("Creating enhanced sample NBA data with realistic statistics...")
        
        # Real NBA player names and teams (2023-24 season)
        players = [
            'Nikola Jokic', 'Joel Embiid', 'Giannis Antetokounmpo', 'Luka Doncic', 'Shai Gilgeous-Alexander',
            'Kevin Durant', 'Stephen Curry', 'LeBron James', 'Damian Lillard', 'Anthony Davis',
            'Jayson Tatum', 'Devin Booker', 'Jimmy Butler', 'Kawhi Leonard', 'Paul George',
            'Russell Westbrook', 'Chris Paul', 'Kyrie Irving', 'Bradley Beal', 'Donovan Mitchell',
            'Zion Williamson', 'Ja Morant', 'Trae Young', 'De\'Aaron Fox', 'Tyrese Haliburton',
            'Bam Adebayo', 'Julius Randle', 'Pascal Siakam', 'Domantas Sabonis', 'Rudy Gobert',
            'Karl-Anthony Towns', 'Anthony Edwards', 'Cade Cunningham', 'Jalen Green', 'Scottie Barnes',
            'Franz Wagner', 'Evan Mobley', 'Josh Giddey', 'Jalen Suggs', 'Jonathan Kuminga',
            'Keegan Murray', 'Paolo Banchero', 'Jabari Smith Jr.', 'Chet Holmgren', 'Victor Wembanyama',
            'Scoot Henderson', 'Brandon Miller', 'Amen Thompson', 'Ausar Thompson', 'Cam Whitmore'
        ]
        
        teams = ['DEN', 'PHI', 'MIL', 'DAL', 'OKC', 'PHX', 'GSW', 'LAL', 'MIL', 'LAL',
                'BOS', 'PHX', 'MIA', 'LAC', 'LAC', 'LAC', 'GSW', 'DAL', 'PHX', 'CLE',
                'NOP', 'MEM', 'ATL', 'SAC', 'IND', 'MIA', 'NYK', 'TOR', 'SAC', 'MIN',
                'MIN', 'MIN', 'DET', 'HOU', 'TOR', 'ORL', 'CLE', 'OKC', 'ORL', 'GSW',
                'SAC', 'ORL', 'HOU', 'OKC', 'SAS', 'POR', 'CHA', 'HOU', 'DET', 'DET']
        
        # Create realistic NBA statistics
        data = []
        for i in range(50):
            # Generate realistic stats based on player type
            if i < 10:  # Top tier players (Jokic, Embiid, Giannis, etc.)
                pts = 25.0 + (i % 8)  # 25-32 PPG
                ast = 5.0 + (i % 6)   # 5-10 APG
                reb = 8.0 + (i % 5)   # 8-12 RPG
                fg_pct = 0.48 + (i % 8) * 0.01  # 0.48-0.55
                fg3_pct = 0.35 + (i % 10) * 0.01  # 0.35-0.44
            elif i < 25:  # Mid tier players
                pts = 18.0 + (i % 12)  # 18-29 PPG
                ast = 3.0 + (i % 8)    # 3-10 APG
                reb = 5.0 + (i % 8)    # 5-12 RPG
                fg_pct = 0.44 + (i % 12) * 0.01  # 0.44-0.55
                fg3_pct = 0.32 + (i % 15) * 0.01  # 0.32-0.46
            else:  # Role players
                pts = 12.0 + (i % 15)  # 12-26 PPG
                ast = 2.0 + (i % 6)    # 2-7 APG
                reb = 3.0 + (i % 8)    # 3-10 RPG
                fg_pct = 0.42 + (i % 15) * 0.01  # 0.42-0.56
                fg3_pct = 0.30 + (i % 20) * 0.01  # 0.30-0.49
            
            player_data = {
                'PLAYER_ID': i + 1,
                'PLAYER_NAME': players[i],
                'TEAM_ABBREVIATION': teams[i],
                'AGE': 22 + (i % 18),  # Ages 22-39
                'GP': 55 + (i % 25),   # Games 55-79
                'MIN': 28.0 + (i % 12), # Minutes 28-39
                'PTS': pts,
                'REB': reb,
                'AST': ast,
                'STL': 0.8 + (i % 3) * 0.2,   # Steals 0.8-1.4
                'BLK': 0.3 + (i % 4) * 0.2,   # Blocks 0.3-1.1
                'TOV': 1.5 + (i % 4) * 0.5,   # Turnovers 1.5-3.5
                'FG_PCT': fg_pct,
                'FG3_PCT': fg3_pct,
                'FT_PCT': 0.75 + (i % 20) * 0.01,  # FT% 0.75-0.94
                'DREB': reb * 0.7,  # Defensive rebounds (70% of total)
                'PF': 2.0 + (i % 4),    # Personal fouls 2-5
                'EFF': 15.0 + (i % 20)  # Efficiency 15-34
            }
            data.append(player_data)
        
        df = pd.DataFrame(data)
        logger.info(f"Created enhanced sample data with {len(df)} players")
        return df
    
    def get_basketball_reference_stats(self, season: str = "2023-24") -> pd.DataFrame:
        """Get NBA player stats from Basketball Reference via web scraping"""
        logger.info(f"Fetching {season} stats from Basketball Reference...")
        
        try:
            # Basketball Reference per-game stats URL
            url = f"{self.basketball_ref_base}/leagues/NBA_{season.split('-')[1]}_per_game.html"
            
            logger.info(f"Scraping from: {url}")
            
            # Add delay to respect rate limits
            time.sleep(self.request_delay)
            
            response = self.session.get(url, timeout=self.timeout)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find the stats table
                table = soup.find('table', {'id': 'per_game_stats'})
                
                if table:
                    # Extract headers
                    headers = []
                    header_row = table.find('thead').find('tr')
                    for th in header_row.find_all('th'):
                        headers.append(th.get_text().strip())
                    
                    # Extract data rows
                    rows = []
                    tbody = table.find('tbody')
                    for tr in tbody.find_all('tr', class_=lambda x: x != 'thead'):
                        row_data = []
                        for td in tr.find_all(['td', 'th']):
                            row_data.append(td.get_text().strip())
                        if len(row_data) > 1:  # Skip empty rows
                            rows.append(row_data)
                    
                    # Create DataFrame
                    df = pd.DataFrame(rows, columns=headers)
                    
                    # Clean and convert data types
                    df = self._clean_basketball_reference_data(df)
                    
                    logger.info(f"✅ Retrieved {len(df)} players from Basketball Reference")
                    return df
                else:
                    logger.error("Could not find stats table on Basketball Reference")
                    return pd.DataFrame()
            else:
                logger.error(f"Basketball Reference request failed: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error scraping Basketball Reference: {e}")
            return pd.DataFrame()
    
    def get_espn_stats(self, season: str = "2023-24") -> pd.DataFrame:
        """Get NBA player stats from ESPN API"""
        logger.info(f"Fetching {season} stats from ESPN API...")
        
        try:
            # ESPN API endpoint for NBA stats
            url = f"{self.espn_api_base}/athletes"
            
            # ESPN uses different season format
            espn_season = season.split('-')[1]  # "2024" for "2023-24"
            
            params = {
                'season': espn_season,
                'limit': 1000  # Get more players
            }
            
            logger.info(f"Requesting from ESPN API: {url}")
            
            # Add delay to respect rate limits
            time.sleep(self.request_delay)
            
            response = self.session.get(url, params=params, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'athletes' in data:
                    athletes = data['athletes']
                    
                    # Extract relevant stats
                    players_data = []
                    for athlete in athletes:
                        if 'statistics' in athlete and 'splits' in athlete['statistics']:
                            stats = athlete['statistics']['splits'].get('categories', [])
                            
                            # Find relevant stat categories
                            player_stats = {
                                'PLAYER_NAME': athlete.get('displayName', ''),
                                'TEAM_ABBREVIATION': athlete.get('team', {}).get('abbreviation', ''),
                                'AGE': athlete.get('age', 0),
                                'GP': 0,
                                'MIN': 0,
                                'PTS': 0,
                                'REB': 0,
                                'AST': 0,
                                'STL': 0,
                                'BLK': 0,
                                'TOV': 0,
                                'FG_PCT': 0,
                                'FG3_PCT': 0,
                                'FT_PCT': 0
                            }
                            
                            # Extract stats from categories
                            for category in stats:
                                if category.get('name') == 'games':
                                    player_stats['GP'] = category.get('stats', [{}])[0].get('value', 0)
                                elif category.get('name') == 'scoring':
                                    scoring_stats = category.get('stats', [])
                                    for stat in scoring_stats:
                                        if stat.get('name') == 'pointsPerGame':
                                            player_stats['PTS'] = stat.get('value', 0)
                                        elif stat.get('name') == 'fieldGoalPercentage':
                                            player_stats['FG_PCT'] = stat.get('value', 0)
                                        elif stat.get('name') == 'threePointPercentage':
                                            player_stats['FG3_PCT'] = stat.get('value', 0)
                                        elif stat.get('name') == 'freeThrowPercentage':
                                            player_stats['FT_PCT'] = stat.get('value', 0)
                                elif category.get('name') == 'rebounds':
                                    reb_stats = category.get('stats', [])
                                    for stat in reb_stats:
                                        if stat.get('name') == 'reboundsPerGame':
                                            player_stats['REB'] = stat.get('value', 0)
                                elif category.get('name') == 'assists':
                                    ast_stats = category.get('stats', [])
                                    for stat in ast_stats:
                                        if stat.get('name') == 'assistsPerGame':
                                            player_stats['AST'] = stat.get('value', 0)
                                elif category.get('name') == 'steals':
                                    stl_stats = category.get('stats', [])
                                    for stat in stl_stats:
                                        if stat.get('name') == 'stealsPerGame':
                                            player_stats['STL'] = stat.get('value', 0)
                                elif category.get('name') == 'blocks':
                                    blk_stats = category.get('stats', [])
                                    for stat in blk_stats:
                                        if stat.get('name') == 'blocksPerGame':
                                            player_stats['BLK'] = stat.get('value', 0)
                                elif category.get('name') == 'turnovers':
                                    tov_stats = category.get('stats', [])
                                    for stat in tov_stats:
                                        if stat.get('name') == 'turnoversPerGame':
                                            player_stats['TOV'] = stat.get('value', 0)
                            
                            # Only add players with meaningful stats
                            if player_stats['GP'] > 0 and player_stats['PTS'] > 0:
                                players_data.append(player_stats)
                    
                    df = pd.DataFrame(players_data)
                    
                    if not df.empty:
                        logger.info(f"✅ Retrieved {len(df)} players from ESPN API")
                        return df
                    else:
                        logger.warning("No player data found in ESPN API response")
                        return pd.DataFrame()
                else:
                    logger.error("No athletes data found in ESPN API response")
                    return pd.DataFrame()
            else:
                logger.error(f"ESPN API request failed: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error fetching from ESPN API: {e}")
            return pd.DataFrame()
    
    def _clean_basketball_reference_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize Basketball Reference data"""
        try:
            # Remove rows with no player name
            df = df[df['Player'].notna() & (df['Player'] != '')]
            
            # Rename columns to match our standard format
            column_mapping = {
                'Player': 'PLAYER_NAME',
                'Tm': 'TEAM_ABBREVIATION',
                'Age': 'AGE',
                'G': 'GP',
                'MP': 'MIN',
                'PTS': 'PTS',
                'TRB': 'REB',
                'AST': 'AST',
                'STL': 'STL',
                'BLK': 'BLK',
                'TOV': 'TOV',
                'FG%': 'FG_PCT',
                '3P%': 'FG3_PCT',
                'FT%': 'FT_PCT'
            }
            
            # Rename columns that exist
            existing_columns = {k: v for k, v in column_mapping.items() if k in df.columns}
            df = df.rename(columns=existing_columns)
            
            # Convert numeric columns
            numeric_columns = ['AGE', 'GP', 'MIN', 'PTS', 'REB', 'AST', 'STL', 'BLK', 'TOV', 'FG_PCT', 'FG3_PCT', 'FT_PCT']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
            
            # Fill missing values
            df = df.fillna(0)
            
            # Add missing columns with default values
            if 'DREB' not in df.columns:
                df['DREB'] = df['REB'] * 0.7  # Estimate defensive rebounds
            if 'PF' not in df.columns:
                df['PF'] = 2.5  # Default personal fouls
            if 'EFF' not in df.columns:
                # Calculate simple efficiency rating
                df['EFF'] = df['PTS'] + df['REB'] * 1.2 + df['AST'] * 1.5 + df['STL'] * 2 + df['BLK'] * 2 - df['TOV'] * 1
            
            return df
            
        except Exception as e:
            logger.error(f"Error cleaning Basketball Reference data: {e}")
            return df
    
    def save_to_csv(self, data: Dict[str, pd.DataFrame], output_dir: str = "data"):
        """Save all collected data to CSV files"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # Create a combined dataset (this is what the API actually uses)
        if data['current_season'].empty and not data['historical'].empty:
            combined_df = data['historical']
        elif not data['current_season'].empty:
            combined_df = data['current_season']
        else:
            combined_df = pd.DataFrame()
        
        if not combined_df.empty:
            # Only save the combined file that the API actually uses
            latest_combined_filename = f"{output_dir}/nba_combined_latest.csv"
            combined_df.to_csv(latest_combined_filename, index=False)
            logger.info(f"✅ Saved combined data to {latest_combined_filename} ({len(combined_df)} players)")
            
            # Optionally save individual files for debugging (commented out to reduce clutter)
            # for data_type, df in data.items():
            #     if not df.empty:
            #         latest_filename = f"{output_dir}/nba_{data_type}_latest.csv"
            #         df.to_csv(latest_filename, index=False)
            #         logger.info(f"Saved {data_type} data to {latest_filename}")
        else:
            logger.warning("No data to save - all DataFrames are empty")

if __name__ == "__main__":
    # Test the data collector
    collector = NBADataCollector()
    
    # Use sample data for testing (set to False to use real APIs)
    use_sample_data = True
    
    data = collector.collect_all_data(use_sample_data=use_sample_data)
    collector.save_to_csv(data)
    
    print("Data collection completed!")
