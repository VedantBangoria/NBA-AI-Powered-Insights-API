import pandas as pd
import numpy as np
from typing import List, Dict, Optional
import json
import logging
from datetime import datetime
import os
from ollama import Client
import re # Added for hot take parsing

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NBAAnalytics:
    """
    NBA Analytics class with three main methods:
    1. Generate hot takes based on data analysis
    2. Advanced statistical analysis with AI insights
    3. Player lookup with offensive/defensive scores
    """
    
    def __init__(self, data_path: str = "data/nba_combined_latest.csv", model_name: str = "llama2:7b"):
        """
        Initialize NBA Analytics with local LLM model
        
        Args:
            data_path: Path to the NBA data CSV file
            model_name: Name of the Ollama model to use (default: llama2:7b)
        """
        self.data_path = data_path
        self.model_name = model_name
        self.client = Client(host='http://localhost:11434')
        self.data = None
        self.load_data()
        
        # Check if model is available, if not provide instructions
        self._check_model_availability()
    
    def _check_model_availability(self):
        """Check if the specified model is available in Ollama"""
        try:
            models = self.client.list()
            available_models = [model['name'] for model in models['models']]
            
            if self.model_name not in available_models:
                logging.warning(f"Model {self.model_name} not found. Available models: {available_models}")
                logging.info(f"To install {self.model_name}, run: ollama pull {self.model_name}")
                logging.info("For your RTX 3050 Ti, I recommend: ollama pull llama2:7b")
                # Fallback to a smaller model if available
                fallback_models = ['llama2:7b', 'mistral:7b', 'phi:2.7b']
                for fallback in fallback_models:
                    if fallback in available_models:
                        self.model_name = fallback
                        logging.info(f"Using fallback model: {self.model_name}")
                        break
        except Exception as e:
            logging.error(f"Could not connect to Ollama: {e}")
            logging.info("Make sure Ollama is installed and running: https://ollama.ai")
    
    def _call_local_llm(self, prompt: str, max_tokens: int = 1000) -> str:
        """
        Call the local LLM model using Ollama
        
        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens to generate
            
        Returns:
            Generated response from the model
        """
        try:
            response = self.client.generate(
                model=self.model_name,
                prompt=prompt,
                options={
                    'num_predict': max_tokens,
                    'temperature': 0.7,
                    'top_p': 0.9
                }
            )
            return response['response']
        except Exception as e:
            logging.error(f"Error calling local LLM: {e}")
            return ""

    def load_data(self):
        """Load NBA data from CSV file"""
        try:
            if os.path.exists(self.data_path):
                self.data = pd.read_csv(self.data_path)
                logging.info(f"Loaded {len(self.data)} player records from {self.data_path}")
            else:
                logging.warning(f"Data file {self.data_path} not found. Please run data collection first.")
                self.data = pd.DataFrame()
        except Exception as e:
            logging.error(f"Error loading data: {e}")
            self.data = pd.DataFrame()

    def calculate_offensive_score(self, player_stats: pd.Series) -> float:
        """
        Calculate offensive score based on points, shooting efficiency, assists, and turnovers
        
        Formula: (Points * 0.3) + (FG% * 100 * 0.2) + (3P% * 100 * 0.15) + 
                 (FT% * 100 * 0.1) + (Assists * 0.15) - (Turnovers * 0.1)
        """
        try:
            points = player_stats.get('PTS', 0)
            fg_pct = player_stats.get('FG_PCT', 0) * 100
            three_pt_pct = player_stats.get('FG3_PCT', 0) * 100
            ft_pct = player_stats.get('FT_PCT', 0) * 100
            assists = player_stats.get('AST', 0)
            turnovers = player_stats.get('TOV', 0)
            
            offensive_score = (
                points * 0.3 +
                fg_pct * 0.2 +
                three_pt_pct * 0.15 +
                ft_pct * 0.1 +
                assists * 0.15 -
                turnovers * 0.1
            )
            
            return round(max(0, offensive_score), 2)
        except Exception as e:
            logging.error(f"Error calculating offensive score: {e}")
            return 0.0

    def calculate_defensive_score(self, player_stats: pd.Series) -> float:
        """
        Calculate defensive score based on steals, blocks, defensive rebounds, and fouls
        
        Formula: (Steals * 2) + (Blocks * 2) + (Defensive Rebounds * 0.5) - (Fouls * 0.5)
        """
        try:
            steals = player_stats.get('STL', 0)
            blocks = player_stats.get('BLK', 0)
            def_rebounds = player_stats.get('DREB', 0)
            fouls = player_stats.get('PF', 0)
            
            defensive_score = (
                steals * 2 +
                blocks * 2 +
                def_rebounds * 0.5 -
                fouls * 0.5
            )
            
            return round(max(0, defensive_score), 2)
        except Exception as e:
            logging.error(f"Error calculating defensive score: {e}")
            return 0.0

    def generate_hot_takes(self, num_takes: int = 5) -> Dict:
        """Generate NBA hot takes that are controversial but data-supported"""
        try:
            if self.data.empty:
                return {
                    "error": "No data available",
                    "hot_takes": [],
                    "model_used": self.model_name
                }
            
            # Create a summary of available data for the LLM
            data_summary = self._create_data_summary()
            
            prompt = f"""
You are an NBA analyst known for controversial but data-supported hot takes. 
Based on the following NBA player statistics, generate {num_takes} hot takes that:
1. Are controversial and few people would agree with
2. Are supported ONLY by the data provided below
3. Include specific statistics from the data to back up the claim
4. Are written in a bold, confident tone
5. DO NOT reference statistics that are not in the data (like TS%, efficiency ratings, etc.)

Available NBA Player Statistics:
{data_summary}

IMPORTANT RULES:
- Only use statistics that are actually listed above
- Do not make up rankings or percentages
- Do not reference "league leaders" unless they're clearly the highest in the data
- Focus on the actual numbers provided
- Be specific with the statistics you reference

Generate {num_takes} hot takes in this EXACT format:
1. HOT TAKE: [Short, vague, controversial statement - max 15 words]
   RATIONALE: [Detailed explanation with specific stats from the data]

2. HOT TAKE: [Short, vague, controversial statement - max 15 words]
   RATIONALE: [Detailed explanation with specific stats from the data]

3. HOT TAKE: [Short, vague, controversial statement - max 15 words]
   RATIONALE: [Detailed explanation with specific stats from the data]

4. HOT TAKE: [Short, vague, controversial statement - max 15 words]
   RATIONALE: [Detailed explanation with specific stats from the data]

5. HOT TAKE: [Short, vague, controversial statement - max 15 words]
   RATIONALE: [Detailed explanation with specific stats from the data]

The HOT TAKE should be brief and shocking. The RATIONALE should provide the detailed statistical backing.
Focus on surprising insights that go against popular opinion but are backed by the actual numbers provided.
"""
            
            # Try to get response from local LLM
            response = self._call_local_llm(prompt)
            
            if response:
                # Parse the response to extract hot takes and rationales
                hot_takes = self._parse_hot_takes_response(response, num_takes)
                
                return {
                    "hot_takes": hot_takes,
                    "model_used": self.model_name,
                    "data_source": "NBA Stats API",
                    "total_players_analyzed": len(self.data)
                }
            else:
                # Fallback to rule-based hot takes
                logger.warning("LLM failed, using rule-based hot takes")
                rule_based_takes = self._generate_rule_based_hot_takes(num_takes)
                return {
                    "hot_takes": rule_based_takes,
                    "model_used": "rule-based (LLM unavailable)",
                    "data_source": "NBA Stats API",
                    "total_players_analyzed": len(self.data)
                }
                
        except Exception as e:
            logger.error(f"Error generating hot takes: {e}")
            return {
                "error": f"Failed to generate hot takes: {str(e)}",
                "hot_takes": [],
                "model_used": self.model_name
            }

    def advanced_stats_analysis(self, player_name: str = None, team: str = None) -> Dict:
        """
        Provide AI-powered advanced statistical analysis
        """
        if self.data.empty:
            return {"error": "No data available for analysis"}
        
        try:
            if player_name:
                return self._analyze_player(player_name)
            elif team:
                return self._analyze_team(team)
            else:
                return self._analyze_league()
                
        except Exception as e:
            logging.error(f"Error in advanced stats analysis: {e}")
            return {"error": f"Analysis failed: {str(e)}"}

    def player_lookup(self, player_name: str) -> Dict:
        """
        Get player's stats and calculated offensive/defensive scores
        """
        if self.data.empty:
            return {"error": "No data available"}
        
        try:
            # Case-insensitive search
            player_data = self.data[
                self.data['PLAYER_NAME'].str.contains(player_name, case=False, na=False)
            ]
            
            if player_data.empty:
                return {"error": f"Player '{player_name}' not found"}
            
            # Get the first match
            player_stats = player_data.iloc[0]
            
            offensive_score = self.calculate_offensive_score(player_stats)
            defensive_score = self.calculate_defensive_score(player_stats)
            
            # Convert numpy types to Python native types for JSON serialization
            return {
                "player_name": str(player_stats['PLAYER_NAME']),
                "team": str(player_stats.get('TEAM_ABBREVIATION', 'Unknown')),
                "position": str(player_stats.get('PLAYERCODE', 'Unknown')),
                "games_played": int(player_stats.get('GP', 0)),
                "minutes_per_game": float(player_stats.get('MIN', 0)),
                "points_per_game": float(player_stats.get('PTS', 0)),
                "rebounds_per_game": float(player_stats.get('REB', 0)),
                "assists_per_game": float(player_stats.get('AST', 0)),
                "steals_per_game": float(player_stats.get('STL', 0)),
                "blocks_per_game": float(player_stats.get('BLK', 0)),
                "field_goal_percentage": float(player_stats.get('FG_PCT', 0)),
                "three_point_percentage": float(player_stats.get('FG3_PCT', 0)),
                "free_throw_percentage": float(player_stats.get('FT_PCT', 0)),
                "offensive_score": float(offensive_score),
                "defensive_score": float(defensive_score),
                "offensive_rating": str(self._get_rating_description(offensive_score, "offensive")),
                "defensive_rating": str(self._get_rating_description(defensive_score, "defensive")),
                "analysis": str(self._generate_player_analysis(player_stats, offensive_score, defensive_score))
            }
            
        except Exception as e:
            logging.error(f"Error in player lookup: {e}")
            return {"error": f"Lookup failed: {str(e)}"}

    def _prepare_data_summary(self) -> str:
        """Prepare a summary of the data for LLM analysis"""
        if self.data.empty:
            return "No data available"
        
        summary = []
        summary.append(f"Total players: {len(self.data)}")
        
        # Top scorers
        top_scorers = self.data.nlargest(5, 'PTS')[['PLAYER_NAME', 'PTS', 'TEAM_ABBREVIATION']]
        summary.append("Top 5 scorers:")
        for _, player in top_scorers.iterrows():
            summary.append(f"- {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}): {player['PTS']:.1f} PPG")
        
        # Top assist leaders
        top_assists = self.data.nlargest(5, 'AST')[['PLAYER_NAME', 'AST', 'TEAM_ABBREVIATION']]
        summary.append("Top 5 assist leaders:")
        for _, player in top_assists.iterrows():
            summary.append(f"- {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}): {player['AST']:.1f} APG")
        
        # Shooting percentages
        summary.append(f"League average FG%: {self.data['FG_PCT'].mean():.3f}")
        summary.append(f"League average 3P%: {self.data['FG3_PCT'].mean():.3f}")
        
        return "\n".join(summary)

    def _create_data_summary(self) -> str:
        """Create a summary of available data for the LLM"""
        if self.data.empty:
            return "No data available"
        
        summary = []
        summary.append(f"Total players: {len(self.data)}")
        
        # Top scorers
        top_scorers = self.data.nlargest(5, 'PTS')[['PLAYER_NAME', 'PTS', 'TEAM_ABBREVIATION']]
        summary.append("Top 5 scorers:")
        for _, player in top_scorers.iterrows():
            summary.append(f"- {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}): {player['PTS']:.1f} PPG")
        
        # Top assist leaders
        top_assists = self.data.nlargest(5, 'AST')[['PLAYER_NAME', 'AST', 'TEAM_ABBREVIATION']]
        summary.append("Top 5 assist leaders:")
        for _, player in top_assists.iterrows():
            summary.append(f"- {player['PLAYER_NAME']} ({player['TEAM_ABBREVIATION']}): {player['AST']:.1f} APG")
        
        # Shooting percentages
        summary.append(f"League average FG%: {self.data['FG_PCT'].mean():.3f}")
        summary.append(f"League average 3P%: {self.data['FG3_PCT'].mean():.3f}")
        
        return "\n".join(summary)

    def _analyze_player(self, player_name: str) -> Dict:
        """Analyze a specific player"""
        player_data = self.data[
            self.data['PLAYER_NAME'].str.contains(player_name, case=False, na=False)
        ]
        
        if player_data.empty:
            return {"error": f"Player '{player_name}' not found"}
        
        player_stats = player_data.iloc[0]
        
        prompt = f"""
Analyze this NBA player's performance and provide insights:

Player: {player_stats['PLAYER_NAME']}
Team: {player_stats.get('TEAM_ABBREVIATION', 'Unknown')}
Games: {player_stats.get('GP', 0)}
Minutes: {player_stats.get('MIN', 0):.1f} per game
Points: {player_stats.get('PTS', 0):.1f} per game
Rebounds: {player_stats.get('REB', 0):.1f} per game
Assists: {player_stats.get('AST', 0):.1f} per game
Steals: {player_stats.get('STL', 0):.1f} per game
Blocks: {player_stats.get('BLK', 0):.1f} per game
FG%: {player_stats.get('FG_PCT', 0):.3f}
3P%: {player_stats.get('FG3_PCT', 0):.3f}
FT%: {player_stats.get('FT_PCT', 0):.3f}

Provide a detailed analysis covering:
1. Strengths and weaknesses
2. Efficiency analysis
3. Role and impact on team
4. Areas for improvement
5. Comparison to league averages

Write in a professional but engaging tone.
"""

        response = self._call_local_llm(prompt, max_tokens=600)
        
        return {
            "player_name": player_stats['PLAYER_NAME'],
            "team": player_stats.get('TEAM_ABBREVIATION', 'Unknown'),
            "stats": player_stats.to_dict(),
            "analysis": response if response else "Analysis unavailable"
        }

    def _analyze_team(self, team: str) -> Dict:
        """Analyze a specific team"""
        team_data = self.data[
            self.data['TEAM_ABBREVIATION'].str.contains(team, case=False, na=False)
        ]
        
        if team_data.empty:
            return {"error": f"Team '{team}' not found"}
        
        # Calculate team averages
        team_avg = team_data.mean(numeric_only=True)
        
        prompt = f"""
Analyze this NBA team's performance:

Team: {team}
Players: {len(team_data)}
Average Points: {team_avg.get('PTS', 0):.1f} per game
Average Rebounds: {team_avg.get('REB', 0):.1f} per game
Average Assists: {team_avg.get('AST', 0):.1f} per game
Average FG%: {team_avg.get('FG_PCT', 0):.3f}
Average 3P%: {team_avg.get('FG3_PCT', 0):.3f}

Provide analysis covering:
1. Team strengths and weaknesses
2. Playing style assessment
3. Key players' contributions
4. Areas for improvement
5. Overall team efficiency

Write in a professional tone.
"""

        response = self._call_local_llm(prompt, max_tokens=500)
        
        return {
            "team": team,
            "player_count": len(team_data),
            "team_averages": team_avg.to_dict(),
            "analysis": response if response else "Analysis unavailable"
        }

    def _analyze_league(self) -> Dict:
        """Analyze league-wide trends"""
        if self.data.empty:
            return {"error": "No data available"}
        
        league_avg = self.data.mean(numeric_only=True)
        
        prompt = f"""
Analyze current NBA league trends based on these averages:

League Averages:
- Points per game: {league_avg.get('PTS', 0):.1f}
- Rebounds per game: {league_avg.get('REB', 0):.1f}
- Assists per game: {league_avg.get('AST', 0):.1f}
- Field Goal %: {league_avg.get('FG_PCT', 0):.3f}
- Three Point %: {league_avg.get('FG3_PCT', 0):.3f}
- Free Throw %: {league_avg.get('FT_PCT', 0):.3f}

Provide analysis covering:
1. Current league trends
2. Offensive vs defensive balance
3. Three-point shooting impact
4. Pace of play observations
5. Notable statistical patterns

Write in a professional tone.
"""

        response = self._call_local_llm(prompt, max_tokens=500)
        
        return {
            "analysis_type": "league_wide",
            "league_averages": league_avg.to_dict(),
            "analysis": response if response else "Analysis unavailable"
        }

    def _generate_player_analysis(self, player_stats: pd.Series, offensive_score: float, defensive_score: float) -> str:
        """Generate a brief analysis of the player"""
        try:
            prompt = f"""
Provide a brief 2-3 sentence analysis of this NBA player:

Name: {player_stats['PLAYER_NAME']}
Offensive Score: {offensive_score}
Defensive Score: {defensive_score}
Points: {player_stats.get('PTS', 0):.1f} PPG
Assists: {player_stats.get('AST', 0):.1f} APG
Rebounds: {player_stats.get('REB', 0):.1f} RPG

Focus on their playing style and impact.
"""

            response = self._call_local_llm(prompt, max_tokens=200)
            return response if response else "Analysis unavailable"
        except Exception as e:
            logging.error(f"Error generating player analysis: {e}")
            return "Analysis unavailable"

    def _parse_hot_takes_response(self, response: str, num_takes: int) -> List[Dict]:
        """Parse LLM response to extract hot takes and rationales"""
        hot_takes = []
        
        try:
            # Split by numbered items
            lines = response.strip().split('\n')
            current_take = {}
            
            for line in lines:
                line = line.strip()
                
                # Check for numbered items
                if re.match(r'^\d+\.', line):
                    # Save previous take if exists
                    if current_take and 'hot_take' in current_take and 'rationale' in current_take:
                        hot_takes.append(current_take)
                    
                    # Start new take
                    current_take = {}
                    continue
                
                # Check for HOT TAKE
                if line.startswith('HOT TAKE:'):
                    hot_take = line.replace('HOT TAKE:', '').strip()
                    current_take['hot_take'] = hot_take
                    continue
                
                # Check for RATIONALE
                if line.startswith('RATIONALE:'):
                    rationale = line.replace('RATIONALE:', '').strip()
                    current_take['rationale'] = rationale
                    continue
                
                # If we're in a rationale section, append to current rationale
                if 'rationale' in current_take and line:
                    current_take['rationale'] += ' ' + line
            
            # Add the last take
            if current_take and 'hot_take' in current_take and 'rationale' in current_take:
                hot_takes.append(current_take)
            
            # If parsing failed, create fallback takes
            if len(hot_takes) < num_takes:
                logger.warning(f"Only parsed {len(hot_takes)} hot takes, creating fallbacks")
                fallback_takes = self._generate_rule_based_hot_takes(num_takes - len(hot_takes))
                hot_takes.extend(fallback_takes)
            
            return hot_takes[:num_takes]
            
        except Exception as e:
            logger.error(f"Error parsing hot takes response: {e}")
            # Return rule-based takes as fallback
            return self._generate_rule_based_hot_takes(num_takes)

    def _generate_rule_based_hot_takes(self, num_takes: int) -> List[Dict]:
        """Generate rule-based hot takes when LLM is unavailable"""
        hot_takes = []
        
        try:
            # Get top performers in various categories
            top_scorers = self.data.nlargest(10, 'PTS')
            top_assisters = self.data.nlargest(10, 'AST')
            top_rebounders = self.data.nlargest(10, 'REB')
            top_efficiency = self.data.nlargest(10, 'EFF')
            
            # Hot take templates
            templates = [
                {
                    "hot_take": f"{top_scorers.iloc[0]['PLAYER_NAME']} is overrated as a scorer",
                    "rationale": f"Despite averaging {top_scorers.iloc[0]['PTS']:.1f} PPG, {top_scorers.iloc[0]['PLAYER_NAME']} has a mediocre {top_scorers.iloc[0]['FG_PCT']:.3f} field goal percentage, showing they're inefficient despite high volume."
                },
                {
                    "hot_take": f"{top_assisters.iloc[0]['PLAYER_NAME']} is the best playmaker in the league",
                    "rationale": f"{top_assisters.iloc[0]['PLAYER_NAME']} leads with {top_assisters.iloc[0]['AST']:.1f} assists per game while maintaining a solid {top_assisters.iloc[0]['FG_PCT']:.3f} shooting percentage, proving elite playmaking ability."
                },
                {
                    "hot_take": f"{top_rebounders.iloc[0]['PLAYER_NAME']} is underappreciated",
                    "rationale": f"{top_rebounders.iloc[0]['PLAYER_NAME']} averages {top_rebounders.iloc[0]['REB']:.1f} rebounds per game with {top_rebounders.iloc[0]['PTS']:.1f} PPG, showing they're a complete player who doesn't get enough recognition."
                },
                {
                    "hot_take": f"{top_efficiency.iloc[0]['PLAYER_NAME']} is the most efficient player",
                    "rationale": f"With an efficiency rating of {top_efficiency.iloc[0]['EFF']:.1f}, {top_efficiency.iloc[0]['PLAYER_NAME']} proves that raw stats don't tell the full story - they're getting the most out of every possession."
                },
                {
                    "hot_take": f"High-volume scorers are hurting their teams",
                    "rationale": f"Players averaging over 25 PPG often have FG% below 0.450, showing that high volume scoring doesn't necessarily translate to team success or efficiency."
                }
            ]
            
            # Return requested number of takes
            for i in range(min(num_takes, len(templates))):
                hot_takes.append(templates[i])
            
            return hot_takes
            
        except Exception as e:
            logger.error(f"Error generating rule-based hot takes: {e}")
            return [
                {
                    "hot_take": "Sample hot take - data unavailable",
                    "rationale": "This is a placeholder hot take generated when data analysis is unavailable."
                }
            ]

    def _get_rating_description(self, score: float, score_type: str) -> str:
        """Get a description for the offensive/defensive score"""
        if score_type == "offensive":
            if score >= 25: return "Elite"
            elif score >= 20: return "Excellent"
            elif score >= 15: return "Good"
            elif score >= 10: return "Average"
            else: return "Below Average"
        else:  # defensive
            if score >= 8: return "Elite"
            elif score >= 6: return "Excellent"
            elif score >= 4: return "Good"
            elif score >= 2: return "Average"
            else: return "Below Average"
