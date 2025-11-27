# Cloud Deployment Documentation
## Team Datagoblin - Final Sprint

### Infrastructure Configuration
- **GCP Project:** datagoblin-customer-analysis
- **Region:** us-west1
- **Bucket:** gs://datagoblin-customer-behavior/

### Cluster Specifications
- **Name:** datagoblin-final-cluster
- **Master:** 1x n1-standard-2 (2 vCPUs, 7.5GB RAM)
- **Workers:** 2x n1-standard-2 (2 vCPUs, 7.5GB RAM each)
- **Total:** 6 vCPUs, 22.5GB RAM
- **Image:** dataproc-2.1-debian11

### Data Pipeline
**Input:** gs://datagoblin-customer-behavior/data/customer_data.csv (8MB, 100k rows)

**Processing:**
1. Data cleaning (trim whitespace, handle nulls)
2. Frequency analysis (product, loyalty, region)
3. Top spender identification
4. Partitioned output by product_category

**Outputs:**
- Frequency tables (CSV)
- Top 30 spenders (CSV)
- Cleaned data (Parquet, partitioned)

### Performance Observations
- **Job Duration:** 1.3 minutes (both runs)
- **Stages:** 30 completed, 18 skipped (optimization working)
- **Tasks:** 45 total across 2 workers
- **Shuffle:** 5.8 MiB written
- **Jobs:** 28 completed successfully

### Evidence Captured
- 12 Spark UI screenshots
- Job logs saved
- Output samples downloaded
- DAG visualizations

### Running the Pipeline
```bash
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/customer_pipeline_cloud.py \
    --cluster=datagoblin-final-cluster \
    --region=us-west1
```

**Expected Duration:** ~2 minutes

### Scalability Analysis
**Current:** 100k rows in ~2 minutes

**10x Scale (1M rows):**
- Estimated: 15-20 minutes with current cluster
- Bottleneck: Shuffle operations during groupBy

**100x Scale (10M rows):**
- Would require: Larger cluster (8+ workers)
- Alternative: Auto-scaling with Dataproc Serverless
