
---

## How to Run (Step-by-Step)

### 1. Open a terminal in the project folder
Navigate to the directory that contains `a3_ritik.py`.

You should see:
- `a3_ritik.py`
- `gapminder.csv`
- `requirements.txt`

---

### 2. Create and activate a virtual environment (recommended)

**macOS / Linux**
```bash
python3 -m venv venv
source venv/bin/activate

**Windows (PowerShell)**
python -m venv venv
venv\Scripts\Activate.ps1

### 3. Install required dependencies
pip install -r requirements.txt

### 4. Run the dashboard application
python a3_ritik.py

### 5. Open the dashboard in your browser
http://127.0.0.1:8060/


Dashboard Overview

The dashboard enables exploration of relationships between:

1. GDP per capita
2. Life expectancy
3. Population
4. Geographic location
5. A coordinated multi-view layout ensures that interactions in one view update all others consistently.