# Datagoblin Customer Behavior Analysis
**CS 131 Final Sprint - Team Datagoblin**

## Team Members
- **Engineer #1** (Cloud Infrastructure): Nishinn Thant
- **Engineer #2** (Analysis & ML): Winthurain Lin  
- **Engineer #3** (Quality & Integration): Ryan Kyaw
- **Storyteller**: [Ivy Yee]
- **Product Manager**: [Nathan Jang]

## Project Overview
Big data analysis of 100,000 customer records using distributed Spark processing on Google Cloud Platform.

### Technologies Used
- **Platform**: Google Cloud Dataproc
- **Processing**: Apache Spark (PySpark)
- **Storage**: Google Cloud Storage
- **Machine Learning**: K-Means clustering (K=4)
- **Visualization**: Matplotlib, Seaborn

### Dataset
- **Size**: 100,000 customer records
- **Features**: 12 columns (demographics, behavior, satisfaction)
- **Storage**: Google Cloud Storage bucket

## Repository Structure
```
Datagoblin-customer-behavior-gender/
├── code/
│   ├── engineer1/          # Cloud infrastructure & data pipeline
│   │   └── customer_pipeline_cloud.py
│   ├── engineer2/          # Advanced analysis & ML
│   │   ├── advanced_analysis.py
│   │   ├── performance_optimization.py
│   │   ├── visualizations.py
│   │   └── ml_segmentation.py
│   └── engineer3/          # Validation & quality assurance
│       └── data_quality_validation.py
├── visualizations/         # 6 executive charts (PNG)
│   ├── viz1_age_spending.png
│   ├── viz2_loyalty_distribution.png
│   ├── viz3_category_revenue.png
│   ├── viz4_income_spending.png
│   ├── viz5_region_satisfaction.png
│   └── viz6_purchase_frequency.png
├── results/samples/        # Sample outputs (CSV)
│   ├── clv_by_segment.csv
│   ├── age_analysis.csv
│   ├── value_tiers.csv
│   ├── category_affinity.csv
│   ├── performance_results.csv
│   └── segment_profiles.csv
├── docs/                   # Documentation
│   ├── CLOUD_SETUP.md
│   ├── ANALYSIS_DOCUMENTATION.md
│   ├── DATA_QUALITY_ISSUES.md
│   └── VALIDATION_REPORT.md
└── evidence/              # Spark UI screenshots
    ├── engineer1_screenshots/
    ├── engineer2_screenshots/
    └── engineer3_screenshots/
```

## Quick Start

### Prerequisites
- GCP account with billing enabled
- Access to `datagoblin-customer-analysis` project
- gcloud CLI installed and authenticated

### Setup GCP Environment
```bash
# Set project and region
gcloud config set project datagoblin-customer-analysis
gcloud config set compute/region us-west1
gcloud config set compute/zone us-west1-a

# Create Dataproc cluster
gcloud dataproc clusters create datagoblin-cluster \
    --region=us-west1 \
    --zone=us-west1-a \
    --master-machine-type=n1-standard-2 \
    --master-boot-disk-size=100GB \
    --num-workers=2 \
    --worker-machine-type=n1-standard-2 \
    --worker-boot-disk-size=100GB \
    --image-version=2.1-debian11 \
    --enable-component-gateway \
    --bucket=datagoblin-customer-behavior
```

## Pipeline Execution

### Engineer 1: Data Cleaning & Initial Pipeline
```bash
# Submit data cleaning job
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/customer_pipeline_cloud.py \
    --cluster=datagoblin-cluster \
    --region=us-west1
```

**Outputs:**
- Cleaned data partitioned by product category
- Frequency analysis by category, loyalty, region
- Top spenders identification

---

### Engineer 2: Advanced Analysis & Machine Learning
```bash
# 1. Advanced aggregations
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/advanced_analysis.py \
    --cluster=datagoblin-cluster \
    --region=us-west1

# 2. Performance optimization testing
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/performance_optimization.py \
    --cluster=datagoblin-cluster \
    --region=us-west1

# 3. Generate visualizations
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/visualizations.py \
    --cluster=datagoblin-cluster \
    --region=us-west1

# 4. ML customer segmentation
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/ml_segmentation.py \
    --cluster=datagoblin-cluster \
    --region=us-west1
```

**Outputs:**
- 4 advanced aggregations (CLV, age groups, value tiers, category affinity)
- Performance benchmark results (5 configurations tested)
- 6 executive visualizations
- K-Means customer segmentation (4 personas)

---

### Engineer 3: Quality Validation
```bash
# Run data quality validation
gcloud dataproc jobs submit pyspark \
    gs://datagoblin-customer-behavior/code/data_quality_validation.py \
    --cluster=datagoblin-cluster \
    --region=us-west1
```

**Validation Tests:**
- Data completeness check
- Range validation
- Categorical value validation
- Aggregation consistency
- ML segmentation validation
- Output file verification

---

### Cleanup (IMPORTANT!)
```bash
# Delete cluster to stop charges
gcloud dataproc clusters delete datagoblin-cluster \
    --region=us-west1 \
    --quiet
```

## Data Locations

