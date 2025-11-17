from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
import logging
import os
from dotenv import load_dotenv

from nba_data_collector import NBADataCollector
from nba_analytics import NBAAnalytics

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="NBA Analytics API",
    description="Advanced NBA player analytics with local LLM integration",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global analytics instance
analytics = None

@app.on_event("startup")
async def startup_event():
    """Initialize the analytics system on startup"""
    global analytics
    
    # Initialize analytics with local LLM model
    model_name = os.getenv("LLM_MODEL_NAME", "llama2:7b")
    data_path = os.getenv("DATA_PATH", "data/nba_combined_latest.csv")
    
    analytics = NBAAnalytics(data_path=data_path, model_name=model_name)
    
    # Check if data exists, if not collect real data
    if not os.path.exists(data_path):
        logger.info("No data found. Attempting to collect real NBA data...")
        collector = NBADataCollector()
        
        # Test API connection first
        logger.info("Testing NBA Stats API connectivity...")
        api_available = collector.test_api_connection()
        
        if api_available:
            logger.info("✅ NBA Stats API is accessible. Collecting real data...")
            try:
                collector.collect_all_data(use_sample_data=False)
                logger.info("✅ Real NBA data collected successfully")
            except Exception as e:
                logger.warning(f"⚠️ Failed to collect real data: {e}")
                logger.info("🔄 Falling back to sample data...")
                collector.collect_all_data(use_sample_data=True)
                logger.info("✅ Sample data collected successfully")
        else:
            logger.warning("⚠️ NBA Stats API is not accessible")
            logger.info("🔄 Using sample data instead...")
            try:
                collector.collect_all_data(use_sample_data=True)
                logger.info("✅ Sample data collected successfully")
            except Exception as e:
                logger.error(f"❌ Failed to collect sample data: {e}")
                raise Exception("Failed to initialize data collection")
    else:
        logger.info("✅ Using existing data from previous collection")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "NBA Analytics API",
        "version": "1.0.0",
        "description": "Advanced NBA player analytics with local LLM integration",
        "endpoints": {
            "hot_takes": "/hot-takes",
            "advanced_analysis": "/advanced-analysis",
            "player_lookup": "/player-lookup/{player_name}",
            "collect_data": "/collect-data",
            "health": "/health",
            "players": "/players"
        },
        "model": analytics.model_name if analytics else "Not initialized"
    }

@app.get("/hot-takes")
async def get_hot_takes(num_takes: int = 5):
    """Get NBA hot takes that are controversial but data-supported"""
    try:
        if num_takes < 1 or num_takes > 3:
            raise HTTPException(status_code=400, detail="num_takes must be between 1 and 20")
        
        result = analytics.generate_hot_takes(num_takes)
        
        # Return the result directly since it's already in the correct format
        return result
        
    except Exception as e:
        logger.error(f"Error generating hot takes: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate hot takes: {str(e)}")

@app.get("/advanced-analysis")
async def get_advanced_analysis(
    player_name: Optional[str] = Query(None, description="Player name for individual analysis"),
    team: Optional[str] = Query(None, description="Team abbreviation for team analysis")
):
    """Get advanced statistical analysis with AI insights"""
    if not analytics:
        raise HTTPException(status_code=500, detail="Analytics system not initialized")
    
    try:
        analysis = analytics.advanced_stats_analysis(player_name=player_name, team=team)
        return {
            "analysis": analysis,
            "model_used": analytics.model_name
        }
    except Exception as e:
        logger.error(f"Error in advanced analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/player-lookup/{player_name}")
async def get_player_lookup(player_name: str):
    """Get player's stats and calculated offensive/defensive scores"""
    if not analytics:
        raise HTTPException(status_code=500, detail="Analytics system not initialized")
    
    try:
        player_data = analytics.player_lookup(player_name)
        return {
            "player_data": player_data,
            "model_used": analytics.model_name
        }
    except Exception as e:
        logger.error(f"Error in player lookup: {e}")
        raise HTTPException(status_code=500, detail=f"Player lookup failed: {str(e)}")

@app.post("/collect-data")
async def collect_data(use_sample_data: bool = True):
    """Trigger data collection (real or sample data)"""
    try:
        collector = NBADataCollector()
        collector.collect_all_data(use_sample_data=use_sample_data)
        
        # Reload analytics with new data
        global analytics
        if analytics:
            analytics.load_data()
        
        return {
            "message": "Data collection completed successfully",
            "data_type": "sample" if use_sample_data else "real",
            "data_path": collector.data_path
        }
    except Exception as e:
        logger.error(f"Error collecting data: {e}")
        raise HTTPException(status_code=500, detail=f"Data collection failed: {str(e)}")

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "analytics_initialized": analytics is not None,
        "model_available": analytics.model_name if analytics else None,
        "data_loaded": len(analytics.data) if analytics and analytics.data is not None else 0
    }

@app.get("/players")
async def get_players():
    """Get list of available players"""
    if not analytics or analytics.data is None or analytics.data.empty:
        raise HTTPException(status_code=404, detail="No player data available")
    
    try:
        players = analytics.data['PLAYER_NAME'].tolist()
        return {
            "players": players,
            "count": len(players)
        }
    except Exception as e:
        logger.error(f"Error getting players list: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get players list: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(app, host=host, port=port)
