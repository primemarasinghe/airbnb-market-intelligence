"""
Real-Time Price Monitoring & Alerting Simulation
Using streaming architecture concepts (Kafka-style simulation)
"""

import time
import random
import json
import pandas as pd
import numpy as np
from datetime import datetime
from collections import deque
import threading

# Load market data
df = pd.read_csv("data/processed/listings_enriched.csv", low_memory=False)
df = df[df["price"].between(100, 10000)].copy()

# Neighbourhood baselines
nb_baselines = df.groupby("neighbourhood_cleansed")["price"].median().to_dict()

# --- Simulate Kafka Producer ---
class PriceEventProducer:
    """Simulates real-time price update events from Airbnb listings"""
    
    def __init__(self, listings_df):
        self.listings = listings_df.sample(100, random_state=42).reset_index(drop=True)
    
    def generate_event(self):
        listing = self.listings.sample(1).iloc[0]
        # Simulate price fluctuation ±30%
        base_price = listing["price"]
        fluctuation = random.uniform(0.7, 1.3)
        new_price = round(base_price * fluctuation, 2)
        
        return {
            "event_id": f"EVT_{random.randint(10000, 99999)}",
            "timestamp": datetime.now().isoformat(),
            "listing_id": int(listing["id"]),
            "neighbourhood": listing["neighbourhood_cleansed"],
            "room_type": listing["room_type"],
            "old_price": base_price,
            "new_price": new_price,
            "price_change_pct": round((new_price - base_price) / base_price * 100, 2)
        }


# --- Simulate Kafka Consumer + Stream Processor ---
class StreamProcessor:
    """Processes price events in real-time with windowed aggregations"""
    
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.event_buffer = deque(maxlen=window_size)
        self.alerts = []
        self.stats = {
            "events_processed": 0,
            "alerts_fired": 0,
            "avg_price_change": 0
        }
    
    def process_event(self, event):
        self.event_buffer.append(event)
        self.stats["events_processed"] += 1
        
        # Update rolling avg
        changes = [e["price_change_pct"] for e in self.event_buffer]
        self.stats["avg_price_change"] = round(np.mean(changes), 2)
        
        # Alert rules
        alerts = self.check_alerts(event)
        self.alerts.extend(alerts)
        self.stats["alerts_fired"] += len(alerts)
        
        return alerts
    
    def check_alerts(self, event):
        alerts = []
        nb = event["neighbourhood"]
        baseline = nb_baselines.get(nb, event["old_price"])
        
        # Rule 1: Sudden price spike >50%
        if event["price_change_pct"] > 50:
            alerts.append({
                "type": "PRICE_SPIKE",
                "severity": "HIGH",
                "message": f"Listing {event['listing_id']} in {nb} spiked +{event['price_change_pct']:.1f}% to ฿{event['new_price']:,.0f}",
                "timestamp": event["timestamp"]
            })
        
        # Rule 2: Price drop >40%
        elif event["price_change_pct"] < -40:
            alerts.append({
                "type": "PRICE_DROP",
                "severity": "MEDIUM",
                "message": f"Listing {event['listing_id']} in {nb} dropped {event['price_change_pct']:.1f}% to ฿{event['new_price']:,.0f}",
                "timestamp": event["timestamp"]
            })
        
        # Rule 3: Price 3x above neighbourhood median
        if event["new_price"] > baseline * 3:
            alerts.append({
                "type": "ABOVE_MARKET",
                "severity": "LOW",
                "message": f"Listing {event['listing_id']} priced ฿{event['new_price']:,.0f} — {event['new_price']/baseline:.1f}x above {nb} median (฿{baseline:,.0f})",
                "timestamp": event["timestamp"]
            })
        
        # Rule 4: Neighbourhood avg rising (windowed)
        nb_events = [e for e in self.event_buffer if e["neighbourhood"] == nb]
        if len(nb_events) >= 3:
            avg_change = np.mean([e["price_change_pct"] for e in nb_events])
            if avg_change > 20:
                alerts.append({
                    "type": "NEIGHBOURHOOD_TREND",
                    "severity": "INFO",
                    "message": f"{nb} showing sustained price increase: avg +{avg_change:.1f}% over last {len(nb_events)} events",
                    "timestamp": event["timestamp"]
                })
        
        return alerts
    
    def get_window_stats(self):
        if not self.event_buffer:
            return {}
        
        prices = [e["new_price"] for e in self.event_buffer]
        changes = [e["price_change_pct"] for e in self.event_buffer]
        
        return {
            "window_size": len(self.event_buffer),
            "avg_price": round(np.mean(prices), 2),
            "avg_change_pct": round(np.mean(changes), 2),
            "max_spike": round(max(changes), 2),
            "max_drop": round(min(changes), 2),
            "events_processed": self.stats["events_processed"],
            "alerts_fired": self.stats["alerts_fired"]
        }


