import pandas as pd
import json
import os
from datetime import datetime

RAW_DIR = "data/raw/Bangkok/data"
OUTPUT = "data/processed/profiling_report.json"
os.makedirs("data/processed", exist_ok=True)

def profile_df(name, df):
    report = {
        "file": name,
        "rows": len(df),
        "columns": len(df.columns),
        "fields": {}
    }
    for col in df.columns:
        s = df[col]
        info = {
            "dtype": str(s.dtype),
            "null_count": int(s.isna().sum()),
            "null_pct": round(s.isna().mean() * 100, 2),
            "unique": int(s.nunique()),
        }
        if s.dtype in ["float64", "int64"]:
            info["min"] = float(s.min()) if not s.isna().all() else None
            info["max"] = float(s.max()) if not s.isna().all() else None
            info["mean"] = round(float(s.mean()), 2) if not s.isna().all() else None
        else:
            info["sample_values"] = s.dropna().astype(str).unique()[:5].tolist()
        report["fields"][col] = info
    return report

def run():
    files = {
        "listings": os.path.join(RAW_DIR, "listings.csv"),
        "calendar": os.path.join(RAW_DIR, "calendar.csv"),
        "reviews": os.path.join(RAW_DIR, "reviews.csv"),
        "neighbourhoods": os.path.join(RAW_DIR, "visualisations", "neighbourhoods.csv"),
    }

    full_report = {"profiled_at": datetime.now().isoformat(), "datasets": {}}

    for name, path in files.items():
        if not os.path.exists(path):
            print(f"SKIP {name} — file not found")
            continue
        print(f"Profiling {name}...")
        df = pd.read_csv(path, low_memory=False)
        full_report["datasets"][name] = profile_df(name, df)
        print(f"  {len(df)} rows, {len(df.columns)} cols")

    with open(OUTPUT, "w") as f:
        json.dump(full_report, f, indent=2)
    print(f"\nReport saved to {OUTPUT}")

if __name__ == "__main__":
    run()