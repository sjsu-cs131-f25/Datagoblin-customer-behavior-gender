#!/usr/bin/env bash
set -euo pipefail

# ============================================================================
# run_pa4.sh - Sprint 4 Main Entry Script
# Usage: ./run_pa4.sh <input_csv>
# ============================================================================

# Check arguments
if [ $# -eq 0 ]; then
    echo "Usage: $0 <input_csv_file>"
    echo "Example: ./run_pa4.sh data/customer_data.csv"
    exit 1
fi

INPUT="$1"
OUTDIR="out"
LOGDIR="logs"

# Create directories
mkdir -p "$OUTDIR" "$LOGDIR"

# Check input exists
if [ ! -f "$INPUT" ]; then
    echo "Error: Input file not found: $INPUT"
    exit 1
fi

# Set permissions for group access
chmod -R g+rX "$INPUT" || true

# Start logging
exec > >(tee -a "$LOGDIR/run_pa4.log")
exec 2>&1

echo "============================================================================"
echo "Sprint 4: Customer Shopping Data Analysis Pipeline"
echo "============================================================================"
echo "Started: $(date)"
echo "Input: $INPUT"
echo "Output: $OUTDIR/"
echo "============================================================================"
echo ""

# ============================================================================
# ENGINEER 1: Data Cleaning & Normalization (Tasks 1-2)
# ============================================================================

echo "=== Engineer 1: Data Cleaning & Normalization ==="
echo ""

cleanfile="$OUTDIR/cleaned_data.tsv"

echo "[Task 1] Cleaning and normalizing data..."
head -n 10 "$INPUT" > "$OUTDIR/clean_sample_before.tsv"

sed 's/,/\t/g' "$INPUT" > "$cleanfile"

head -n 10 "$cleanfile" > "$OUTDIR/clean_sample_after.tsv"
echo "  ✓ Created cleaned_data.tsv"

echo "[Task 2] Creating frequency tables and skinny table..."

# Frequency tables
awk -F'\t' 'NR>1 {print $3}' "$cleanfile" | sort | uniq -c | sort -nr > "$OUTDIR/freq_gender.tsv"
echo "  ✓ Created freq_gender.tsv"

awk -F'\t' 'NR>1 {print $10}' "$cleanfile" | sort | uniq -c | sort -nr > "$OUTDIR/freq_category.tsv"
echo "  ✓ Created freq_category.tsv"

# Top-N list
awk -F'\t' 'NR>1 {print $10}' "$cleanfile" | sort | uniq -c | sort -nr | head -n 10 > "$OUTDIR/top10_product_categories.tsv"
echo "  ✓ Created top10_product_categories.tsv"

# Skinny table
awk -F'\t' 'BEGIN {OFS="\t"}
    NR==1 {
        print "id", "gender", "region", "purchase_amount", "product_category", "satisfaction_score"
        next
    }
    {
        print $1, $3, $6, $9, $10, $12
    }' "$cleanfile" > "$OUTDIR/skinny.tsv"
echo "  ✓ Created skinny.tsv"

echo ""

# ============================================================================
# ENGINEER 2: Quality Filters & Buckets (Tasks 3-4)
# ============================================================================

echo "=== Engineer 2: Quality Filters & Purchase Buckets ==="
echo ""

echo "[Task 3] Applying quality filters..."
./scripts/awk/quality_filters.awk "$OUTDIR/skinny.tsv" > "$OUTDIR/filtered_data.tsv"
filtered_count=$(wc -l < "$OUTDIR/filtered_data.tsv")
original_count=$(wc -l < "$OUTDIR/skinny.tsv")
removed=$((original_count - filtered_count))
echo "  ✓ Original: $original_count rows"
echo "  ✓ Filtered: $filtered_count rows"
echo "  ✓ Removed: $removed invalid rows"

echo "[Task 4] Computing purchase buckets and category summaries..."
./scripts/awk/buckets.awk "$OUTDIR/filtered_data.tsv" > "$OUTDIR/buckets_summary.tsv"
echo "  ✓ Created buckets_summary.tsv"

echo ""

# ============================================================================
# ENGINEER 3: Would add Tasks 5-6 here
# ============================================================================

# echo "=== Engineer 3: Regional Analysis & Signal Discovery ==="
# echo ""
# echo "[Task 5] Analyzing regional patterns..."
# ./scripts/awk/region_analysis.awk "$OUTDIR/filtered_data.tsv" > "$OUTDIR/region_distribution.tsv"
# echo "  ✓ Created region_distribution.tsv"
#
# echo "[Task 6] Discovering signals (outliers)..."
# ./scripts/awk/signal_discovery.awk "$OUTDIR/filtered_data.tsv" > "$OUTDIR/high_value_customers.tsv"
# echo "  ✓ Created high_value_customers.tsv"
#
# echo ""

# ============================================================================
# SUMMARY
# ============================================================================

echo "============================================================================"
echo "Pipeline Complete!"
echo "============================================================================"
echo "Finished: $(date)"
echo ""
echo "Outputs created in $OUTDIR/:"
ls -lh "$OUTDIR/" | tail -n +2
echo ""
echo "Log saved to: $LOGDIR/run_pa4.log"
echo "============================================================================"
