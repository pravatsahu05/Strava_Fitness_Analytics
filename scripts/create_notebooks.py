"""
Script to create the 4 required EDA Jupyter Notebooks.
"""

import json
from pathlib import Path

nb_dir = Path("notebooks")
nb_dir.mkdir(parents=True, exist_ok=True)

def make_nb(cells_data):
    cells = []
    for ctype, src in cells_data:
        cells.append({
            'cell_type': ctype,
            'metadata': {},
            'outputs': [],
            'execution_count': None,
            'source': [line + '\n' for line in src.split('\n')]
        })
    return {
        'cells': cells,
        'metadata': {
            'language_info': {'name': 'python'}
        },
        'nbformat': 4,
        'nbformat_minor': 2
    }

nb1 = make_nb([
    ('markdown', '# Notebook 01: Data Understanding & Inspection\n\nThis notebook inspects raw Fitabase CSV datasets, column names, dataset shapes, and primary key grains.'),
    ('code', 'import pandas as pd\nimport glob, os\n\nraw_files = sorted(glob.glob("../data/raw/fitabase.zip/Fitabase Data 4.12.16-5.12.16/*.csv"))\nprint(f"Found {len(raw_files)} raw CSV files:")\nfor f in raw_files:\n    df = pd.read_csv(f, nrows=5)\n    print(f"- {os.path.basename(f)}: {len(df.columns)} columns")'),
    ('code', 'df_act = pd.read_csv(raw_files[0])\nprint("Daily Activity Info:")\nprint(df_act.info())\nprint(df_act.head())')
])

nb2 = make_nb([
    ('markdown', '# Notebook 02: Data Cleaning & Deduplication\n\nApplies standardized column naming, date formatting, deduplication, and quality reporting.'),
    ('code', 'import sys, os\nsys.path.insert(0, "..")\nfrom src.etl.data_cleaning import run_data_cleaning_pipeline\n\ndf_rep, df_summ = run_data_cleaning_pipeline()\nprint(df_rep)\nprint("\\nSummary:")\nprint(df_summ)')
])

nb3 = make_nb([
    ('markdown', '# Notebook 03: Exploratory Data Analysis (EDA)\n\nUnivariate distributions, bivariate step vs calorie relationships, weekday activity behavior, and sleep patterns.'),
    ('code', 'import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\n\ndf = pd.read_csv("../data/processed/daily_master.csv")\nprint(f"Loaded daily_master with {len(df)} rows")\nprint(df.describe())'),
    ('code', 'plt.figure(figsize=(10, 5))\nsns.histplot(df[df["total_steps"] > 0]["total_steps"], kde=True, color="teal")\nplt.title("Distribution of Daily Steps")\nplt.xlabel("Daily Steps")\nplt.show()'),
    ('code', 'plt.figure(figsize=(8, 5))\nsns.scatterplot(data=df[df["total_steps"] > 0], x="total_steps", y="calories", alpha=0.7, color="royalblue")\nplt.title("Daily Steps vs Calories Burned")\nplt.xlabel("Total Steps")\nplt.ylabel("Calories (kcal)")\nplt.show()')
])

nb4 = make_nb([
    ('markdown', '# Notebook 04: Business Insights & Recommendations\n\nExtracts factual dynamic insights and formulates strategy recommendations for Bellabeat marketing leadership.'),
    ('code', 'import sys\nsys.path.insert(0, "..")\nimport pandas as pd\nfrom src.analytics.insights import generate_dynamic_business_insights\n\ndf_daily = pd.read_csv("../data/processed/daily_master.csv")\ndf_hourly = pd.read_csv("../data/processed/hourly_master.csv")\ninsights = generate_dynamic_business_insights(df_daily, df_hourly)\n\nprint("--- DYNAMIC BUSINESS INSIGHTS ---")\nfor k, v in insights.items():\n    if k.startswith("insight_"):\n        print(f"• {v}")')
])

for name, nb in [('01_data_understanding.ipynb', nb1), ('02_data_cleaning.ipynb', nb2), ('03_eda.ipynb', nb3), ('04_insights.ipynb', nb4)]:
    with open(nb_dir / name, 'w', encoding='utf-8') as f:
        json.dump(nb, f, indent=2)

print("All 4 Jupyter Notebooks generated successfully in notebooks/")
