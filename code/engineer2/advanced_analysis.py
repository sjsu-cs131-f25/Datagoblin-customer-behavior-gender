"""
CS 131 Final Sprint - Advanced Customer Analysis
Team: Datagoblin | Engineer 2: Analysis & Optimization
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.window import Window

def main():
    print("=" * 70)
    print("ADVANCED CUSTOMER BEHAVIOR ANALYSIS")
    print("=" * 70)
    
    spark = SparkSession.builder \
        .appName("Datagoblin-Advanced-Analysis") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    # CORRECTED: Load cleaned data from Engineer 1
    input_path = "gs://datagoblin-customer-behavior/output/customer_data_clean"
    df = spark.read.parquet(input_path)
    
    print(f"\nLoaded {df.count():,} customers from Engineer 1's cleaned data")
    
    # ANALYSIS 1: CUSTOMER LIFETIME VALUE BY SEGMENT
    print("\n[ANALYSIS 1] Customer Lifetime Value by Segment")
    print("-" * 70)
    
    clv_by_segment = df.groupBy('loyalty_status', 'region') \
        .agg(
            count('*').alias('customer_count'),
            avg('purchase_amount').alias('avg_purchase'),
            sum('purchase_amount').alias('total_revenue'),
            avg('age').alias('avg_age'),
            avg('income').alias('avg_income'),
            avg('satisfaction_score').alias('avg_satisfaction')
        ) \
        .orderBy(desc('total_revenue'))
    
    print("\nTop Revenue Segments:")
    clv_by_segment.show(20, truncate=False)
    
    # Save
    clv_by_segment.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/aggregations/clv_by_segment")
    
    # ANALYSIS 2: AGE GROUP ANALYSIS
    print("\n[ANALYSIS 2] Purchase Patterns by Age Group")
    print("-" * 70)
    
    # Create age groups
    df_with_age_group = df.withColumn(
        'age_group',
        when(col('age') < 25, '18-24')
        .when(col('age') < 35, '25-34')
        .when(col('age') < 50, '35-49')
        .otherwise('50+')
    )
    
    age_analysis = df_with_age_group.groupBy('age_group') \
        .agg(
            count('*').alias('customers'),
            avg('purchase_amount').alias('avg_spending'),
            avg('satisfaction_score').alias('avg_satisfaction'),
            sum('purchase_amount').alias('total_revenue')
        ) \
        .orderBy('age_group')
    
    print("\nAge Group Spending:")
    age_analysis.show()
    
    # Save
    age_analysis.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/aggregations/age_analysis")
    
    # ANALYSIS 3: HIGH-VALUE CUSTOMERS (Percentile-based)
    print("\n[ANALYSIS 3] High-Value Customer Identification")
    print("-" * 70)
    
    # Calculate percentiles
    percentiles = df.stat.approxQuantile('purchase_amount', [0.75, 0.90, 0.95], 0.01)
    
    print(f"\nPurchase Amount Percentiles:")
    print(f"  75th percentile: ${percentiles[0]:,.2f}")
    print(f"  90th percentile: ${percentiles[1]:,.2f}")
    print(f"  95th percentile: ${percentiles[2]:,.2f}")
    
    # Segment customers
    df_segmented = df.withColumn(
        'value_tier',
        when(col('purchase_amount') >= percentiles[2], 'Platinum')
        .when(col('purchase_amount') >= percentiles[1], 'Gold')
        .when(col('purchase_amount') >= percentiles[0], 'Silver')
        .otherwise('Bronze')
    )
    
    value_tier_summary = df_segmented.groupBy('value_tier') \
        .agg(
            count('*').alias('customer_count'),
            avg('purchase_amount').alias('avg_purchase'),
            avg('income').alias('avg_income'),
            avg('satisfaction_score').alias('avg_satisfaction')
        ) \
        .orderBy(desc('avg_purchase'))
    
    print("\nValue Tier Summary:")
    value_tier_summary.show()
    
    # Save
    value_tier_summary.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/aggregations/value_tiers")
    
    # ANALYSIS 4: CATEGORY PREFERENCES BY LOYALTY
    print("\n[ANALYSIS 4] Product Category Preferences")
    print("-" * 70)
    
    category_affinity = df.groupBy('loyalty_status', 'product_category') \
        .agg(
            count('*').alias('purchases'),
            avg('purchase_amount').alias('avg_amount')
        )
    
    # Rank within each loyalty status
    window = Window.partitionBy('loyalty_status').orderBy(desc('purchases'))
    
    category_affinity_ranked = category_affinity.withColumn(
        'rank',
        row_number().over(window)
    ).filter(col('rank') <= 3)
    
    print("\nTop 3 Categories by Loyalty Status:")
    category_affinity_ranked.orderBy('loyalty_status', 'rank').show(20, truncate=False)
    
    # Save
    category_affinity_ranked.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/aggregations/category_affinity")
    
    print("\n" + "=" * 70)
    print("ADVANCED ANALYSIS COMPLETE!")
    print("=" * 70)
    
    spark.stop()

if __name__ == "__main__":
    main()