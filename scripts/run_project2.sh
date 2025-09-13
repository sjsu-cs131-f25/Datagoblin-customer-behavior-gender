#!/bin/bash
# Usage: ./scripts/run_project2.sh data/customer_data.csv
# Customer behavior analysis pipeline
# Assumes CSV with comma delimiter and header

DATASET_PATH=${1:-data/customer_data.csv}

if [ ! -f "$DATASET_PATH" ]; then
    echo "Error: Dataset file not found: $DATASET_PATH"
    exit 1
fi

mkdir -p data/samples out logs

echo "=== Customer Behavior Analysis Pipeline ===" | tee out/analysis.log
echo "Dataset: $DATASET_PATH" | tee -a out/analysis.log
echo "Started: $(date)" | tee -a out/analysis.log

echo "Creating 1000-record sample..." | tee -a out/analysis.log
head -1 $DATASET_PATH > data/samples/customer_sample_1k.csv
tail -n +2 $DATASET_PATH | shuf -n 1000 >> data/samples/customer_sample_1k.csv
echo "Sample created: $(wc -l < data/samples/customer_sample_1k.csv) lines" | tee -a out/analysis.log

echo "Building frequency tables..." | tee -a out/analysis.log
tail -n +2 $DATASET_PATH | cut -d',' -f2 | sort | uniq -c | sort -nr > out/freq_gender.txt
tail -n +2 $DATASET_PATH | cut -d',' -f10 | sort | uniq -c | sort -nr > out/freq_product_category.txt

echo "Identifying top spenders..." | tee -a out/analysis.log
tail -n +2 $DATASET_PATH | cut -d',' -f1,9 | sort -t',' -k2,2nr | head -20 > out/top_spenders.txt

echo "Creating skinny table..." | tee -a out/analysis.log
tail -n +2 $DATASET_PATH | cut -d',' -f2,4,9 | sort -u > out/gender_income_spending.txt

echo "Running grep analysis..." | tee -a out/analysis.log
grep -i "female" $DATASET_PATH | wc -l > out/female_count.txt
grep -v "Books" $DATASET_PATH > out/non_books_customers.txt

echo "Analysis complete: $(date)" | tee -a out/analysis.log
