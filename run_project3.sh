#!/bin/bash
# run_project3.sh - Sprint 3 Unified Pipeline
# Usage: ./run_project3.sh data/customer_data.csv

if [ $# -eq 0 ]; then
    echo "Usage: $0 path/to/customer_data.csv"
    exit 1
fi

DATA_FILE=$1
OUTPUT_DIR="sprint3_outputs"

echo "=== CS 131 Sprint 3 Pipeline ==="
echo "Dataset: $DATA_FILE"
echo "Started: $(date)"

mkdir -p $OUTPUT_DIR

# Step 1: Create edges (FIXED - category first, then customer)
echo "[Step 1] Creating edges..."
cut -d',' -f10,1 $DATA_FILE | tail -n +2 | tr ',' '\t' | awk '{print $2"\t"$1}' | sort -k1,1 > $OUTPUT_DIR/edges.tsv

echo "Sample edges:"
head -5 $OUTPUT_DIR/edges.tsv

# Step 2: Count entities
echo "[Step 2] Counting entities..."
cut -f1 $OUTPUT_DIR/edges.tsv | sort | uniq -c | sort -k2 | awk '{print $2"\t"$1}' > $OUTPUT_DIR/entity_counts.tsv

echo "Entity counts:"
cat $OUTPUT_DIR/entity_counts.tsv

# All pass threshold, copy all edges
cp $OUTPUT_DIR/edges.tsv $OUTPUT_DIR/edges_thresholded.tsv

# Step 3: Cluster sizes
echo "[Step 3] Computing cluster sizes..."
sort -k2,2n $OUTPUT_DIR/entity_counts.tsv > $OUTPUT_DIR/cluster_sizes.tsv

# Step 4: Top-30
echo "[Step 4] Top-30 analysis..."
cut -f2 $OUTPUT_DIR/edges_thresholded.tsv | sort | uniq -c | sort -nr | head -30 | awk '{print $2"\t"$1}' > $OUTPUT_DIR/top30_clusters.txt
cut -f2 $OUTPUT_DIR/edges.tsv | sort | uniq -c | sort -nr | head -30 | awk '{print $2"\t"$1}' > $OUTPUT_DIR/top30_overall.txt
comm -3 <(cut -f1 $OUTPUT_DIR/top30_clusters.txt | sort) <(cut -f1 $OUTPUT_DIR/top30_overall.txt | sort) > $OUTPUT_DIR/diff_top30.txt

echo ""
echo "=== Pipeline Complete ==="
echo "Completed: $(date)"
echo ""
echo "File sizes:"
ls -lh $OUTPUT_DIR/*.tsv $OUTPUT_DIR/*.txt | awk '{print $9, $5}'
