# 🚀 Loud Hawk v2 - Professional Aviation News Aggregator

A comprehensive aviation news aggregation platform with intelligent content ranking, dynamic scheduling, and multi-source integration capabilities.

## ✈️ Features

### **Comprehensive Source Coverage**
- **74+ aviation sources** globally across all sectors
- **Regulators**: FAA, NTSB, EASA, ICAO, Transport Canada, UK CAA, CASA Australia
- **OEMs**: Airbus, Boeing, Embraer, Bombardier, GE Aerospace, Pratt & Whitney, Rolls-Royce
- **Airlines**: Delta, United, Alaska, American, Southwest, Lufthansa, Air France-KLM
- **Media**: Aviation Week, FlightGlobal, AVweb, Simple Flying, The Air Current
- **Industry**: A4A, ACI World, Eurocontrol, NATS
- **Data Providers**: OAG, Flightradar24, RoutesOnline
- **eVTOL**: Joby Aviation, Archer Aviation, Eve Air Mobility, Vertical Aerospace

### **Intelligent Content Management**
- **Authority-weighted ranking** system prioritizes high-signal sources
- **Dynamic scheduling** optimizes polling frequency based on source activity
- **Advanced content filtering** eliminates noise and clickbait
- **Canonical URL deduplication** prevents duplicate articles
- **Content hash fingerprinting** for cross-syndication detection

### **Reliability & Performance**
- **Circuit breaker system** auto-disables problematic sources
- **XML recovery** handles malformed RSS feeds (NTSB, EASA)
- **Smart fallbacks** between RSS, HTML, JSON, and sitemap strategies
- **Realistic HTTP headers** to avoid bot detection
- **Rate limiting** and error handling with graceful degradation

### **Advanced Adapters**
- **12 different adapter strategies** for various source types
- **RSS Native**: Direct RSS/Atom feeds
- **RSS Redirected**: Discover RSS via HTML links
- **HTML Scraping**: With aviation content filtering
- **JSON API**: WordPress and CMS endpoints
- **YouTube Integration**: Aviation video content
- **Sitemap Discovery**: For sources without obvious RSS

## 🏗️ Architecture

### **Backend (Python/FastAPI)**
```
backend/
├── main.py                 # FastAPI application with professional API
├── models.py              # SQLModel data models with deduplication
├── database.py            # Database operations and session management
├── ingest.py              # Multi-strategy news ingestion
├── source_adapters.py     # Advanced source adapter strategies
├── ranking_system.py      # Authority-weighted content ranking
├── dynamic_scheduler.py   # Smart polling frequency management
├── source_health.py       # Circuit breaker and reliability tracking
├── youtube_adapter.py     # YouTube channel integration
├── scheduler.py           # Background task scheduling
├── sources_loader.py      # CSV source import utility
├── trusted_sources.yaml   # Source configuration (23+ sources)
├── osa_sources_seed.csv   # Complete source database (74+ sources)
└── requirements.txt       # Python dependencies
```

### **Frontend (React/TypeScript)**
```
frontend/
├── src/
│   ├── pages/NewsTerminal.tsx  # Main news interface
│   ├── services/api.ts         # API integration
│   ├── types/index.ts          # TypeScript definitions
│   └── App.tsx                 # Application component
├── package.json               # Node.js dependencies
└── vite.config.ts            # Vite build configuration
```

## 🚀 Quick Start

### **Prerequisites**
- Python 3.9+
- Node.js 16+
- SQLite (included with Python)

### **Backend Setup**
```bash
# Navigate to backend
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python3 -c "from database import init_db; init_db()"

# Start the server
python3 main.py
```

The backend will be available at:
- **API**: http://localhost:8000
- **Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

### **Frontend Setup**
```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at: http://localhost:5173

## 📊 API Endpoints

### **Core News API**
- `GET /news` - Get ranked articles with optional filtering
- `GET /search?q={query}` - Search articles by content
- `POST /ingest` - Trigger manual news harvest

### **Source Management**
- `GET /sources` - List all configured sources
- `GET /sources/health` - Source reliability metrics
- `GET /sources/activity` - Dynamic scheduling information
- `POST /sources/{name}/toggle` - Enable/disable sources

### **Advanced Features**
- `GET /ranking/stats` - Authority ranking analytics
- `GET /youtube/channels` - YouTube channel information
- `GET /bookmarks` - User bookmarks management

### **System Health**
- `GET /health` - System health check
- `GET /stats` - System statistics

## 🎯 Key Features in Detail

### **Authority Ranking System**
Sources are ranked by authority and importance:
- **FAA Newsroom**: 100 (highest authority)
- **NTSB Press**: 95
- **EASA News**: 90
- **ICAO Newsroom**: 85
- **Airbus/Boeing**: 80
- **Aviation Week**: 75
- **Simple Flying**: 50
- **YouTube Creators**: 35-40

### **Dynamic Scheduling**
Polling frequencies adapt to source activity:
- **Fast Movers (3 min)**: Simple Flying, FlightGlobal, AVweb
- **Steady Sources (10 min)**: FAA, NTSB, EASA, Airbus, Boeing
- **Moderate Sources (15 min)**: Airlines, industry associations
- **Slow Movers (30 min)**: IR pages, MROs, airports

### **Content Quality**
- **Clickbait filtering**: Removes "You Won't Believe", "Amazing", etc.
- **Aviation keywords**: Rewards relevant aviation content
- **Promotional filtering**: Removes sales/promotional content
- **Technical content**: Rewards analysis, reports, studies

## 🔧 Configuration

### **Source Configuration**
Sources are configured in `trusted_sources.yaml`:
```yaml
- name: "FAA Newsroom"
  category: "REGULATOR"
  weight: 10
  kind: "rss"
  enabled: true
  home: "https://www.faa.gov/newsroom"
  discover: true
```

### **Adding New Sources**
1. **Use CSV Import**: Add to `osa_sources_seed.csv` and run `sources_loader.py`
2. **Manual Addition**: Add to `trusted_sources.yaml` with proper format
3. **API Management**: Use `/sources/{name}/toggle` endpoint

## 📈 Performance

### **Current Metrics**
- **74+ sources** configured globally
- **23+ sources** actively polling
- **Dynamic scheduling** optimizing bandwidth
- **Authority ranking** prioritizing high-signal content
- **Circuit breakers** maintaining reliability
- **Content filtering** ensuring aviation relevance

### **Reliability Features**
- **Error handling**: Graceful degradation on failures
- **Health monitoring**: Real-time source status tracking
- **Auto-recovery**: Smart source re-enabling
- **XML recovery**: Handles malformed feeds
- **Rate limiting**: Prevents over-polling

## 🛠️ Development

### **Adding New Adapter Strategies**
1. Define strategy in `source_adapters.py`
2. Implement fetch logic with error handling
3. Add to adapter manager
4. Configure sources to use new strategy

### **Extending Ranking System**
1. Modify authority weights in `ranking_system.py`
2. Add new quality filters
3. Adjust scoring algorithm
4. Test with real data

### **Database Migrations**
```bash
# Add new fields to models.py
# Run database initialization
python3 -c "from database import init_db; init_db()"
```

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🎉 Acknowledgments

- **Aviation Community**: For providing valuable feedback and source suggestions
- **Open Source**: Built with FastAPI, React, SQLModel, and other excellent tools
- **Data Sources**: All aviation news sources for providing public RSS feeds

---

**Loud Hawk v2** - Your professional aviation news terminal, now with intelligent ranking and comprehensive coverage! ✈️🚀