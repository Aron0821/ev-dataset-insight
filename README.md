# Electric Vehicle Dataset Insight

<div align="center">

[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-12%2B-316192.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28%2B-FF4B4B.svg?logo=streamlit&logoColor=white)](https://streamlit.io/)
[![FAISS](https://img.shields.io/badge/FAISS-Vector_Search-00ADD8.svg)](https://github.com/facebookresearch/faiss)

**A comprehensive end-to-end data engineering and analytics platform for electric vehicle analysis**

[Features](#-features) • [Quick Start](#-quick-start)

</div>

---

## 🎯 Overview

**EV-DATASET-INSIGHT** is a complete data platform for analyzing electric vehicle datasets, featuring automated ETL pipelines, interactive visualizations, and AI-powered insights.

**Key Capabilities:**
- 🗄️ PostgreSQL + PostGIS for robust data storage
- 🔄 Automated ETL pipeline with data quality checks
- 📊 Interactive Streamlit dashboard with 6 analysis tabs
- 🤖 RAG-based AI chatbot using FAISS vector search
- 🗺️ Geospatial analysis with interactive mapping

---

## ✨ Features

### Database & ETL
- Normalized relational schema with referential integrity
- Automated migrations using sync-db
- PostGIS integration for geographic queries
- SQL stored procedures for data transformation
- Complete ETL pipeline with validation

### Analytics Dashboard
- 📈 **Trends Analysis** - Registration patterns over time
- 🏭 **Manufacturer Insights** - Market share and top models
- 🗺️ **Geographic Distribution** - State/county analysis with maps
- ⚡ **Performance Metrics** - Electric range comparisons
- 📋 **Data Explorer** - Searchable table with CSV export
- 🎨 **Interactive Charts** - Plotly visualizations with filters

### AI & Machine Learning
- 🔍 **FAISS Vector Search** - Fast similarity-based retrieval
- 💬 **RAG Chatbot** - Natural language queries on EV data
- 📚 **Vector Embeddings** - Semantic search capabilities
- 🧠 **Context-Aware Responses** - LLM-powered answers

---

## 📸 Dashboard Screenshots

### 📊 Analytics Overview
![Overview](image/Overview.png)

### 🏭 Manufacturer Insights
![Manufacturer Insights](image/Manufacturer.png)

### 🗺️ Geographic Distribution
![Geo Distribution](image/GeoDistribution.png)

### ⚡ Performance Metrics
![Electric Range Analysis](image/evRange.png)

### 🤖 AI Chatbot (RAG)
![Data Table](image/DataTable.png)

### 📋 Data Explorer
![AI Chatbot](image/Chatbot.png)

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
    │  1. Extract  ────────▶  │
    │  2. Transform ───────▶  │
    │  3. Load  ──────────▶   │
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
│  │              │  │ • lat/lon    │  │ • location_id│              │
│  └──────────────┘  └──────────────┘  └──────────────┘              │
│                                                                    │
│  ┌──────────────────────────────────────────────────┐              │
│  │        electric_vehicles (Staging)                │             │
│  │  • Raw data before normalization                 │              │
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
    │ • Vector     │              │                  │
    │   Embeddings │              │ • 6 Tabs         │
    │ • Similarity │              │ • Charts         │
    │   Search     │              │ • Filters        │
    └──────┬───────┘              └──────────────────┘
           │
           ▼
    ┌──────────────┐
    │  AI Chatbot  │
    │              │
    │ • RAG System │
    │ • LLM (Groq) │
    │ • Q&A        │
    └──────────────┘
```

### Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         DATA FLOW DIAGRAM                            │
└─────────────────────────────────────────────────────────────────────┘

  Raw Data          ETL Pipeline              Database              Application
     │                   │                        │                      │
     │                   │                        │                      │
┌────▼────┐         ┌────▼────┐            ┌─────▼──────┐        ┌─────▼──────┐
│   API   │  ─────▶ │ Extract │  ────────▶ │  Staging   │  ────▶ │  Dashboard │
│         │         │         │            │   Table    │        │            │
└─────────┘         └─────────┘            └─────┬──────┘        │ • Trends   │
                          │                      │               │ • Geo Map  │
                          │                      │               │ • AI Chat  │
                          ▼                      ▼               └────────────┘
                    ┌──────────┐           ┌──────────┐
                    │Transform │  ───────▶ │   model  │
                    │  Clean   │           │ location │
                    │ Validate │           │ vehicle  │
                    └──────────┘           └──────────┘
                          │                      │
                          │                      │
                          ▼                      ▼
                    ┌──────────┐           ┌──────────┐
                    │   Load   │  ───────▶ │ Indexed  │
                    │ Normalize│           │   Data   │
                    └──────────┘           └────┬─────┘
                                                 │
                                                 ▼
                                          ┌─────────────┐
                                          │ Vector Store│
                                          │   (FAISS)   │
                                          └─────────────┘
```

---

## 📁 Project Structure

```
EV-DATASET-INSIGHT/
│
├── 📁 db/  
|   |── 📁 src                                  Database Layer
│       │
│       ├── 📁 migrations/                        Migration files (.up/.down.sql)
│       │   ├── *_create_table_electric_vehicles.*
│       │   ├── *_create_table_model.*
│       │   ├── *_create_table_location.*
│       │   └── *_create_table_vehicle.*
|       |   └── *_create_std_table_electric_vehicles.*
│       │
│       ├── 📁 scripts/                       ETL Scripts
│       │   ├── extract.py                        Data extraction
│       │   ├── transform.py                      Data transformation  
│       │   └── load.py                           Data loading
│       │
│       └── 📁 sql/
│          ├── 📁 procedure/                     Stored procedures
│          │   ├── load_location.sql
│          │   ├── load_model.sql
│          │   ├── load_vehicle.sql
│          │   └── transform_electric_vehicle.sql
│          └── 📁 view/                          SQL views
│
├── 📁 ev_faiss_index/                        FAISS Vector Index
│   ├── index.faiss                           Vector index file
│   └── index.pkl                             Metadata
│
├── 📁 visualization/                         Streamlit Dashboard
│   ├── 📁 chatbot/                           AI Chatbot Module
│   │   ├── retriever.py                      Document retrieval
│   │   └── vector_store.py                   FAISS management
│   ├── app.py                                Main dashboard app
│   ├── main.py                               Alternative entry
│   ├── text_to_sql.py                        Text-to-SQL
│   └── vector_db.py                          Vector DB builder
│
├── ⚙️  Configuration
│   ├── .env                                  Environment variables
│   ├── connection-resolver.js                DB connection config
│   ├── sync-db.yml                           Migration config
│   ├── package.json                          Node dependencies
│   └── requirements.txt                      Python dependencies
│
├── 🚀 Entry Points
│   └── main.py                               ETL orchestrator
│
└── 📚 Documentation
    └── README.md                            
```

---

## 🛠️ Technology Stack

```
┌─────────────────────────────────────────────────────────────────┐
│                      TECHNOLOGY STACK                            │
└─────────────────────────────────────────────────────────────────┘

Database Layer              Backend Layer              Frontend Layer
┌──────────────┐           ┌──────────────┐           ┌──────────────┐
│ PostgreSQL   │           │ Python 3.8+  │           │ Streamlit    │
│    12+       │◀─────────▶│              │◀─────────▶│   1.28+      │
│              │           │ • pandas     │           │              │
│ PostGIS 3.0+ │           │ • psycopg2   │           │ Plotly 5.17+ │
│              │           │ • NumPy      │           │              │
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
            └──────────────┘           │  • Transformers  │
                                       └──────────────────┘
```

---

## 🚀 Quick Start

- Clone repository
```bash
git clone https://github.com/Aron0821/ev-dataset-insight.git
cd ev-dataset-insight
```

- Set up virtual environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

- Install dependencies
```bash
npm install -g yarn                 # Node.js for migrations
pip install -r requirements.txt     # Python packages
```

- Configure environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

- Set up database

```bash
yarn sync-db synchronize
```

- Run ETL pipeline

```bash
cd db
python main.py
# Select: 4 (All)
```

- Build vector index

```bash
cd visualization
python vector_db.py
````

- Launch dashboard

```bash
cd visualization
python main.py                      # Start fastAPI
cd .. 
streamlit run visualization/app.py
# Open: http://localhost:8501
# run python main.py and streamlit run visualization/app.py in different terminal. Both should be running.
```
