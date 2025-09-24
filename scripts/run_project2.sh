#!/bin/bash
# run_project2.sh - Customer Behavior Analysis
# Usage: ./run_project2.sh data/customer_data.csv
# Delimiter: comma | Header: yes

INPUT=${1:-"data/customer_data.csv"}

echo "========== CUSTOMER ANALYSIS =========="
echo "Dataset: $INPUT"
echo "Started: $(date)"
echo ""

mkdir -p data/samples out logs

# A) DATA CARD
echo "=== A) File Information ==="
ls -lh "$INPUT"
echo "Total lines: $(wc -l < "$INPUT")"
echo "Header: $(head -1 "$INPUT")"
echo ""

# B) SAMPLE
echo "=== B) Creating 1000-record Sample ==="
head -1 "$INPUT" > data/samples/customer_sample_1k.csv
tail -n +2 "$INPUT" | shuf -n 1000 >> data/samples/customer_sample_1k.csv
echo "✓ Sample: $(wc -l < data/samples/customer_sample_1k.csv) lines"
echo ""

# C) FREQUENCY 1: GENDER (column 3!)
echo "=== C.1) Gender Frequency (with tee) ==="
tail -n +2 "$INPUT" | cut -d',' -f3 | tr -d '"' | sort | uniq -c | sort -nr | tee out/freq_gender.txt
echo ""

# C) FREQUENCY 2: PRODUCTS (column 10)
echo "=== C.2) Product Frequency (with tee) ==="
tail -n +2 "$INPUT" | cut -d',' -f10 | tr -d '"' | sort | uniq -c | sort -nr | tee out/freq_product_category.txt
echo ""

# C) FREQUENCY 3: REGION (bonus)
echo "=== C.3) Region Frequency ==="
tail -n +2 "$INPUT" | cut -d',' -f6 | tr -d '"' | sort | uniq -c | sort -nr > out/freq_region.txt
cat out/freq_region.txt
echo ""

# C) TOP-N: Top 20 Spenders
echo "=== C.4) Top 20 Spenders ==="
tail -n +2 "$INPUT" | cut -d',' -f1,9 | sort -t',' -k2,2nr | head -20 > out/top_spenders.txt
echo "Preview:"
head -10 out/top_spenders.txt
echo "✓ Saved to: out/top_spenders.txt"
echo ""

# C) SKINNY TABLE (dedupe)
echo "=== C.5) Skinny Table (Gender,Income,Spending) ==="
tail -n +2 "$INPUT" | cut -d',' -f3,4,9 | tr -d '"' | sort -u > out/skinny_table.txt
echo "✓ Unique combinations: $(wc -l < out/skinny_table.txt)"
head -5 out/skinny_table.txt
echo ""

# C) GREP -i (case-insensitive)
echo "=== C.6) grep -i (case-insensitive) ==="
FEMALE=$(grep -i "female" "$INPUT" | wc -l)
echo "$FEMALE" > out/female_count.txt
echo "✓ Female customers: $FEMALE"

# C) GREP -v (invert)
echo "=== C.7) grep -v (invert-match) ==="
grep -v "Electronics" "$INPUT" > out/non_electronics.txt
echo "✓ Non-Electronics: $(wc -l < out/non_electronics.txt)"
echo ""

# D) REDIRECTION (stdout vs stderr)
echo "=== D) Redirection Demo (> vs 2>) ==="
ls FAKE.csv > out/stdout.log 2> out/stderr.log || true
echo "✓ Error captured in: out/stderr.log"
cat out/stderr.log
echo ""

# E) SUMMARY LOG (with tee)
echo "=== E) Summary Log ==="
{
    echo "Analysis Complete: $(date)"
    echo "Dataset: $INPUT"
    echo "Records: $(wc -l < "$INPUT")"
    echo ""
    echo "Key Results:"
    echo "  Gender: $(head -1 out/freq_gender.txt)"
    echo "  Product: $(head -1 out/freq_product_category.txt)"
    echo "  Top Spender: $(head -1 out/top_spenders.txt)"
} | tee out/summary.log

echo ""
echo "========== COMPLETE! =========="
ls -lh out/
echo "=========================================="