### Cloud Storage Structure
```
gs://datagoblin-customer-behavior/
├── data/
│   └── customer_data.csv                    # Original data (100k rows)
├── code/
│   ├── customer_pipeline_cloud.py           # Engineer 1
│   ├── advanced_analysis.py                 # Engineer 2
│   ├── performance_optimization.py          # Engineer 2
│   ├── visualizations.py                    # Engineer 2
│   ├── ml_segmentation.py                   # Engineer 2
│   └── data_quality_validation.py           # Engineer 3
└── output/
    ├── customer_data_clean/                 # Cleaned & partitioned
    ├── freq_category/                       # Frequency analyses
    ├── freq_loyalty/
    ├── freq_region/
    ├── top_spenders/
    ├── aggregations/                        # Advanced aggregations
    │   ├── clv_by_segment/
    │   ├── age_analysis/
    │   ├── value_tiers/
    │   └── category_affinity/
    ├── performance_results/                 # Performance benchmarks
    ├── visualizations/                      # 6 PNG charts
    ├── ml_segmentation/                     # Customer segments
    │   ├── customer_segments/
    │   └── segment_profiles/
    └── validation/                          # QA results
        └── summary/
```

## Key Findings

### Data Quality (Engineer 3 Validation)
**Overall**: 5/6 tests passed (83% pass rate)

✅ **Passed:**
- Data completeness: 0% null values
- Categorical values: All expected values present
- Aggregation consistency: 100,000 total across all analyses
- ML segmentation: 4 balanced clusters
- Output files: All visualizations and aggregations generated

⚠️ **Issues Identified:**
- **Age range**: 12-49 years (includes minors, lacks seniors)
- **Satisfaction score**: 0-10 scale (expected 1-7)

*Note: These issues exist in the source data, not in processing. All engineering work was performed correctly.*

---

### Customer Segmentation (Engineer 2 - ML)
**K-Means Clustering (K=4):**
- Segment 0: 28,997 customers (29.0%)
- Segment 1: 28,458 customers (28.5%)
- Segment 2: 21,286 customers (21.3%)
- Segment 3: 21,259 customers (21.3%)

**Customer Personas:**
- Budget Shoppers
- Premium Buyers
- Loyal Regulars
- High-Value VIPs

---

### Product Category Distribution
1. **Electronics**: 30,027 customers (30%)
2. **Clothing**: 19,989 customers (20%)
3. **Books**: 14,925 customers (15%)
4. **Food**: 14,822 customers (15%)
5. **Health**: 10,123 customers (10%)
6. **Beauty**: 5,035 customers (5%)
7. **Home**: 5,079 customers (5%)

---

### Performance Optimization (Engineer 2)
- Tested 5 shuffle partition configurations (2, 8, 16, 32, 64)
- Optimal configuration identified for 100k dataset
- Distributed processing across 2 worker nodes
- Average job duration: 2-3 minutes

## Documentation

- **[Cloud Setup Guide](docs/CLOUD_SETUP.md)** - GCP project setup and Dataproc configuration (Engineer 1)
- **[Analysis Documentation](docs/ANALYSIS_DOCUMENTATION.md)** - Advanced analytics methodology (Engineer 2)
- **[Data Quality Issues](docs/DATA_QUALITY_ISSUES.md)** - Identified data quality problems (Engineer 3)
- **[Validation Report](docs/VALIDATION_REPORT.md)** - Complete validation results (Engineer 3)

## Cost Management

### Estimated Costs
- **Total project**: ~$10-15
- **Dataproc cluster**: $2-3/hour
- **Cloud Storage**: ~$0.20 total
- **Data egress**: Minimal

### Cost Optimization Tips
1. ✅ Use preemptible workers when possible
2. ✅ Delete clusters immediately after use
3. ✅ Use appropriate machine types (n1-standard-2)
4. ✅ Minimize disk sizes (100GB vs 500GB default)
5. ✅ Clean up unused Cloud Storage objects

**⚠️ CRITICAL**: Always delete clusters after capturing screenshots/logs!

## Known Limitations

1. **Data Quality Issues** (discovered by Engineer 3):
   - Dataset contains minors (age 12-17) - may require compliance review
   - Satisfaction score scale mismatch (0-10 vs expected 1-7)

2. **Project Scope**:
   - Limited to 100k records for cost management
   - Single snapshot analysis (no time-series)
   - Synthetic/sample data may not reflect real customer patterns

3. **Technical Constraints**:
   - GCP quota limits (disk space, compute)
   - Single region deployment (us-west1)

## Validation Results

| Validation Test | Status | Details |
|----------------|--------|---------|
| Data Completeness | ✅ PASS | 0% null values across all 12 columns |
| **Range Validation** | ⚠️ **FAIL** | **Age: 12-49, Satisfaction: 0-10** |
| Categorical Values | ✅ PASS | All loyalty, region, category values present |
| Aggregation Consistency | ✅ PASS | All totals sum to 100,000 |
| ML Segmentation | ✅ PASS | 4 balanced clusters created |
| Output Files | ✅ PASS | 6 visualizations, 4 aggregations generated |

**Overall**: 83% pass rate - validation system successfully identified source data quality issues.

## Team Contributions

### Engineer 1: Nishinn Thant
- GCP project setup and infrastructure
- Dataproc cluster deployment
- Data cleaning pipeline
- Initial frequency analyses
- Cloud storage organization

### Engineer 2: Winthurain Lin
- Advanced aggregations (CLV, age groups, value tiers)
- Performance optimization experiments
- 6 executive visualizations
- K-Means customer segmentation
- ML model evaluation

### Engineer 3: Ryan Kyaw
- Data quality validation framework
- Consistency verification across all outputs
- Data quality issue identification
- Comprehensive documentation
- Integration and QA

## Technologies & Tools

- **Cloud Platform**: Google Cloud Platform
- **Compute**: Dataproc (Managed Spark)
- **Storage**: Cloud Storage
- **Processing**: Apache Spark 3.x (PySpark)
- **ML Libraries**: PySpark MLlib
- **Visualization**: Matplotlib, Seaborn
- **Version Control**: Git, GitHub

**Last Updated**: November 29, 2025  
**Project Status**: Complete - All 3 engineers finished