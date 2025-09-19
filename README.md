# ✈️ Loud Hawk v2 - Aviation News Terminal

A clean, Bloomberg Terminal-style aviation news aggregator that pulls from 20+ RSS feeds across the aviation industry.

## 🎯 What It Does

**Loud Hawk v2** is your one-stop cockpit dashboard for aviation news. No AI, no auto-posting, just clean aggregation and navigation of all aviation-related content.

### Key Features

- **📡 RSS Aggregation** - 20+ aviation sources (FAA, NTSB, airlines, OEMs, media)
- **🖥️ Terminal Interface** - Bloomberg Terminal-inspired dark theme
- **🔍 Real-time Search** - Full-text search across all articles
- **📱 Mobile Optimized** - Perfect for pilots on tablets
- **⚡ Auto-sync** - Background polling every 5 minutes
- **🎨 Loud Hawk Branding** - Orange/purple accents, professional typography

## 🚀 Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
python3 main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

**Access Points:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## 📊 Data Sources

### Regulatory & Safety
- FAA News
- NTSB Reports
- EASA Updates
- ICAO News

### Airlines
- Alaska Airlines
- Southwest
- American Airlines
- United Airlines
- Delta Air Lines
- JetBlue Airways
- Spirit Airlines
- Frontier Airlines

### OEMs
- Boeing
- Airbus
- Embraer
- Bombardier
- Gulfstream
- Cessna
- Piper

### Media & Industry
- AVWeb
- FlightGlobal
- AeroTime
- The Points Guy
- AirlineGeeks
- Simple Flying
- Airlines for America

### eVTOL & Future Aviation
- Joby Aviation
- Archer Aviation
- Lilium

### Organizations
- AOPA
- NBAA
- NASA Aeronautics

## 🏗️ Architecture

### Backend (FastAPI)
- **Models**: Simple `NewsArticle` schema
- **Database**: PostgreSQL with deduplication
- **Scheduler**: APScheduler for 5-minute polling
- **Feeds**: RSS parsing with error handling

### Frontend (React + TypeScript)
- **Terminal UI**: Dark theme with Loud Hawk branding
- **Responsive**: Mobile-first design
- **Real-time**: Auto-refresh and manual sync
- **Search**: Client-side filtering and server-side search

## 🎨 Design Philosophy

**Bloomberg Terminal meets Aviation** - Professional, data-dense interface optimized for aviation professionals who need quick access to industry news.

### Brand Colors
- **Orange** (`#f17500`) - Energy, movement, visibility
- **Purple** (`#6c5ce7`) - Creativity, innovation, mystery
- **Cream** (`#f8f9fa`) - Neutrality, clarity
- **Dark** (`#0d1117`) - Terminal background

## 📱 Mobile Experience

Optimized for pilots using tablets in the cockpit:
- Touch-friendly interface
- Readable typography
- Responsive sidebar
- iOS zoom prevention

## 🔧 API Endpoints

- `GET /news` - Get articles with filtering
- `GET /search?q=query` - Search articles
- `GET /sources` - List all sources
- `POST /ingest` - Manual news sync
- `GET /health` - Health check

## 🚀 Deployment

### Backend
- **Database**: SQLite (default) or PostgreSQL
- **Hosting**: Fly.io / Railway / Render
- **Environment**: `DATABASE_URL` (optional, defaults to SQLite)

### Frontend
- **Hosting**: Vercel / Netlify
- **Environment**: `VITE_API_BASE_URL` for backend URL

## 📈 Performance

- **Deduplication**: Content hashing prevents duplicates
- **Caching**: Efficient database queries with indexes
- **Error Handling**: Graceful degradation for failed feeds
- **Auto-sync**: Background polling without user intervention

## 🔮 Future Roadmap

### v2.1 (Next Sprint)
- [ ] Article bookmarking/favorites
- [ ] Email digest features
- [ ] More RSS feeds
- [ ] Category filtering

### v2.2 (Future)
- [ ] Mobile app (React Native)
- [ ] Push notifications
- [ ] Custom RSS feed management
- [ ] Analytics dashboard

## 🛠️ Development

### Adding New Feeds
Edit `backend/feeds.py` and add to `AVIATION_FEEDS`:

```python
"New Source": {
    "url": "https://example.com/rss",
    "category": "Category",
    "weight": 5
}
```

### Customizing UI
Edit `frontend/src/App.css` for styling changes.

## 📄 License

MIT License - Built for the aviation community.

---

**Loud Hawk v2** - Your aviation news cockpit dashboard. ✈️