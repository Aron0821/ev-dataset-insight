# EV Dashboard - Intelligent Analytics Platform

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure .env is configured in project root
# Required: GROQ_API_KEY, DB credentials

# Run dashboard
streamlit run app.py

# Dashboard opens at: http://localhost:8501
```

**Note:** Only ONE command needed! No separate API server required.

---

## 📁 Project Structure

```
visualization/
├── 📁 chatbot/                          AI Intelligence Layer
│   └── intelligent_chatbot.py           Hybrid AI chatbot (Groq AI + SQL)
│
├── 📁 components/                       UI Components
│   ├── 📁 tabs/                         8 Analytics Modules
│   │   ├── __init__.py
│   │   ├── ai_analyst.py                AI-powered natural language queries
│   │   ├── data_table.py                Searchable vehicle data table
│   │   ├── forecast.py                  Adoption trend forecasting
│   │   ├── geographic.py                Interactive maps & location analysis
│   │   ├── manufacturers.py             Market share & brand analysis
│   │   ├── performance.py               Range & performance metrics
│   │   ├── prediction.py                ML-based range prediction
│   │   └── trends.py                    Registration trends over time
│   ├── __init__.py
│   ├── metrics.py                       Dashboard KPIs and statistics
│   └── sidebar.py                       Navigation and filters
│
├── 📁 config/                           Configuration
│   ├── __init__.py
│   └── page_config.py                   Streamlit page setup
│
├── 📁 utils/                            Helper Utilities
│   ├── __init__.py
│   ├── data_loader.py                   SQL queries & data fetching
│   ├── database.py                      PostgreSQL connection handler
│   ├── map_debug.py                     Map visualization helpers
│   └── ml_models.py                     ML training & prediction
│
├── 📝 Documentation
│   ├── README.md                        This file
│   ├── PRESENTATION_GUIDE.md            Complete presentation guide
│   ├── CHATBOT_ARCHITECTURE.md          Chatbot technical details
│   ├── DATABASE_ERROR_FIX.md            Troubleshooting guide
│   ├── CLEANUP_GUIDE.md                 File cleanup instructions
│   └── PROJECT_ARCHITECTURE_UPDATED.md  Full architecture diagram
│
├── 🔧 Main Files
│   ├── app.py                           Main Streamlit application
│   ├── test_chatbot.py                  Chatbot test suite
│   └── verify_setup.py                  Setup verification script
```

---

## 🎯 Dashboard Features

| Tab | Description | Key Features |
|-----|-------------|--------------|
| 📈 **Trends** | Registration patterns over time | Yearly/monthly analysis, EV type distribution |
| 🏭 **Manufacturers** | Top makes and models | Market share, brand comparison, top 15 models |
| 🗺️ **Geographic** | Map and location analysis | Interactive maps, state/county stats, debugging tools |
| ⚡ **Performance** | Electric range analysis | Range distribution, BEV vs PHEV, CAFV eligibility |
| 📋 **Data Table** | Browse all vehicles | Searchable, paginated, CSV export |
| 🤖 **AI Analyst** | Natural language queries | SQL auto-generation, conversational responses |
| 🔮 **Prediction** | ML range predictions | Random Forest model, feature importance |
| 📊 **Forecast** | Future adoption trends | Polynomial regression, customizable horizon |

---

## 🤖 AI Analyst - Intelligent Chatbot

### Key Features

✅ **Three Query Types:**
- **General** - EV knowledge (e.g., "What is regenerative braking?")
- **Data Query** - SQL generation (e.g., "How many Teslas?")
- **Hybrid** - Both combined (e.g., "What is CAFV and how many qualify?")

✅ **Transparent:**
- Shows SQL queries generated
- Displays raw data results
- Explains query classification

✅ **Fast & Free:**
- Sub-3-second responses
- Uses Groq AI (Llama 3.3 70B)
- Free API (no costs)

### Example Questions

```
💡 General Knowledge:
"What is an electric vehicle?"
"How does regenerative braking work?"
"What's the difference between BEV and PHEV?"

📊 Database Queries:
"How many vehicles are in the database?"
"What are the top 5 manufacturers?"
"Show me the average electric range by year"

🔍 Hybrid Questions:
"What is CAFV eligibility and how many vehicles qualify?"
"Explain range anxiety and show me typical EV ranges"
"Compare Tesla and Nissan - which is more popular?"
```

### How It Works

```
User Question
     ↓
┌─────────────────┐
│ Step 1: Classify│  → Determine: general/data/hybrid
└────────┬────────┘
         ↓
┌─────────────────┐
│ Step 2: Process │  → Get info from AI or database
└────────┬────────┘
         ↓
