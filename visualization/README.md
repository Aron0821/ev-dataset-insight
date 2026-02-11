# EV Dashboard - Modular Structure

## 🚀 Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run dashboard 1
streamlit run app.py

# Run dashboard 2
cd visualization 
python main.py
```

## 📁 Structure

```
visualization/
├── 📁 chatbot/
│   └── intelligent_chatbot.py
│   ├── retriever.py
│   └── vector_store.py
├── 📁 components/
│   ├── 📁 tabs/
│   │   ├── __init__.py
│   │   ├── ai_analyst.py
│   │   ├── data_table.py
│   │   ├── forecast.py
│   │   ├── geographic.py
│   │   ├── manufacturers.py
│   │   ├── performance.py
│   │   ├── prediction.py
│   │   └── trends.py
│   ├── __init__.py
│   ├── metrics.py
│   └── sidebar.py
├── 📁 config/
│   ├── __init__.py
│   └── page_config.py
├── 📁 utils/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── database.py
│   ├── map_debug.py
│   └── ml_models.py
├── README.md
├── app.py
├── main.py
├── test_chatbot.py
├── text_to_sql.py
├── vector_db.py
└── verify_setup.py
```

## 🎯 Features

| Tab | Description |
|-----|-------------|
| 📈 Trends | Registration trends over time |
| 🏭 Manufacturers | Top makes and models |
| 🗺️ Geographic | Map and location stats |
| ⚡ Performance | Range analysis |
| 📋 Data Table | Browse all vehicles |
| 🤖 AI Analyst | Ask questions about data |
| 🔮 Prediction | ML range predictions |
| 📊 Forecast | Future adoption trends |

## 🔄 Data Flow

```
Database → data_loader.py → app.py → Tabs
                ↓
           (cached with TTL)
```

## 🎨 Architecture

```
┌──────────────┐
│   app.py     │  ← Main orchestrator
└──────┬───────┘
       │
       ├─→ config/         (setup)
       ├─→ utils/          (data & ML)
       └─→ components/     (UI)
           │
           ├─→ sidebar.py  (filters)
           ├─→ metrics.py  (stats)
           └─→ tabs/       (8 tabs)
```

## 🛠️ Adding a New Tab

1. **Create file**: `components/tabs/my_tab.py`
```python
import streamlit as st

def render_my_tab(filtered_df):
    st.subheader("My Feature")
    # Your code here
```

2. **Import in app.py**:
```python
from components.tabs.my_tab import render_my_tab
```

3. **Add to tabs**:
```python
with tab9:
    render_my_tab(filtered_df)
```

## 📝 Key Files

- `app.py` - Main application (loads everything)
- `utils/data_loader.py` - All SQL queries
- `utils/ml_models.py` - ML training/prediction
- `components/tabs/*.py` - Individual features
