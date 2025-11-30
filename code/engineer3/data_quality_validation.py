"""
CS 131 Final Sprint - Data Quality Validation
Team: Datagoblin | Engineer 3: Quality & Integration
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *

def main():
    print("=" * 70)
    print("DATA QUALITY VALIDATION REPORT")
    print("Team Datagoblin - Engineer 3: Ryan Kyaw")
    print("=" * 70)
    
    spark = SparkSession.builder \
        .appName("Datagoblin-Quality-Validation") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    # Load Engineer 1's cleaned data
    df = spark.read.parquet("gs://datagoblin-customer-behavior/output/customer_data_clean")
    
    total_rows = df.count()
    print(f"\n📊 Dataset Size: {total_rows:,} rows")
    print(f"📊 Columns: {len(df.columns)}")
    
    # VALIDATION 1: COMPLETENESS CHECK
    print("\n" + "=" * 70)
    print("[1/6] DATA COMPLETENESS CHECK")
    print("=" * 70)
    
    print(f"\n{'Column Name':<25} {'Null Count':>12} {'Null %':>10} {'Status':>10}")
    print("-" * 70)
    
    all_complete = True
    for col_name in df.columns:
        null_count = df.filter(col(col_name).isNull()).count()
        null_pct = (null_count / total_rows) * 100
        status = "✓ PASS" if null_pct == 0 else "✗ FAIL"
        if null_pct > 0:
            all_complete = False
        print(f"{col_name:<25} {null_count:>12,} {null_pct:>9.2f}% {status:>10}")
    
    print(f"\nCompleteness Check: {'✓ PASSED' if all_complete else '✗ FAILED'}")
    
    # VALIDATION 2: DATA RANGE VALIDATION
    print("\n" + "=" * 70)
    print("[2/6] DATA RANGE VALIDATION")
    print("=" * 70)
    
    # Age validation
    age_stats = df.select(
        min('age').alias('min_age'),
        max('age').alias('max_age'),
        avg('age').alias('avg_age')
    ).collect()[0]
    
    age_valid = 18 <= age_stats['min_age'] and age_stats['max_age'] <= 100
    print(f"\n{'✓' if age_valid else '✗'} Age Range:")
    print(f"  Min: {age_stats['min_age']:.0f} years")
    print(f"  Max: {age_stats['max_age']:.0f} years")
    print(f"  Avg: {age_stats['avg_age']:.1f} years")
    print(f"  Expected: 18-100 years")
    print(f"  Status: {'✓ PASS' if age_valid else '✗ FAIL'}")
    
    # Income validation
    income_stats = df.select(
        min('income').alias('min_income'),
        max('income').alias('max_income'),
        avg('income').alias('avg_income')
    ).collect()[0]
    
    income_valid = income_stats['min_income'] > 0 and income_stats['max_income'] < 500000
    print(f"\n{'✓' if income_valid else '✗'} Income Range:")
    print(f"  Min: ${income_stats['min_income']:,.0f}")
    print(f"  Max: ${income_stats['max_income']:,.0f}")
    print(f"  Avg: ${income_stats['avg_income']:,.0f}")
    print(f"  Status: {'✓ PASS' if income_valid else '✗ FAIL'}")
    
    # Purchase amount validation
    purchase_stats = df.select(
        min('purchase_amount').alias('min_purchase'),
        max('purchase_amount').alias('max_purchase'),
        avg('purchase_amount').alias('avg_purchase')
    ).collect()[0]
    
    purchase_valid = purchase_stats['min_purchase'] > 0 and purchase_stats['max_purchase'] < 50000
    print(f"\n{'✓' if purchase_valid else '✗'} Purchase Amount Range:")
    print(f"  Min: ${purchase_stats['min_purchase']:,.2f}")
    print(f"  Max: ${purchase_stats['max_purchase']:,.2f}")
    print(f"  Avg: ${purchase_stats['avg_purchase']:,.2f}")
    print(f"  Status: {'✓ PASS' if purchase_valid else '✗ FAIL'}")
    
    # Satisfaction score
    satisfaction_stats = df.select(
        min('satisfaction_score').alias('min_sat'),
        max('satisfaction_score').alias('max_sat'),
        avg('satisfaction_score').alias('avg_sat')
    ).collect()[0]
    
    sat_valid = 1 <= satisfaction_stats['min_sat'] and satisfaction_stats['max_sat'] <= 7
    print(f"\n{'✓' if sat_valid else '✗'} Satisfaction Score Range:")
    print(f"  Min: {satisfaction_stats['min_sat']:.1f}")
    print(f"  Max: {satisfaction_stats['max_sat']:.1f}")
    print(f"  Avg: {satisfaction_stats['avg_sat']:.2f}")
    print(f"  Expected: 1-7")
    print(f"  Status: {'✓ PASS' if sat_valid else '✗ FAIL'}")
    
    # VALIDATION 3: CATEGORICAL VALUES
    print("\n" + "=" * 70)
    print("[3/6] CATEGORICAL VALUE VALIDATION")
    print("=" * 70)
    
    # Loyalty status
    loyalty_values = df.select('loyalty_status').distinct().rdd.flatMap(lambda x: x).collect()
    expected_loyalty = {'Gold', 'Silver', 'Regular'}
    loyalty_valid = set(loyalty_values) == expected_loyalty
    print(f"\n{'✓' if loyalty_valid else '✗'} Loyalty Status:")
    print(f"  Found: {sorted(loyalty_values)}")
    print(f"  Expected: {sorted(expected_loyalty)}")
    print(f"  Status: {'✓ PASS' if loyalty_valid else '✗ FAIL'}")
    
    # Regions
    region_values = df.select('region').distinct().rdd.flatMap(lambda x: x).collect()
    expected_regions = {'North', 'South', 'East', 'West'}
    region_valid = set(region_values) == expected_regions
    print(f"\n{'✓' if region_valid else '✗'} Regions:")
    print(f"  Found: {sorted(region_values)}")
    print(f"  Expected: {sorted(expected_regions)}")
    print(f"  Status: {'✓ PASS' if region_valid else '✗ FAIL'}")
    
    # Product categories
    category_values = df.select('product_category').distinct().collect()
    category_count = len(category_values)
    print(f"\n✓ Product Categories:")
    print(f"  Count: {category_count} unique values")
    for cat in sorted([row['product_category'] for row in category_values]):
        count = df.filter(col('product_category') == cat).count()
        print(f"    - {cat}: {count:,} customers")
    
    # Gender
    gender_values = df.select('gender').distinct().rdd.flatMap(lambda x: x).collect()
    print(f"\n✓ Gender:")
    print(f"  Values: {sorted(gender_values)}")
    
    # VALIDATION 4: AGGREGATION CONSISTENCY
    print("\n" + "=" * 70)
    print("[4/6] AGGREGATION CONSISTENCY CHECK")
    print("=" * 70)
    
    # Load and validate CLV aggregation
    clv_df = spark.read.csv("gs://datagoblin-customer-behavior/output/aggregations/clv_by_segment/", header=True)
    total_in_clv = clv_df.select(sum(col('customer_count').cast('int'))).collect()[0][0]
    clv_consistent = total_in_clv == total_rows
    
    print(f"\n{'✓' if clv_consistent else '✗'} CLV Segmentation:")
    print(f"  Total customers: {total_in_clv:,}")
    print(f"  Expected: {total_rows:,}")
    print(f"  Status: {'✓ PASS' if clv_consistent else '✗ FAIL'}")
    
    # Validate age analysis
    age_df = spark.read.csv("gs://datagoblin-customer-behavior/output/aggregations/age_analysis/", header=True)
    total_in_age = age_df.select(sum(col('customers').cast('int'))).collect()[0][0]
    age_consistent = total_in_age == total_rows
    
    print(f"\n{'✓' if age_consistent else '✗'} Age Analysis:")
    print(f"  Total customers: {total_in_age:,}")
    print(f"  Expected: {total_rows:,}")
    print(f"  Status: {'✓ PASS' if age_consistent else '✗ FAIL'}")
    
    # VALIDATION 5: ML SEGMENTATION
    print("\n" + "=" * 70)
    print("[5/6] ML SEGMENTATION VALIDATION")
    print("=" * 70)
    
    # Load segment profiles
    segments_df = spark.read.csv("gs://datagoblin-customer-behavior/output/ml_segmentation/segment_profiles/", header=True)
    
    segment_count = segments_df.count()
    total_segmented = segments_df.select(sum(col('customer_count').cast('int'))).collect()[0][0]
    
    segments_valid = segment_count == 4 and total_segmented == total_rows
    
    print(f"\n{'✓' if segments_valid else '✗'} ML Segmentation:")
    print(f"  Number of segments: {segment_count} (expected 4)")
    print(f"  Total customers segmented: {total_segmented:,}")
    print(f"  Expected: {total_rows:,}")
    print(f"  Status: {'✓ PASS' if segments_valid else '✗ FAIL'}")
    
    print("\nSegment Distribution:")
    for row in segments_df.collect():
        seg_id = row['segment']
        count = int(row['customer_count'])
        pct = (count / total_rows) * 100
        print(f"  Segment {seg_id}: {count:,} customers ({pct:.1f}%)")
    
    # VALIDATION 6: OUTPUT FILES
    print("\n" + "=" * 70)
    print("[6/6] OUTPUT FILES VALIDATION")
    print("=" * 70)
    
    import subprocess
    
    # Check visualizations
    result = subprocess.run(
        ['gsutil', 'ls', 'gs://datagoblin-customer-behavior/output/visualizations/'],
        capture_output=True,
        text=True
    )
    
    viz_files = [line.split('/')[-1] for line in result.stdout.strip().split('\n') if line.endswith('.png')]
    expected_viz_count = 6
    viz_valid = len(viz_files) == expected_viz_count
    
    print(f"\n{'✓' if viz_valid else '✗'} Visualization Files:")
    print(f"  Found: {len(viz_files)} PNG files")
    print(f"  Expected: {expected_viz_count}")
    print(f"  Status: {'✓ PASS' if viz_valid else '✗ FAIL'}")
    
    for viz in sorted(viz_files):
        print(f"    - {viz}")
    
    # Check aggregation folders
    agg_folders = ['clv_by_segment', 'age_analysis', 'value_tiers', 'category_affinity']
    print(f"\n✓ Aggregation Outputs:")
    for folder in agg_folders:
        result = subprocess.run(
            ['gsutil', 'ls', f'gs://datagoblin-customer-behavior/output/aggregations/{folder}/'],
            capture_output=True,
            text=True
        )
        files = [line for line in result.stdout.strip().split('\n') if line.endswith('.csv')]
        print(f"    - {folder}: {len(files)} CSV file(s)")

    # FINAL SUMMARY
    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    
    all_passed = (
        all_complete and 
        age_valid and income_valid and purchase_valid and sat_valid and
        loyalty_valid and region_valid and
        clv_consistent and age_consistent and
        segments_valid and
        viz_valid
    )
    
    print(f"\n{'✓ PASS' if all_complete else '✗ FAIL'} - Data Completeness")
    print(f"{'✓ PASS' if (age_valid and income_valid and purchase_valid and sat_valid) else '✗ FAIL'} - Range Validation")
    print(f"{'✓ PASS' if (loyalty_valid and region_valid) else '✗ FAIL'} - Categorical Values")
    print(f"{'✓ PASS' if (clv_consistent and age_consistent) else '✗ FAIL'} - Aggregation Consistency")
    print(f"{'✓ PASS' if segments_valid else '✗ FAIL'} - ML Segmentation")
    print(f"{'✓ PASS' if viz_valid else '✗ FAIL'} - Output Files")
    
    print("\n" + "=" * 70)
    if all_passed:
        print("🎉 ALL VALIDATIONS PASSED!")
    else:
        print("⚠️  SOME VALIDATIONS FAILED - REVIEW ABOVE")
    print("=" * 70)
    
    # Save summary report
    print("\nSaving validation summary...")
    summary_data = [
        ("Data Completeness", "PASS" if all_complete else "FAIL"),
        ("Range Validation", "PASS" if (age_valid and income_valid and purchase_valid) else "FAIL"),
        ("Categorical Values", "PASS" if (loyalty_valid and region_valid) else "FAIL"),
        ("Aggregation Consistency", "PASS" if (clv_consistent and age_consistent) else "FAIL"),
        ("ML Segmentation", "PASS" if segments_valid else "FAIL"),
        ("Output Files", "PASS" if viz_valid else "FAIL")
    ]
    
    summary_df = spark.createDataFrame(summary_data, ["Validation_Test", "Status"])
    summary_df.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/validation/summary")
    
    print("✓ Validation summary saved to: gs://datagoblin-customer-behavior/output/validation/summary/")
    
    spark.stop()

if __name__ == "__main__":
    main()