┌─────────────────┐
│ Step 3: Generate│  → Create natural answer
└─────────────────┘
```

---

## 🔄 Data Flow Architecture

```
┌─────────────┐
│ PostgreSQL  │
│  Database   │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ data_loader.py   │  ← SQL queries (cached with TTL)
└──────┬───────────┘
       │
       ▼
┌──────────────────┐
│    app.py        │  ← Main orchestrator
└──────┬───────────┘
       │
       ├─→ config/         (Streamlit setup)
       ├─→ utils/          (Data & ML helpers)
       └─→ components/     (UI components)
           │
           ├─→ sidebar.py  (Filters & navigation)
           ├─→ metrics.py  (Dashboard KPIs)
           └─→ tabs/       (8 analytics modules)
```

---

## 🎨 Application Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      app.py                             │
│              Main Streamlit Application                 │
└──────────────────┬──────────────────────────────────────┘
                   │
      ┌────────────┼────────────┐
      │            │            │
      ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│  config/ │ │  utils/  │ │components│
└──────────┘ └──────────┘ └──────────┘
      │            │            │
      │            │            ├─→ sidebar.py
      │            │            ├─→ metrics.py
      │            │            └─→ tabs/
      │            │                  ├─→ trends.py
      │            │                  ├─→ manufacturers.py
      │            │                  ├─→ geographic.py
      │            │                  ├─→ performance.py
      │            │                  ├─→ data_table.py
      │            │                  ├─→ ai_analyst.py
      │            │                  ├─→ prediction.py
      │            │                  └─→ forecast.py
      │            │
      │            ├─→ database.py (Connection)
      │            ├─→ data_loader.py (SQL queries)
      │            ├─→ ml_models.py (ML training)
      │            └─→ map_debug.py (Map helpers)
      │
      └─→ page_config.py (Streamlit styling)
```

---

## 🛠️ Adding a New Tab

### Step 1: Create Tab File

Create `components/tabs/my_feature.py`:

```python
import streamlit as st

def render_my_feature_tab(filtered_df):
    """Render my new feature tab"""
    st.subheader("🎯 My New Feature")
    
    # Your analysis code here
    st.write(f"Analyzing {len(filtered_df)} vehicles...")
    
    # Example chart
    import plotly.express as px
    fig = px.bar(filtered_df.head(10), x='make', y='electric_range')
    st.plotly_chart(fig, use_container_width=True)
```

### Step 2: Import in app.py

Add to imports section:

```python
from components.tabs.my_feature import render_my_feature_tab
```

### Step 3: Add Tab to UI

Find the tabs definition and add:

```python
tabs = st.tabs([
    "📈 Trends",
    "🏭 Manufacturers", 
    "🗺️ Geographic",
    "⚡ Performance",
    "📋 Data Table",
    "🤖 AI Analyst",
    "🔮 Prediction",
    "📊 Forecast",
    "🎯 My Feature"  # ← Add your tab
])

# Then add the render call
with tabs[8]:  # Adjust index
    render_my_feature_tab(filtered_df)
```

### Step 4: Test

```bash
streamlit run app.py
```

---

## 📝 Key Files Explained

### Core Files

| File | Purpose | Key Functions |
|------|---------|---------------|
| `app.py` | Main entry point | Loads all components, manages state |
| `config/page_config.py` | Streamlit setup | Page title, icon, layout |
| `utils/database.py` | DB connection | `get_connection()` |
| `utils/data_loader.py` | Data queries | All SQL queries with caching |
| `utils/ml_models.py` | ML operations | Training, prediction, evaluation |

### UI Components

| File | Purpose | Renders |
|------|---------|---------|
| `components/sidebar.py` | Navigation & filters | State, make, year, EV type filters |
| `components/metrics.py` | Dashboard stats | Total vehicles, makes, models, avg range |
| `components/tabs/*.py` | Analytics modules | Individual feature tabs |

### AI Components

| File | Purpose | Key Features |
|------|---------|--------------|
| `chatbot/intelligent_chatbot.py` | AI chatbot | Question classification, SQL generation, Groq AI |

---

## 🔧 Configuration

### Required Environment Variables

Create `.env` file in **project root** (not in visualization/):

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=ev_db
DB_USER=your_username
DB_PASSWORD=your_password

# AI Configuration
GROQ_API_KEY=your_groq_api_key_here

# Optional
API_URL=https://data.wa.gov/resource/f6w7-q2d2.csv
```

## 🧪 Testing

### Test Chatbot

```bash
python test_chatbot.py
```

Tests 9 different question types:
- 3 general questions
- 3 database queries
- 3 hybrid questions

### Verify Setup

```bash
python verify_setup.py
```

Checks:
- File structure
- Database connection
- Required packages
- Environment variables
