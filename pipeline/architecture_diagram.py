import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(1, 1, figsize=(16, 10))
ax.set_xlim(0, 16)
ax.set_ylim(0, 10)
ax.axis("off")
ax.set_facecolor("#0e1117")
fig.patch.set_facecolor("#0e1117")

def box(ax, x, y, w, h, label, sublabel="", color="#1a1f2e", border="#00d4ff"):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2+(0.15 if sublabel else 0), label,
            ha="center", va="center", color="white",
            fontsize=9, fontweight="bold", fontfamily="monospace")
    if sublabel:
        ax.text(x+w/2, y+h/2-0.2, sublabel,
                ha="center", va="center", color="#7a8499",
                fontsize=7, fontfamily="monospace")

def arrow(ax, x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color="#00d4ff", lw=1.5))

def layer_label(ax, x, y, text):
    ax.text(x, y, text, color="#00d4ff", fontsize=8,
            fontweight="bold", fontfamily="monospace",
            rotation=90, va="center", ha="center")

# Layer labels
layer_label(ax, 0.3, 7.5, "SOURCE")
layer_label(ax, 0.3, 5.5, "BRONZE")
layer_label(ax, 0.3, 3.5, "SILVER")
layer_label(ax, 0.3, 1.8, "GOLD")

# Title
ax.text(8, 9.5, "Bangkok Airbnb Market Intelligence — Data Architecture",
        ha="center", va="center", color="white",
        fontsize=13, fontweight="bold", fontfamily="monospace")

# SOURCE layer
box(ax, 1, 7, 3, 1, "Inside Airbnb", "insideairbnb.com", border="#ff6b6b")
box(ax, 5, 7, 2.5, 1, "listings.csv", "28,806 rows", border="#ff6b6b")
box(ax, 8, 7, 2.5, 1, "calendar.csv", "10.5M rows", border="#ff6b6b")
box(ax, 11, 7, 2.5, 1, "reviews.csv", "583K rows", border="#ff6b6b")

# SOURCE arrows
for x in [5, 8, 11]:
    arrow(ax, 4, 7.5, x, 8)

# BRONZE layer
box(ax, 1, 5, 3, 1, "ingest.py", "retry + metadata", border="#f59e0b")
box(ax, 5, 5, 2.5, 1, "raw/listings", ".csv.gz", border="#f59e0b")
box(ax, 8, 5, 2.5, 1, "raw/calendar", ".csv.gz", border="#f59e0b")
box(ax, 11, 5, 2.5, 1, "raw/reviews", ".csv.gz", border="#f59e0b")

# SOURCE → BRONZE
for x in [5, 8, 11]:
    arrow(ax, x+1.25, 7, x+1.25, 6)
arrow(ax, 2.5, 7, 2.5, 6)

# SILVER layer
box(ax, 1, 3, 3, 1, "clean.py", "standardize + validate", border="#4ade80")
box(ax, 5, 3, 2.5, 1, "listings_clean", ".csv", border="#4ade80")
box(ax, 8, 3, 2.5, 1, "calendar_clean", ".csv", border="#4ade80")
box(ax, 11, 3, 2.5, 1, "reviews_clean", ".csv", border="#4ade80")

# BRONZE → SILVER
for x in [5, 8, 11]:
    arrow(ax, x+1.25, 5, x+1.25, 4)
arrow(ax, 2.5, 5, 2.5, 4)

# GOLD layer
box(ax, 1, 1, 3, 1, "enrich.py", "join + derive + model", border="#a78bfa")
box(ax, 4.5, 1, 2, 1, "listings\nenriched", border="#a78bfa")
box(ax, 7, 1, 2, 1, "fact\nlistings", border="#a78bfa")
box(ax, 9.5, 1, 1.5, 1, "dim_host", border="#a78bfa")
box(ax, 11.5, 1, 1.5, 1, "dim_location", border="#a78bfa")
box(ax, 13.5, 1, 1.5, 1, "dim_property", border="#a78bfa")

# SILVER → GOLD
for x in [5, 8, 11]:
    arrow(ax, x+1.25, 3, x+1.25, 2)
arrow(ax, 2.5, 3, 2.5, 2)

# GOLD → outputs
box(ax, 4.5, -0.5, 2, 0.8, "EDA Notebook", "", color="#0e1117", border="#00d4ff")
box(ax, 7, -0.5, 2, 0.8, "Hypothesis\nTesting", color="#0e1117", border="#00d4ff")
box(ax, 9.5, -0.5, 2, 0.8, "Dashboard", "", color="#0e1117", border="#00d4ff")
box(ax, 12, -0.5, 2, 0.8, "PDF Report", "", color="#0e1117", border="#00d4ff")

for x in [5.5, 8, 10.5, 13]:
    arrow(ax, x, 1, x, 0.3)

plt.tight_layout()
plt.savefig("report/architecture_diagram.png", dpi=150,
            bbox_inches="tight", facecolor="#0e1117")
plt.show()
print("Saved to report/architecture_diagram.png")