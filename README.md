# 🏀 NBA AI-Powered Insights API

> A full-stack NBA analytics platform featuring AI-generated insights, advanced statistical analysis, and real-time player performance evaluation using local LLM integration.

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [API Documentation](#-api-documentation)
- [Frontend](#-frontend)
- [Project Structure](#-project-structure)
- [Key Highlights](#-key-highlights)

## 🎯 Overview

This project is a comprehensive NBA analytics platform that combines **real-time data collection**, **advanced statistical analysis**, and **AI-powered insights** using local Large Language Models (LLMs). The system provides three core analytical capabilities:

1. **Hot Takes Generation** - AI-generated controversial but data-supported NBA insights
2. **Advanced Statistical Analysis** - Comprehensive player, team, and league analysis with AI commentary
3. **Player Performance Evaluation** - Detailed player profiles with custom offensive/defensive scoring algorithms

The backend is a production-ready FastAPI application with comprehensive error handling, while the frontend provides an intuitive web interface for interacting with all features.

## ✨ Features

### 🤖 AI-Powered Analytics
- **Local LLM Integration** - Uses Ollama with models like Llama 2, Mistral, or Phi-2 for privacy and cost-effectiveness
- **Intelligent Hot Takes** - Generates controversial but statistically-backed NBA insights
- **Contextual Analysis** - AI provides detailed commentary on player performance, team dynamics, and league trends
- **Fallback System** - Rule-based analysis when LLM is unavailable

### 📊 Advanced Statistics
- **Custom Scoring Algorithms** - Proprietary offensive and defensive rating systems
- **Multi-Source Data Collection** - Aggregates data from NBA Stats API, Basketball Reference, and ESPN
- **Historical Analysis** - Supports multi-season data analysis
- **Real-time Updates** - On-demand data collection and refresh capabilities

### 🎨 Modern Web Interface
- **Responsive Design** - Clean, modern UI with NBA-themed styling
- **Interactive Dashboard** - Easy navigation between different analytical features
- **Real-time Data Display** - Dynamic content rendering from API responses

### 🔧 Developer-Friendly
- **RESTful API** - Well-documented endpoints with OpenAPI/Swagger integration
- **Comprehensive Error Handling** - Graceful fallbacks and detailed error messages
- **Modular Architecture** - Clean separation of concerns for easy maintenance and extension
- **Environment Configuration** - Flexible setup via environment variables

## 🛠 Tech Stack

### Backend
- **Framework**: FastAPI (Python)
- **Data Processing**: Pandas, NumPy
- **LLM Integration**: Ollama (local LLM inference)
- **Data Collection**: Requests, BeautifulSoup4
- **API Documentation**: Swagger/OpenAPI
- **Validation**: Pydantic

### Frontend
- **HTML5/CSS3** - Modern, responsive design
- **JavaScript** - Dynamic content and API integration
- **NBA-Themed UI** - Custom styling with gradients and animations

### Infrastructure
- **Data Sources**: NBA Stats API, Basketball Reference, ESPN API
- **Storage**: CSV-based data caching
- **Deployment**: Ready for containerization (Docker)

## 🏗 Architecture

```
┌─────────────────┐
│   Frontend UI   │  ← User Interface (HTML/CSS/JS)
└────────┬────────┘
         │ HTTP/REST
┌────────▼────────┐
│  FastAPI Backend│  ← API Server (Python)
│  ┌───────────┐ │
│  │ Analytics │ │  ← Core Analytics Engine
│  └─────┬─────┘ │
│  ┌─────▼─────┐ │
│  │Data       │ │  ← Data Collection & Processing
│  │Collector  │ │
│  └─────┬─────┘ │
└────────┼───────┘
         │
    ┌────▼────┐
    │  Ollama │  ← Local LLM (Llama 2, Mistral, etc.)
    └────┬────┘
         │
    ┌────▼──────────────┐
    │  NBA Data Sources │
    │  - NBA Stats API  │
    │  - Basketball Ref │
    │  - ESPN API       │
    └───────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Ollama installed ([Download](https://ollama.ai))
- 8GB+ RAM (for LLM models)
- GPU recommended (RTX 3050 Ti or better)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/NBA-AI-Powered-Insights-API.git
   cd NBA-AI-Powered-Insights-API/Backend\ API
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up Ollama and download a model**
   ```bash
   # Install Ollama from https://ollama.ai
   # Then download a recommended model:
   ollama pull llama2:7b
   # Or for better performance:
   ollama pull mistral:7b
   ```

4. **Configure environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your preferred model name
   ```

5. **Start the backend API**
   ```bash
   python main.py
   ```

6. **Open the frontend**
   - Navigate to `frontend website code/index.html` in your browser
   - Or serve it with a local web server

The API will be available at `http://localhost:8000`

## 📚 API Documentation

### Core Endpoints

#### 1. Hot Takes Generation
```http
GET /hot-takes?num_takes=5
```
Generates AI-powered controversial but data-supported NBA insights.

**Response:**
```json
{
  "hot_takes": [
    {
      "hot_take": "Player X is overrated as a scorer",
      "rationale": "Despite averaging 25.1 PPG, Player X has a mediocre 0.420 field goal percentage..."
    }
  ],
  "model_used": "llama2:7b",
  "total_players_analyzed": 500
}
```

#### 2. Advanced Statistical Analysis
```http
GET /advanced-analysis?player_name=LeBron James
GET /advanced-analysis?team=LAL
GET /advanced-analysis
```
Provides comprehensive statistical analysis with AI-generated insights for players, teams, or league-wide trends.

#### 3. Player Lookup
```http
GET /player-lookup/{player_name}
```
Returns detailed player profile with custom offensive/defensive scores and AI analysis.

**Response:**
```json
{
  "player_name": "LeBron James",
  "team": "LAL",
  "points_per_game": 25.7,
  "offensive_score": 78.5,
  "defensive_score": 18.2,
  "offensive_rating": "Elite",
  "defensive_rating": "Good",
  "analysis": "AI-generated detailed analysis..."
}
```

#### 4. Additional Endpoints
- `GET /` - API information and available endpoints
- `GET /health` - Health check and system status
- `GET /players` - List all available players
- `POST /collect-data` - Trigger data collection (real or sample)

### Interactive Documentation

Once the server is running:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 🎨 Frontend

The frontend provides an intuitive web interface for all backend features:

- **Home** - Welcome screen and overview
- **Hot Takes** - View AI-generated controversial insights
- **Advanced Analysis** - Player, team, and league analysis
- **Player Lookup** - Search and view detailed player profiles
- **Collect Data** - Trigger data collection
- **Players** - Browse available players
- **Health** - System status check

### Frontend Features
- Modern, responsive design with NBA-themed styling
- Real-time API integration
- Dynamic content rendering
- User-friendly navigation

*Note: Frontend JavaScript implementation is in progress*

## 📁 Project Structure

```
NBA-AI-Powered-Insights-API/
├── Backend API/
│   ├── main.py                 # FastAPI application entry point
│   ├── nba_analytics.py         # Core analytics engine with LLM integration
│   ├── nba_data_collector.py    # Multi-source data collection system
│   ├── requirements.txt         # Python dependencies
│   ├── env.example             # Environment variables template
│   ├── OLLAMA_SETUP.md         # Ollama installation guide
│   ├── README_NBA_API.md       # Detailed backend documentation
│   └── data/                   # NBA data storage (CSV files)
│       └── nba_combined_latest.csv
│
└── frontend website code/
    ├── index.html              # Main frontend page
    ├── styles.css              # Styling and NBA theme
    └── js/                     # JavaScript files (in progress)
        └── app.js
```

## 🌟 Key Highlights

### For Users
- **No API Keys Required** - Uses local LLM, completely private
- **Real NBA Data** - Aggregates from multiple official sources
- **Fast Performance** - Local inference means no external API delays
- **Always Available** - Fallback system ensures functionality even if LLM is unavailable

### For Recruiters/Developers
- **Full-Stack Development** - Demonstrates both backend API design and frontend integration
- **AI/ML Integration** - Shows practical application of LLMs in data analysis
- **Production-Ready Code** - Comprehensive error handling, logging, and documentation
- **Modern Tech Stack** - FastAPI, async programming, RESTful design
- **Scalable Architecture** - Modular design allows easy feature additions
- **Data Engineering** - Multi-source data collection and processing
- **API Design** - Well-structured REST API with OpenAPI documentation

## 🔬 Technical Deep Dive

### Scoring Algorithms

**Offensive Score Formula:**
```
Offensive Score = (Points × 0.3) + (FG% × 100 × 0.2) + (3P% × 100 × 0.15) + 
                  (FT% × 100 × 0.1) + (Assists × 0.15) - (Turnovers × 0.1)
```

**Defensive Score Formula:**
```
Defensive Score = (Steals × 2) + (Blocks × 2) + (Defensive Rebounds × 0.5) - 
                  (Fouls × 0.5)
```

### Data Collection Strategy
1. **Primary**: NBA Stats API (official NBA data)
2. **Secondary**: Basketball Reference (web scraping)
3. **Tertiary**: ESPN API
4. **Fallback**: Enhanced sample data with realistic statistics

### LLM Integration
- Uses Ollama for local inference (privacy-focused)
- Supports multiple models (Llama 2, Mistral, Phi-2)
- Automatic fallback to rule-based analysis
- Optimized prompts for consistent, data-driven responses

## 🧪 Testing

```bash
# Test data collection
python nba_data_collector.py

# Test API endpoints
python test_api.py

# Test with real data
python test_real_data.py
```

## 📝 Configuration

### Environment Variables

```env
# LLM Configuration
LLM_MODEL_NAME=llama2:7b          # Model to use (llama2:7b, mistral:7b, phi:2.7b)

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Data Configuration
DATA_PATH=data/nba_combined_latest.csv
USE_SAMPLE_DATA=false             # Use sample data for testing

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
```

## 🚢 Deployment

### Docker (Recommended)

```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
- Configure CORS origins appropriately
- Set up proper logging and monitoring
- Use environment variables for sensitive data
- Consider database storage for production data
- Set up scheduled data collection jobs

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- NBA Stats API for providing official statistics
- Basketball Reference for historical data
- Ollama team for local LLM infrastructure
- FastAPI for the excellent web framework

## 📧 Contact & Support

For questions, issues, or contributions:
- Open an issue on GitHub
- Check the API documentation at `/docs` when running
- Review `OLLAMA_SETUP.md` for LLM setup help

---

**Built with ❤️ for NBA analytics enthusiasts and developers**

*Showcasing modern full-stack development with AI integration*
