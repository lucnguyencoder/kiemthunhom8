import pandas as pd
import numpy as np
from pathlib import Path

CSV_PATH = Path("results.csv")

def analyze_results():
    if not CSV_PATH.exists():
        print(f"❌ File not found: {CSV_PATH}")
        return
    
    # Đọc dữ liệu
    df = pd.read_csv(CSV_PATH)
    
    if len(df) == 0:
        print("❌ CSV file is empty")
        return
    
    latencies = df['latency_ms'].values
    
    # Tính toán thống kê
    total_msgs = len(df)
    total_clients = df['connection_id'].nunique()
    
    min_lat = latencies.min()
    max_lat = latencies.max()
    mean_lat = latencies.mean()
    median_lat = np.median(latencies)
    p95_lat = np.percentile(latencies, 95)
    p99_lat = np.percentile(latencies, 99)
    stdev_lat = latencies.std()
    
    # In kết quả
    print("\n" + "="*60)
    print("📊 PERFORMANCE TEST STATISTICS")
    print("="*60)
    print(f"Total messages      : {total_msgs:,}")
    print(f"Unique clients      : {total_clients:,}")
    print(f"Avg msgs/client     : {total_msgs/total_clients:.2f}")
    print("-"*60)
    print("⏱️  LATENCY METRICS (milliseconds)")
    print("-"*60)
    print(f"Min                 : {min_lat:>10.3f} ms")
    print(f"Max                 : {max_lat:>10.3f} ms")
    print(f"Mean                : {mean_lat:>10.3f} ms")
    print(f"Median              : {median_lat:>10.3f} ms")
    print(f"Std Dev             : {stdev_lat:>10.3f} ms")
    print(f"P95                 : {p95_lat:>10.3f} ms")
    print(f"P99                 : {p99_lat:>10.3f} ms")
    print("="*60)
    
    # Đánh giá chất lượng
    print("\n✅ EVALUATION:")
    if mean_lat < 300:
        print("   ✓ Mean latency is GOOD (< 300ms)")
    elif mean_lat < 500:
        print("   ⚠ Mean latency is OK (300-500ms)")
    else:
        print("   ✗ Mean latency is POOR (> 500ms)")
    
    if p99_lat < 500:
        print("   ✓ P99 latency is GOOD (< 500ms)")
    elif p99_lat < 1000:
        print("   ⚠ P99 latency is OK (500-1000ms)")
    else:
        print("   ✗ P99 latency is POOR (> 1000ms)")
    
    if (max_lat - min_lat) < 500:
        print("   ✓ Latency distribution is CONSISTENT")
    else:
        print("   ⚠ Latency has high variance")
    
    print("="*60 + "\n")

if __name__ == "__main__":
    analyze_results()
