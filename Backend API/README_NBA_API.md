# NBA Analytics API

A comprehensive FastAPI-based NBA analytics platform that provides advanced statistical analysis, AI-powered insights, and player performance evaluation using LLM integration.

## Features

### 🏀 **Three Core Analytics Methods**

1. **Hot Takes Generation** - Generate controversial but data-supported NBA insights
2. **Advanced Statistical Analysis** - AI-powered analysis of player and team statistics  
3. **Player Lookup with Advanced Scores** - Comprehensive player profiles with calculated offensive/defensive scores

### 🚀 **Key Capabilities**

- **LLM Integration** - OpenAI GPT-4 powered insights and analysis
- **Data Collection** - Automated NBA data collection from multiple APIs
- **Advanced Metrics** - Custom offensive/defensive scoring formulas
- **Real-time Analysis** - Dynamic statistical analysis and insights
- **Comprehensive API** - RESTful endpoints with full documentation

## Tech Stack

- **Backend**: FastAPI (Python)
- **Data Processing**: Pandas, NumPy, Scikit-learn
- **LLM**: OpenAI GPT-4
- **Data Collection**: Requests, BeautifulSoup
- **Documentation**: Swagger/OpenAPI
- **Validation**: Pydantic

## Installation

### Prerequisites

- Python 3.8+
- OpenAI API key (for LLM features)

### Setup

1. **Clone and install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your OpenAI API key
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### 1. Hot Takes Generation
```
GET /hot-takes?num_takes=5
```
Generates controversial but data-supported NBA insights using LLM analysis.

**Response:**
```json
[
  {
    "statement": "Player X is overrated due to poor efficiency",
    "evidence": "FG%: 0.420 (bottom 30%), PPG: 25.1",
    "controversy_reason": "High scoring averages mask poor shooting",
    "data_reasoning": "Low field goal percentage despite high volume"
  }
]
```

### 2. Advanced Statistical Analysis
```
GET /advanced-analysis?player_name=LeBron James
GET /advanced-analysis?team=LAL
GET /advanced-analysis
```
Provides comprehensive statistical analysis with AI insights.

**Response:**
```json
{
  "analysis_scope": "player LeBron James",
  "data_summary": "Comprehensive statistical breakdown...",
  "advanced_metrics": {
    "avg_per": 25.8,
    "avg_usage_rate": 28.5,
    "avg_ast_to_ratio": 2.1
  },
  "ai_insights": "Detailed AI-generated analysis...",
  "timestamp": "2024-01-15T10:30:00"
}
```

### 3. Player Lookup with Advanced Scores
```
GET /player-lookup/LeBron James
```
Returns comprehensive player profile with calculated offensive/defensive scores.

**Response:**
```json
{
  "player_name": "LeBron James",
  "team": "LAL",
  "age": "39",
  "games_played": 67,
  "minutes_per_game": 35.3,
  "basic_stats": {
    "points_per_game": 25.7,
    "rebounds_per_game": 7.3,
    "assists_per_game": 8.1
  },
  "calculated_scores": {
    "offensive_score": 78.5,
    "defensive_score": 18.2,
    "overall_score": 54.8
  },
  "analysis": {
    "offensive_rating": "Elite Offensive Player",
    "defensive_rating": "Good Defensive Player",
    "overall_rating": "Very Good Player"
  }
}
```

### Additional Endpoints

- `GET /` - API information
- `GET /health` - Health check
- `GET /players` - List available players
- `POST /collect-data` - Trigger data collection

## Data Collection

The API includes a comprehensive data collection system:

### NBA Data Sources
- **NBA Stats API** - Official NBA statistics
- **Basketball Reference** - Historical data and advanced metrics
- **Multiple Seasons** - Current and historical data collection

### Data Types Collected
- **Basic Stats** - Points, rebounds, assists, etc.
- **Advanced Stats** - PER, usage rate, efficiency metrics
- **Defensive Stats** - Steals, blocks, defensive ratings
- **Historical Data** - Multi-season analysis

## Scoring Formulas

### Offensive Score Formula
```
Offensive Score = (Points × 2.0 + Efficiency Bonus + Assists × 1.5 + Turnover Penalty) × Minutes Factor

Where:
- Efficiency Bonus = (FG% × 0.5 + 3P% × 0.3 + FT% × 0.2) × 20
- Minutes Factor = min(Minutes/35.0, 1.2)
```

### Defensive Score Formula
```
Defensive Score = (Steals × 3.0 + Blocks × 2.5 + Defensive Rebounds × 1.0 + Foul Penalty) × Minutes Factor

Where:
- Defensive Rebounds = Total Rebounds × 0.4 (if not available)
- Minutes Factor = min(Minutes/35.0, 1.2)
```

## Usage Examples

### Python Client Example
```python
import requests

# Get hot takes
response = requests.get("http://localhost:8000/hot-takes?num_takes=3")
hot_takes = response.json()

# Get player analysis
response = requests.get("http://localhost:8000/player-lookup/LeBron James")
player_data = response.json()

# Get advanced analysis
response = requests.get("http://localhost:8000/advanced-analysis?team=LAL")
analysis = response.json()
```

### cURL Examples
```bash
# Get hot takes
curl "http://localhost:8000/hot-takes?num_takes=5"

# Look up player
curl "http://localhost:8000/player-lookup/Stephen Curry"

# Get team analysis
curl "http://localhost:8000/advanced-analysis?team=GSW"
```

## Configuration

### Environment Variables
- `OPENAI_API_KEY` - Required for LLM features
- `PORT` - Server port (default: 8000)
- `DATA_PATH` - Path to NBA data CSV file
- `USE_SAMPLE_DATA` - Use sample data for testing

### Data Configuration
The API automatically collects and manages NBA data:
- Sample data is used by default for testing
- Real API data collection can be triggered via `/collect-data` endpoint
- Data is cached in CSV format for performance

## Development

### Project Structure
```
├── main.py                 # FastAPI server
├── nba_analytics.py        # Core analytics class
├── nba_data_collector.py   # Data collection module
├── requirements.txt        # Python dependencies
├── env.example            # Environment variables template
├── data/                  # NBA data storage
└── README_NBA_API.md      # This file
```

### Running Tests
```bash
# Test data collection
python nba_data_collector.py

# Test analytics
python -c "from nba_analytics import NBAAnalytics; analytics = NBAAnalytics(); print(analytics.generate_hot_takes(1))"
```

### Adding New Features
1. Extend the `NBAAnalytics` class with new methods
2. Add corresponding FastAPI endpoints in `main.py`
3. Update Pydantic models for request/response validation
4. Add tests and documentation

## API Documentation

Once the server is running, visit:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## Performance Considerations

- **Data Caching**: NBA data is cached in CSV format
- **LLM Optimization**: Efficient prompt engineering for faster responses
- **Rate Limiting**: Built-in rate limiting for API calls
- **Error Handling**: Comprehensive error handling and fallbacks

## Production Deployment

### Docker (Recommended)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Setup
1. Set production environment variables
2. Configure CORS origins appropriately
3. Set up monitoring and logging
4. Configure data collection schedules

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the API documentation at `/docs`
2. Review the health endpoint at `/health`
3. Check the logs for detailed error information

---

**Built with ❤️ for NBA analytics enthusiasts**
