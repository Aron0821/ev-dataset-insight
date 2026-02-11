# Electric Vehicle Dataset Insight

<div align="center">

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-00ADD8.svg)](https://github.com/facebookresearch/faiss)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-ML-F7931E.svg?logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)

**A comprehensive end-to-end data engineering and analytics platform for electric vehicle analysis**

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#️-architecture) • [Documentation](#-project-structure)

</div>

---

## 🎯 Overview

**EV-DATASET-INSIGHT** is a complete data platform for analyzing electric vehicle datasets, featuring automated ETL pipelines, interactive visualizations, AI-powered insights, and predictive machine learning models.

**Key Capabilities:**
- 🗄️ **PostgreSQL + PostGIS** - Robust data storage with geospatial support
- 🔄 **Automated ETL Pipeline** - Data quality checks and validation
- 📊 **Interactive Dashboard** - 8 comprehensive analysis tabs with real-time filtering
- 🤖 **RAG-based AI Chatbot** - Natural language queries using FAISS vector search
- 🗺️ **Geospatial Analysis** - Interactive mapping with coordinate debugging tools
- 🔮 **ML Predictions** - Range prediction and adoption forecasting models

---

## ✨ Features

### Database & ETL
- **Normalized Relational Schema** - Referential integrity and optimized queries
- **Automated Migrations** - Using sync-db for version control
- **PostGIS Integration** - Geographic queries and spatial indexing
- **SQL Stored Procedures** - Efficient data transformation
- **Complete ETL Pipeline** - Extract, transform, load with validation
- **Data Quality Checks** - Automated validation and error handling

### Analytics Dashboard
- 📈 **Trends Analysis** - Registration patterns and time-series analysis
- 🏭 **Manufacturer Insights** - Market share, top models, and brand comparison
- 🗺️ **Geographic Distribution** - State/county analysis with interactive maps
  - Built-in map debugging tool
  - Support for both PostGIS and standard POINT formats
  - Coordinate validation and error diagnostics
- ⚡ **Performance Metrics** - Electric range comparisons and CAFV eligibility
- 📋 **Data Explorer** - Searchable table with pagination and CSV export
- 🤖 **AI Analyst** - Natural language queries powered by RAG
- 🔮 **Range Prediction** - ML model for predicting vehicle range
- 📊 **Adoption Forecast** - Polynomial regression for future trends

### AI & Machine Learning
- 🔍 **FAISS Vector Search** - Fast similarity-based retrieval (50,000+ embeddings)
- 💬 **RAG Chatbot** - Context-aware responses using LangChain
- 📚 **Vector Embeddings** - Semantic search with sentence-transformers
- 🧠 **LLM Integration** - Groq API for natural language understanding
- 🎯 **Random Forest** - Range prediction model with feature importance
- 📈 **Polynomial Regression** - Adoption forecasting with customizable complexity

### Interactive Visualizations
- **Real-time Filtering** - Dynamic updates across all visualizations
- **Plotly Charts** - Interactive, responsive visualizations
- **Custom Color Schemes** - Professional, accessible color palettes
- **Export Capabilities** - Download data and charts
- **Responsive Design** - Works on desktop and mobile

---

## 📸 Dashboard Screenshots

### 📊 Analytics Overview
![Overview](image/Overview.png)
*Summary metrics with total vehicles, manufacturers, models, and average range*

### 🏭 Manufacturer Insights
![Manufacturer Insights](image/Manufacturer.png)
*Top manufacturers, market share analysis, and model rankings*

### 🗺️ Geographic Distribution
![Geo Distribution](image/GeoDistribution.png)
*Interactive map with state/county distribution and built-in debugging tools*

### ⚡ Performance Metrics
![Electric Range Analysis](image/evRange.png)
*Range distribution, manufacturer comparison, and year-over-year trends*

### 📋 Data Explorer
![Data Table](image/DataTable.png)
*Searchable, paginated data table with advanced filtering*

### 🤖 AI Chatbot (RAG)
![AI Chatbot](image/Chatbot.png)
*Natural language queries with context-aware responses*

### 🔮 Range Prediction
![Range Prediction](image/RangePrediction.png)
*ML-powered range prediction with feature importance analysis*

### 📊 Adoption Forecast
![Adoption](image/Adoption.png)
*Future adoption trends using polynomial regression*

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          SYSTEM ARCHITECTURE                                │
└─────────────────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │   Data Sources   │
    │   • APIs         │
    └────────┬─────────┘
             │
             ▼
    ┌─────────────────────────┐
    │    ETL PIPELINE         │
    ├─────────────────────────┤
    │  1. Extract  ────────▶  │ • Data validation
    │  2. Transform ───────▶  │ • Quality checks
    │  3. Load  ──────────▶   │ • Error handling
    └────────┬────────────────┘
             │
             ▼
┌────────────────────────────────────────────────────────────────────┐
│                   POSTGRESQL DATABASE (PostGIS)                    │
├────────────────────────────────────────────────────────────────────┤
│                                                                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐              │
│  │    model     │  │   location   │  │   vehicle    │              │
│  │              │  │              │  │              │              │
│  │ • model_id   │  │ • location_id│  │ • vehicle_id │              │
│  │ • make       │  │ • city       │  │ • vin        │              │  
│  │ • model      │  │ • state      │  │ • model_id   │              │
│  │              │  │ • county     │  │ • location_id│              │
│  │              │  │ • lat/lon    │  │ • model_year │              │
│  │              │  │ • postal_code│  │ • ev_type    │              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                    │
│  ┌──────────────────────────────────────────────────┐              │
│  │        electric_vehicles (Staging)               │              │
│  │  • Raw data before normalization                 │              │
│  │  • Supports incremental loads                    │              │
│  └──────────────────────────────────────────────────┘              │
│                                                                    │
└─────────────────────────┬──────────────────────────────────────────┘
                          │
          ┌───────────────┴─────────────────┐
          │                                 │
          ▼                                 ▼
    ┌──────────────┐              ┌──────────────────┐
    │  FAISS Index │              │   Streamlit      │
    │              │              │   Dashboard      │
    │ • 50K+       │              │                  │
    │   Vectors    │              │ • 8 Tabs         │
    │ • Similarity │              │ • ML Models      │
    │   Search     │              │ • Filters        │
    │ • L2 Distance│              │ • Geo Debug      │
    └──────┬───────┘              └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │  AI Chatbot  │
    │              │
    │ • RAG System │
    │ • LLM (Groq) │
    │ • Q&A        │
    │ • FastAPI    │
    └──────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                           │
└─────────────────────────────────────────────────────────────────────┘

  Raw Data          ETL Pipeline              Database              Application
     │                   │                        │                      │
     │                   │                        │                      │
┌────▼────┐         ┌────▼────┐            ┌─────▼──────┐        ┌─────▼──────┐
│   API   │  ─────▶ │ Extract │  ────────▶ │  Staging   │  ────▶ │  Dashboard │
│         │         │ Validate│            │   Table    │        │            │
└─────────┘         └─────────┘            └─────┬──────┘        │ • Trends   │
                          │                      │               │ • Geo Map  │
                          │                      │               │ • AI Chat  │
                          ▼                      ▼               │ • ML Models│
                    ┌──────────┐           ┌──────────┐          └────────────┘
                    │Transform │  ───────▶ │   model  │
                    │  Clean   │           │ location │
                    │ Normalize│           │ vehicle  │
                    └──────────┘           └──────────┘
                          │                      │
                          │                      │
                          ▼                      ▼
                    ┌──────────┐           ┌──────────┐
                    │   Load   │  ───────▶ │ Indexed  │
                    │ Reference│           │   Data   │
                    └──────────┘           └────┬─────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │ Vector Store│
                                          │   (FAISS)   │
                                          │  + Metadata │
                                          └─────────────┘
```

---

## 📁 Project Structure

```
EV-DATASET-INSIGHT/
│
├── 📁 db/                                   Database Layer
│   └── 📁 src/
│       │
│       ├── 📁 migrations/                   Migration files (.up/.down.sql)
│       │   ├── *_create_table_electric_vehicles.*
│       │   ├── *_create_table_model.*
│       │   ├── *_create_table_location.*
│       │   ├── *_create_table_vehicle.*
│       │   └── *_create_std_table_electric_vehicles.*
│       │
│       ├── 📁 scripts/                      ETL Scripts
│       │   ├── 📁 util/
│       │   │   └── db_connection.py         Database connector
│       │   ├── extract.py                   Data extraction from sources
│       │   ├── transform.py                 Data cleaning & validation  
│       │   └── load.py                      Data loading to database
│       │
│       └── 📁 sql/
│           ├── 📁 procedure/                Stored procedures
│           │   ├── load_location.sql        Location data loader
│           │   ├── load_model.sql           Model data loader
│           │   ├── load_vehicle.sql         Vehicle data loader
│           │   └── transform_electric_vehicle.sql
│           └── 📁 view/                     SQL views
│
├── 📁 ev_faiss_index/                       FAISS Vector Index
│   ├── index.faiss                          Vector index file
│   └── index.pkl                            Metadata & mappings
│
├── 📁 visualization/                        Streamlit Dashboard
|   ├── 📁 chatbot/
|   │   ├── retriever.py                     Vector search & context
|   │   └── vector_store.py                  Embeddings & vector database
|   │   └── intelligent_chatbot.py           
|   ├── 📁 components/
|   │   ├── 📁 tabs/                         Individual features
|   │   │   ├── __init__.py
|   │   │   ├── ai_analyst.py
|   │   │   ├── data_table.py
|   │   │   ├── forecast.py
|   │   │   ├── geographic.py
|   │   │   ├── manufacturers.py
|   │   │   ├── performance.py
|   │   │   ├── prediction.py
|   │   │   └── trends.py
|   │   ├── __init__.py
|   │   ├── metrics.py
|   │   └── sidebar.py
|   ├── 📁 config/
|   │   ├── __init__.py
|   │   └── page_config.py
|   ├── 📁 utils/
|   │   ├── __init__.py
|   │   ├── data_loader.py                   All SQL queries
|   │   ├── database.py                      PostgreSQL connection handler
|   │   ├── map_debug.py
|   │   └── ml_models.py                     ML training/prediction
|   ├── app.py                               Main application (loads everything)    
|   ├── main.py
|   ├── test_chatbot.py
|   ├── text_to_sql.py
|   ├── vector_db.py
|   └── verify_setup.py                      Vector DB builder
│
├── 📁 image/                                Screenshots
│   ├── Overview.png
│   ├── Manufacturer.png
│   ├── GeoDistribution.png
│   ├── evRange.png
│   ├── DataTable.png
│   ├── Chatbot.png
│   ├── RangePrediction.png
│   └── Adoption.png
│
├── ⚙️  Configuration
│   ├── .env                                 Environment variables
│   ├── connection-resolver.js               DB connection config
│   ├── sync-db.yml                          Migration config
│   ├── package.json                         Node dependencies
│   └── requirements.txt                     Python dependencies
│
├── 🚀 Entry Points
│   └── main.py                              ETL orchestrator
│
└── 📚 Documentation
    └── README.md                            
```

---

## 🛠️ Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                           │
└─────────────────────────────────────────────────────────────────┘

Database Layer              Backend Layer              Frontend Layer
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│ PostgreSQL   │           │ Python 3.8+  │           │ Streamlit    │
│    12+       │◀─────────▶│              │◀─────────▶│   1.28+      │
│              │           │ • pandas     │           │              │
│ PostGIS 3.0+ │           │ • psycopg2   │           │ Plotly 5.17+ │
│              │           │ • NumPy      │           │              │
│ Point/       │           │ • scikit-    │           │ • Mapbox     │
│ Geometry     │           │   learn      │           │ • Charts     │
└──────────────┘           └──────────────┘           └──────────────┘
       │                          │                          │
       │                          │                          │
       └────────────┬─────────────┴──────────────┬───────────┘
                    │                            │
                    ▼                            ▼
            ┌──────────────┐           ┌──────────────────┐
            │  Migration   │           │   AI/ML Layer    │
            │              │           │                  │
            │  sync-db     │           │  • FAISS         │
            │  Node.js 14+ │           │  • LangChain     │
            │  Yarn        │           │  • Groq API      │
            │              │           │  • Transformers  │
            │              │           │  • FastAPI       │
            └──────────────┘           └──────────────────┘

Dependencies:
├── Data Processing: pandas, numpy, psycopg2-binary
├── Visualization: streamlit, plotly
├── ML/AI: scikit-learn, faiss-cpu, sentence-transformers, langchain
├── API: fastapi, uvicorn, requests
└── Database: PostgreSQL 12+, PostGIS 3.0+
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- PostgreSQL 12+ with PostGIS extension
- Node.js 14+ and Yarn
- Git

### Installation

**1. Clone repository**
```bash
git clone https://github.com/Aron0821/ev-dataset-insight.git
cd ev-dataset-insight
```

**2. Set up virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

**3. Install dependencies**
```bash
# Node.js for migrations
yarn install

# Python packages
pip install -r requirements.txt
```

**4. Configure environment**
```bash
cp .env_example .env
# Edit .env with your credentials:
# - DATABASE_URL=postgresql://user:password@localhost:5432/ev_db
# - GROQ_API_KEY=your_groq_api_key
```

**5. Set up database**
```bash
# Create database
createdb ev_db

# Enable PostGIS
psql ev_db -c "CREATE EXTENSION postgis;"

# Run migrations
yarn sync-db synchronize
```

**6. Run ETL pipeline**
```bash
cd db
python main.py
# Select: 4 (All - Extract, Transform, Load)
```

**7. Build vector index** (for AI chatbot)
```bash
cd visualization
python vector_db.py
```

**8. Launch application**

Open two terminal windows:

**Terminal 1 - FastAPI Server:**
```bash
cd visualization
python main.py
# Server runs on: http://localhost:8000
```

**Terminal 2 - Streamlit Dashboard:**
```bash
streamlit run visualization/app.py
# Dashboard opens at: http://localhost:8501
```
---

## 📊 Dashboard Features

### 1. Trends Analysis
- Vehicle registration patterns by year
- EV type distribution (BEV vs PHEV)
- Time-series trend analysis
- Interactive filtering by state, make, model year

### 2. Manufacturer Insights
- Top 10 manufacturers by market share
- Top 15 vehicle models
- Market concentration analysis
- Brand performance comparison

### 3. Geographic Distribution
- State and county-level analysis
- Interactive map with vehicle locations
- Sample or full dataset mapping options
- Built-in coordinate debugging tools

### 4. Performance Metrics
- Electric range distribution
- Range by manufacturer
- Year-over-year range trends
- BEV vs PHEV comparison
- CAFV eligibility analysis

### 5. Data Explorer
- Searchable, paginated data table
- Multi-field search (VIN, make, model, city)
- CSV export functionality
- Real-time filtering

### 6. AI Analyst
- Natural language queries
- RAG-based context retrieval
- LLM-powered responses
- Conversation history

### 7. Range Prediction
- Random Forest regression model
- Feature importance analysis
- Predict range based on:
  - Model year
  - Make/model
  - EV type
  - State
  - CAFV eligibility

### 8. Adoption Forecast
- Polynomial regression forecasting
- Customizable prediction horizon (1-10 years)
- Adjustable model complexity
- Historical vs predicted visualization

---

## 🤖 AI Chatbot Usage

The RAG-based chatbot can answer questions like:

- "What's the average range of Tesla vehicles?"
- "Which state has the most EVs?"
- "Show me BEV adoption trends"
- "Compare range between manufacturers"
- "What percentage are PHEVs?"

**How it works:**
1. Question is embedded using sentence-transformers
2. FAISS finds similar vehicle records
3. Context is passed to LLM (Groq)
4. LLM generates contextual answer

---

## 🔧 Configuration

### Environment Variables (.env)

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=DB_NAME
DB_USER=your_username
DB_PASSWORD=your_password

# Dataset
API_URL = "https://data.wa.gov/resource/f6w7-q2d2.csv"

# AI/ML
GROQ_API_KEY=your_groq_api_key

```

## 🔄 ETL Pipeline Details

### Extract
- Reads API data
- Validates data structure
- Handles missing values
- Logs extraction statistics

### Transform
- Cleans and normalizes data
- Creates POINT geometries
- Validates data types
- Removes duplicates

### Load
- Loads to staging table
- Calls stored procedures for normalization
- Creates model, location, vehicle records
- Maintains referential integrity
- Handles conflicts (upsert)
