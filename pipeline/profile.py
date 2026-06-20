import pandas as pd
import json
import os
import json
from datetime import datetime
from difflib import SequenceMatcher


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

# --- Fuzzy Duplicate Detection ---


def fuzzy_duplicates(df, col="name", threshold=0.95, sample_size=500):
    """Detect near-duplicate listings by name similarity"""
    sample = df[col].dropna().astype(str).head(sample_size).tolist()
    duplicates = []
    for i in range(len(sample)):
        for j in range(i+1, len(sample)):
            ratio = SequenceMatcher(None, sample[i], sample[j]).ratio()
            if ratio >= threshold:
                duplicates.append({
                    "name_1": sample[i],
                    "name_2": sample[j],
                    "similarity": round(ratio, 4)
                })
    return pd.DataFrame(duplicates)

print("\nRunning fuzzy duplicate detection on listings...")
listings_df = pd.read_csv(os.path.join("data/raw/Bangkok/data", "listings.csv"), 
                          low_memory=False)

# Deterministic duplicates
det_dupes = listings_df.duplicated(subset=["id"]).sum()
print(f"Deterministic duplicates (by ID): {det_dupes}")

# Fuzzy duplicates by name
fuzzy_df = fuzzy_duplicates(listings_df, col="name", threshold=0.95)
print(f"Fuzzy near-duplicates (name similarity ≥ 95%): {len(fuzzy_df)}")
if len(fuzzy_df) > 0:
    print(fuzzy_df.head(5).to_string())

# Fuzzy duplicates by coordinates
coord_dupes = listings_df.groupby(["latitude","longitude"]).size()
coord_dupes = coord_dupes[coord_dupes > 1]
print(f"Listings sharing exact coordinates: {len(coord_dupes)} coordinate pairs")
print(f"Total listings in coordinate duplicates: {coord_dupes.sum()}")

# Save fuzzy report
fuzzy_report = {
    "deterministic_duplicates": int(det_dupes),
    "fuzzy_name_duplicates": len(fuzzy_df),
    "coordinate_duplicate_pairs": int(len(coord_dupes)),
    "sample_fuzzy_matches": fuzzy_df.head(10).to_dict("records")
}

with open("data/processed/duplicate_report.json", "w") as f:
    json.dump(fuzzy_report, f, indent=2)
print("Duplicate report saved.")

if __name__ == "__main__":
    run()