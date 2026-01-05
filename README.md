# Bo_Check - Movie Booking Statistics Aggregator for India

## Table of Contents

1. [Project Overview](#project-overview)
2. [Problem Statement](#problem-statement)
3. [Solution Approach](#solution-approach)
4. [Features](#features)
5. [System Architecture](#system-architecture)
6. [Technology Stack](#technology-stack)
7. [Project Structure](#project-structure)
8. [Installation and Setup](#installation-and-setup)
9. [Usage](#usage)
10. [API Documentation](#api-documentation)
11. [Expected Output](#expected-output)
12. [Future Enhancements](#future-enhancements)
13. [Disclaimer](#disclaimer)
14. [License](#license)

---

## Project Overview

Bo_Check is a comprehensive movie booking statistics aggregator designed for metropolitan cities across India. The application collects, processes, and presents real-time data about movie show timings, seat availability, ticket prices, and theater information from major booking platforms including BookMyShow and District (by Zomato).

The project provides both a command-line interface for quick data access and a web-based dashboard for detailed visualization and analysis.

---

## Problem Statement

Movie enthusiasts in India often face several challenges when planning to watch a movie:

1. **Scattered Information**: Show timings, prices, and availability are spread across multiple booking platforms, requiring users to check each platform individually.

2. **No Price Comparison**: There is no centralized way to compare ticket prices across different theaters for the same movie.

3. **Lack of Availability Insights**: Understanding seat availability trends and occupancy patterns requires manually checking multiple shows.

4. **No Historical Data**: Booking platforms do not provide historical pricing or occupancy data for analysis.

5. **Limited Accessibility**: Users who prefer command-line tools have no option for quick movie information lookup.

---

## Solution Approach

Bo_Check addresses these challenges through a multi-layered approach:

### Data Collection Layer
- Web scrapers built with async HTTP clients extract data from BookMyShow and District platforms
- Rate limiting and user agent rotation ensure respectful scraping practices
- Data is normalized into a unified schema regardless of source platform

### Data Storage Layer
- PostgreSQL database stores movie, theater, show, and pricing information
- Redis provides caching for frequently accessed data
- Background workers periodically refresh data to maintain accuracy

### Presentation Layer
- RESTful API exposes all data through well-documented endpoints
- Next.js web dashboard provides visual representation of statistics
- Command-line interface offers quick access for power users

---

## Features

### Currently Implemented

| Feature | Description |
|---------|-------------|
| Movie Listings | Browse currently showing movies by city |
| Show Timings | View all show timings across theaters for any movie |
| Seat Availability | Real-time seat availability with category breakdown |
| Ticket Prices | Current ticket prices by seat category and theater |
| Theater Information | Theater details including location and amenities |
| City Support | Eight metropolitan cities supported in Phase 1 |
| Search and Filter | Search movies by name, filter by language and genre |
| CLI Tool | Command-line access for quick data retrieval |
| API Documentation | Auto-generated Swagger documentation |

### Supported Cities

| City | Code | State |
|------|------|-------|
| Mumbai | MUM | Maharashtra |
| Delhi NCR | DEL | Delhi |
| Bangalore | BLR | Karnataka |
| Hyderabad | HYD | Telangana |
| Chennai | CHE | Tamil Nadu |
| Kolkata | KOL | West Bengal |
| Pune | PUN | Maharashtra |
| Ahmedabad | AHM | Gujarat |

---

## System Architecture

```
                                    +------------------+
                                    |   Data Sources   |
                                    +------------------+
                                    | - BookMyShow     |
                                    | - District       |
                                    +--------+---------+
                                             |
                                             v
+------------------+              +------------------+
|   CLI Client     |              |  Scraping Engine |
+------------------+              +------------------+
        |                         | - Base Scraper   |
        |                         | - BMS Scraper    |
        v                         | - District Scrpr |
+------------------+              +--------+---------+
|  FastAPI Backend |<---------------------+
+------------------+
| - REST API       |              +------------------+
| - Data Models    |<------------>|   PostgreSQL     |
| - Business Logic |              +------------------+
+--------+---------+
         |                        +------------------+
         +----------------------->|   Redis Cache    |
         |                        +------------------+
         v
+------------------+              +------------------+
| Next.js Frontend |              |   Celery Worker  |
+------------------+              +------------------+
| - Dashboard      |              | - Background     |
| - Movie Pages    |              |   Scraping Tasks |
| - Analytics      |              +------------------+
+------------------+
```

---

## Technology Stack

### Backend (Python)

| Component | Technology | Purpose |
|-----------|------------|---------|
| API Framework | FastAPI | Async REST API with automatic documentation |
| ORM | SQLAlchemy 2.0 | Async database operations |
| Database | PostgreSQL | Persistent data storage |
| Caching | Redis | Response caching and session storage |
| Task Queue | Celery | Background job processing |
| HTTP Client | httpx | Async HTTP requests for scraping |
| HTML Parsing | BeautifulSoup4 | Web page parsing |
| Browser Automation | Playwright | JavaScript-rendered page handling |
| Data Validation | Pydantic v2 | Request and response validation |
| CLI Framework | Typer | Command-line interface |
| CLI Formatting | Rich | Terminal output formatting |

### Frontend (Node.js)

| Component | Technology | Purpose |
|-----------|------------|---------|
| Framework | Next.js 14 | React-based web application |
| Language | TypeScript | Type-safe JavaScript |
| Styling | Tailwind CSS | Utility-first CSS framework |
| HTTP Client | Fetch API | API communication |

### DevOps

| Component | Technology | Purpose |
|-----------|------------|---------|
| Containerization | Docker | Application packaging |
| Orchestration | Docker Compose | Multi-container management |
| Code Quality | Ruff, ESLint | Linting and formatting |
| Testing | pytest, Jest | Automated testing |

---

## Project Structure

```
Bo_Check/
|
+-- backend/                        Python FastAPI Backend
|   +-- app/
|   |   +-- api/
|   |   |   +-- routes/
|   |   |   |   +-- cities.py       City endpoints
|   |   |   |   +-- movies.py       Movie endpoints
|   |   |   |   +-- theaters.py     Theater endpoints
|   |   |   |   +-- shows.py        Show endpoints
|   |   |   |   +-- stats.py        Statistics endpoints
|   |   |   +-- deps.py             Dependency injection
|   |   +-- models/
|   |   |   +-- schemas.py          SQLAlchemy ORM models
|   |   +-- schemas/
|   |   |   +-- movie.py            Pydantic schemas
|   |   +-- scrapers/
|   |   |   +-- base.py             Base scraper class
|   |   |   +-- bookmyshow.py       BookMyShow scraper
|   |   |   +-- district.py         District scraper
|   |   +-- cli/
|   |   |   +-- main.py             CLI commands
|   |   +-- main.py                 Application entry point
|   |   +-- config.py               Configuration management
|   |   +-- database.py             Database setup
|   +-- requirements.txt            Python dependencies
|   +-- Dockerfile                  Container configuration
|
+-- frontend/                       Next.js Frontend
|   +-- src/
|   |   +-- app/
|   |   |   +-- page.tsx            Dashboard home
|   |   |   +-- layout.tsx          Root layout
|   |   |   +-- globals.css         Global styles
|   |   |   +-- movies/
|   |   |   |   +-- page.tsx        Movies listing
|   |   |   |   +-- [id]/
|   |   |   |       +-- page.tsx    Movie details
|   |   +-- lib/
|   |   |   +-- api.ts              API client
|   |   |   +-- utils.ts            Utility functions
|   |   +-- types/
|   |       +-- movie.ts            TypeScript types
|   +-- package.json                Node dependencies
|   +-- Dockerfile                  Container configuration
|
+-- docker-compose.yml              Full stack orchestration
+-- README.md                       Project documentation
+-- LICENSE                         Apache 2.0 License
```

---

## Installation and Setup

### Prerequisites

- Python 3.10 or higher
- Node.js 18 or higher
- PostgreSQL 14 or higher
- Redis 6 or higher
- Docker and Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/Bo_Check.git
cd Bo_Check

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option 2: Manual Setup

#### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file and configure
cp .env.example .env

# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

---

## Usage

### Web Dashboard

Access the web dashboard at `http://localhost:3000` after starting the application.

- **Home Page**: City selector, quick stats, and trending movies
- **Movies Page**: Full movie listing with search and filters
- **Movie Details**: Show timings, seat availability, and pricing

### API Access

Access the API documentation at `http://localhost:8000/docs` for interactive testing.

### Command-Line Interface

```bash
# Install CLI tool
cd backend
pip install -e .

# List supported cities
bo-check cities

# Get movies in a city
bo-check movies --city MUM

# Get show timings for a movie
bo-check shows "Movie Name" --city HYD --date 2026-01-06

# Compare prices
bo-check prices "Movie Name" --city BLR

# Export data to file
bo-check export movies --city DEL --format json --output delhi_movies.json
```

---

## API Documentation

### Endpoints Overview

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/v1/cities | List all supported cities |
| GET | /api/v1/cities/{code} | Get city details |
| GET | /api/v1/movies | List movies with filters |
| GET | /api/v1/movies/{id} | Get movie details |
| GET | /api/v1/movies/{id}/shows | Get show timings for a movie |
| GET | /api/v1/movies/search/{query} | Search movies by name |
| GET | /api/v1/theaters | List theaters in a city |
| GET | /api/v1/theaters/{id} | Get theater details |
| GET | /api/v1/theaters/{id}/shows | Get shows at a theater |
| GET | /api/v1/shows/{id} | Get show details |
| GET | /api/v1/shows/{id}/seats | Get seat availability |
| GET | /api/v1/stats/overview | City overview statistics |
| GET | /api/v1/stats/movie/{id} | Movie-specific statistics |
| GET | /api/v1/stats/trending | Trending movies |
| GET | /api/v1/stats/price-comparison | Price comparison across theaters |

---

## Expected Output

### Web Dashboard Output

The web dashboard provides:

1. **Dashboard View**: Visual representation of movies currently showing, with city selection and quick statistics including total theaters, shows, and average prices.

2. **Movie Listing**: Grid view of movies with poster, rating, language, genre, and duration. Supports filtering by language and searching by title.

3. **Movie Details View**: Comprehensive show information including:
   - All theaters showing the movie
   - Show timings for each theater
   - Seat availability by category (Standard, Premium, Recliner)
   - Ticket prices with color-coded availability status

### CLI Output

```
$ bo-check movies --city HYD

Movies in Hyderabad

 # | Movie                  | Language | Genre          | Rating
---+------------------------+----------+----------------+--------
 1 | Pushpa 2: The Rule     | Telugu   | Action, Drama  | 8.5
 2 | Kalki 2898 AD          | Telugu   | Sci-Fi, Action | 8.2
 3 | Fighter                | Hindi    | Action, Thrill | 7.8

Showing 3 of 24 movies
```

### API Response Example

```json
{
  "movies": [
    {
      "id": 1,
      "name": "Pushpa 2: The Rule",
      "language": "Telugu",
      "genres": ["Action", "Drama"],
      "rating": 8.5,
      "duration_mins": 180,
      "certification": "UA"
    }
  ],
  "total": 24,
  "page": 1,
  "per_page": 20,
  "city": "HYD"
}
```

---

## Future Enhancements

### Phase 2: Extended Features

| Enhancement | Description |
|-------------|-------------|
| Additional Cities | Expand coverage to 20+ cities across India |
| More Platforms | Integration with additional booking platforms |
| Box Office Data | Daily and weekly collection tracking |
| User Accounts | Personal watchlists and notification preferences |
| Price Alerts | Notifications when prices drop for selected movies |
| Mobile Application | Native iOS and Android applications |

### Phase 3: Advanced Analytics

| Enhancement | Description |
|-------------|-------------|
| Historical Trends | Price and occupancy trends over time |
| Predictive Analytics | ML-based demand forecasting |
| Recommendation Engine | Personalized movie suggestions |
| Sentiment Analysis | Review aggregation and sentiment scoring |
| Theater Ratings | User-contributed theater ratings and reviews |

### Phase 4: Enterprise Features

| Enhancement | Description |
|-------------|-------------|
| Theater Dashboard | Analytics dashboard for theater owners |
| API Monetization | Paid API access for third-party applications |
| WhatsApp Integration | Movie information via WhatsApp bot |
| Voice Assistant | Integration with Alexa and Google Assistant |

### Technical Improvements

| Improvement | Description |
|-------------|-------------|
| Database Migrations | Alembic for version-controlled schema changes |
| Comprehensive Testing | Unit, integration, and end-to-end tests |
| CI/CD Pipeline | Automated testing and deployment |
| Monitoring | Application performance monitoring and alerting |
| Rate Limiting | API rate limiting for fair usage |
| Authentication | JWT-based API authentication |

---

## Disclaimer

This project is developed for educational and personal use only. Web scraping may violate the Terms of Service of the target platforms (BookMyShow, District). Users are responsible for ensuring compliance with applicable laws and platform policies.

The developers of this project:
- Do not encourage or condone any misuse of this software
- Are not responsible for any consequences of using this software
- Recommend implementing appropriate rate limiting and respecting robots.txt

---

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.

---

## Contributing

Contributions are welcome. Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes with appropriate tests
4. Submit a pull request with a clear description

---

## Contact

For questions, suggestions, or issues, please open an issue on the GitHub repository.