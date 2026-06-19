import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import warnings
warnings.filterwarnings("ignore")

# Style
sns.set_theme(style="darkgrid")
plt.rcParams["figure.dpi"] = 120

import os
os.makedirs("notebooks/figures", exist_ok=True)

df = pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)
print(f"Shape: {df.shape}")
print(df["room_type"].value_counts())