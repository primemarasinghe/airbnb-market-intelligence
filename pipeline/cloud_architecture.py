import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch
import matplotlib.patheffects as pe

fig, ax = plt.subplots(1, 1, figsize=(18, 12))
ax.set_xlim(0, 18)
ax.set_ylim(0, 12)
ax.axis("off")
ax.set_facecolor("#0e1117")
fig.patch.set_facecolor("#0e1117")

def box(ax, x, y, w, h, label, sublabel="", color="#1a1f2e", border="#00d4ff", fontsize=8):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor=border, linewidth=1.5)
    ax.add_patch(rect)
    ax.text(x+w/2, y+h/2+(0.12 if sublabel else 0), label,
            ha="center", va="center", color="white",
            fontsize=fontsize, fontweight="bold", fontfamily="monospace")
    if sublabel:
        ax.text(x+w/2, y+h/2-0.2, sublabel,
                ha="center", va="center", color="#7a8499",
                fontsize=6, fontfamily="monospace")

def arrow(ax, x1, y1, x2, y2, color="#00d4ff"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=1.5))

def layer_bg(ax, x, y, w, h, label, color):
    rect = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor="none", alpha=0.15)
    ax.add_patch(rect)
    ax.text(x+0.2, y+h-0.2, label, color=color, fontsize=7,
            fontweight="bold", fontfamily="monospace", va="top")

# Title
ax.text(9, 11.5, "Bangkok Airbnb Intelligence — Cloud-Native Architecture (AWS)",
        ha="center", va="center", color="white",
        fontsize=13, fontweight="bold", fontfamily="monospace")

# Layer backgrounds
layer_bg(ax, 0.3, 9.5, 17.4, 1.7, "INGESTION LAYER", "#ff6b6b")
layer_bg(ax, 0.3, 7.2, 17.4, 2.0, "STORAGE LAYER (S3)", "#f59e0b")
layer_bg(ax, 0.3, 4.8, 17.4, 2.1, "PROCESSING LAYER", "#4ade80")
layer_bg(ax, 0.3, 2.5, 17.4, 2.0, "SERVING LAYER", "#00d4ff")
layer_bg(ax, 0.3, 0.3, 17.4, 1.9, "MONITORING & ORCHESTRATION", "#a78bfa")

# INGESTION
box(ax, 0.5, 9.8, 2.5, 1.0, "Inside Airbnb", "Weekly Scrape", border="#ff6b6b")
box(ax, 3.5, 9.8, 2.5, 1.0, "AWS Lambda", "Trigger Function", border="#ff6b6b")
box(ax, 6.5, 9.8, 2.5, 1.0, "API Gateway", "REST Endpoint", border="#ff6b6b")
box(ax, 9.5, 9.8, 2.5, 1.0, "SQS Queue", "Job Queue", border="#ff6b6b")
box(ax, 12.5, 9.8, 2.5, 1.0, "ECR", "Docker Images", border="#ff6b6b")
box(ax, 15.2, 9.8, 2.3, 1.0, "ECS Fargate", "Pipeline Runner", border="#ff6b6b")

arrow(ax, 3.0, 10.3, 3.5, 10.3)
arrow(ax, 6.0, 10.3, 6.5, 10.3)
arrow(ax, 9.0, 10.3, 9.5, 10.3)
arrow(ax, 12.0, 10.3, 12.5, 10.3)
arrow(ax, 15.0, 10.3, 15.2, 10.3)

# STORAGE
box(ax, 0.5, 7.5, 2.5, 1.2, "S3 Bronze", "Raw CSV/GZ", border="#f59e0b")
box(ax, 3.5, 7.5, 2.5, 1.2, "S3 Silver", "Cleaned CSV", border="#f59e0b")
box(ax, 6.5, 7.5, 2.5, 1.2, "S3 Gold", "Enriched/Star", border="#f59e0b")
box(ax, 9.5, 7.5, 2.5, 1.2, "AWS Glue", "Data Catalog", border="#f59e0b")
box(ax, 12.5, 7.5, 2.5, 1.2, "DynamoDB", "Metadata Store", border="#f59e0b")
box(ax, 15.2, 7.5, 2.3, 1.2, "Glacier", "Archive/Backup", border="#f59e0b")

arrow(ax, 3.0, 8.1, 3.5, 8.1)
arrow(ax, 6.0, 8.1, 6.5, 8.1)
arrow(ax, 9.0, 8.1, 9.5, 8.1)
arrow(ax, 12.0, 8.1, 12.5, 8.1)

# PROCESSING
box(ax, 0.5, 5.1, 2.5, 1.2, "AWS Glue ETL", "PySpark Jobs", border="#4ade80")
box(ax, 3.5, 5.1, 2.5, 1.2, "Amazon Athena", "SQL Queries", border="#4ade80")
box(ax, 6.5, 5.1, 2.5, 1.2, "SageMaker", "ML Training", border="#4ade80")
box(ax, 9.5, 5.1, 2.5, 1.2, "Lambda NLP", "Sentiment/RAG", border="#4ade80")
box(ax, 12.5, 5.1, 2.5, 1.2, "ElastiCache", "Redis Cache", border="#4ade80")
box(ax, 15.2, 5.1, 2.3, 1.2, "Step Functions", "Orchestration", border="#4ade80")

arrow(ax, 3.0, 5.7, 3.5, 5.7)
arrow(ax, 6.0, 5.7, 6.5, 5.7)
arrow(ax, 9.0, 5.7, 9.5, 5.7)
arrow(ax, 12.0, 5.7, 12.5, 5.7)

# SERVING
box(ax, 0.5, 2.8, 2.5, 1.2, "QuickSight", "BI Dashboard", border="#00d4ff")
box(ax, 3.5, 2.8, 2.5, 1.2, "API Gateway", "REST API", border="#00d4ff")
box(ax, 6.5, 2.8, 2.5, 1.2, "CloudFront", "CDN/Static", border="#00d4ff")
box(ax, 9.5, 2.8, 2.5, 1.2, "Cognito", "Auth/Users", border="#00d4ff")
box(ax, 12.5, 2.8, 2.5, 1.2, "SageMaker", "Model Endpoint", border="#00d4ff")
box(ax, 15.2, 2.8, 2.3, 1.2, "Bedrock", "LLM/RAG API", border="#00d4ff")

# MONITORING
box(ax, 0.5, 0.5, 2.5, 1.2, "CloudWatch", "Logs/Metrics", border="#a78bfa")
box(ax, 3.5, 0.5, 2.5, 1.2, "EventBridge", "Scheduling", border="#a78bfa")
box(ax, 6.5, 0.5, 2.5, 1.2, "SNS/SES", "Alerting/Email", border="#a78bfa")
box(ax, 9.5, 0.5, 2.5, 1.2, "Cost Explorer", "Cost Monitor", border="#a78bfa")
box(ax, 12.5, 0.5, 2.5, 1.2, "IAM", "Security/Roles", border="#a78bfa")
box(ax, 15.2, 0.5, 2.3, 1.2, "AWS Config", "Compliance", border="#a78bfa")

plt.tight_layout()
plt.savefig("report/cloud_architecture.png", dpi=150,
            bbox_inches="tight", facecolor="#0e1117")
plt.show()
print("Cloud architecture saved.")