def run_simulation(n_events=50, delay=0.1):
    """Run the stream processing simulation"""
    
    print("="*65)
    print("BANGKOK AIRBNB — REAL-TIME PRICE MONITORING SIMULATION")
    print("="*65)
    print(f"Simulating {n_events} price update events...")
    print(f"Alert rules: Spike>50%, Drop<-40%, 3x market, Neighbourhood trend")
    print("="*65)
    
    producer = PriceEventProducer(df)
    processor = StreamProcessor(window_size=10)
    
    all_alerts = []
    
    for i in range(n_events):
        event = producer.generate_event()
        alerts = processor.process_event(event)
        
        # Print every 10th event
        if (i + 1) % 10 == 0:
            stats = processor.get_window_stats()
            print(f"\n[Event {i+1}/{n_events}] Window Stats:")
            print(f"  Avg price: ฿{stats['avg_price']:,.0f}")
            print(f"  Avg change: {stats['avg_change_pct']:+.1f}%")
            print(f"  Max spike: {stats['max_spike']:+.1f}%")
            print(f"  Total alerts: {stats['alerts_fired']}")
        
        if alerts:
            for alert in alerts:
                print(f"\n🚨 [{alert['severity']}] {alert['type']}")
                print(f"   {alert['message']}")
            all_alerts.extend(alerts)
        
        time.sleep(delay)
    
    # Final summary
    print("\n" + "="*65)
    print("SIMULATION COMPLETE — FINAL SUMMARY")
    print("="*65)
    final_stats = processor.get_window_stats()
    print(f"Events processed: {final_stats['events_processed']}")
    print(f"Total alerts fired: {final_stats['alerts_fired']}")
    
    alert_types = {}
    for a in all_alerts:
        alert_types[a["type"]] = alert_types.get(a["type"], 0) + 1
    
    print("\nAlerts by type:")
    for atype, count in sorted(alert_types.items()):
        print(f"  {atype}: {count}")
    
    # Save alert log
    with open("data/processed/stream_alerts_log.json", "w") as f:
        json.dump({
            "simulation_run": datetime.now().isoformat(),
            "events_processed": n_events,
            "total_alerts": len(all_alerts),
            "alert_breakdown": alert_types,
            "sample_alerts": all_alerts[:10]
        }, f, indent=2)
    
    print("\nAlert log saved to data/processed/stream_alerts_log.json")
    
    print("""
PRODUCTION ARCHITECTURE NOTE:
==============================
This simulation demonstrates concepts that would be implemented as:

INGESTION:
  Airbnb scraper → Apache Kafka topic (price_updates)
  
PROCESSING:
  Kafka Streams / Apache Flink consumer
  Windowed aggregations (tumbling 5-min, sliding 1-hour)
  Stateful processing for neighbourhood trend detection
  
ALERTING:
  Alert rules engine → SNS/PagerDuty
  Slack notifications for HIGH severity alerts
  Email digest for MEDIUM/LOW alerts
  
STORAGE:
  Raw events → Kafka (7-day retention)
  Processed alerts → DynamoDB
  Aggregated stats → TimescaleDB / InfluxDB
  Dashboards → Grafana real-time panels
  
SCALABILITY:
  Kafka partitioned by neighbourhood (50 partitions)
  Flink parallelism = number of partitions
  Auto-scaling consumer groups
  Handles 10K+ events/second at 50-city scale
""")

if __name__ == "__main__":
    run_simulation(n_events=50, delay=0.05)