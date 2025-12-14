# DATAVIZ_ASSIGNMENT3 — Global Development Explorer

This repository contains an interactive data visualization dashboard built using the Gapminder dataset.  
The project focuses on exploring global development indicators using a coordinated multi-view design.

---

## Folder Structure
DATAVIZ_ASSIGNMENT3/
├── a3_ritik.py # Main Dash application
├── dataset.ipynb # Notebook used for initial data exploration
├── gapminder.csv # Gapminder dataset (loaded locally)
├── requirements.txt # Python dependencies
└── readme.md # Project documentation


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

1. The dashboard enables exploration of relationships between:
2. GDP per capita
3. Life expectancy
4. Population
5. Geographic location

A coordinated multi-view layout is used, where interaction in one view (such as lasso selection in the scatter plot) updates all other views consistently.