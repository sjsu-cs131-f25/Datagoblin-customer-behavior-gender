"""
CS 131 Final Sprint - Customer Behavior Analysis Pipeline
Team: Datagoblin | Engineer 1: Cloud Infrastructure
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import sys

def main():
    print("=" * 70)
    print("DATAGOBLIN CUSTOMER ANALYSIS PIPELINE - CLOUD RUN")
    print("=" * 70)
    
    # Initialize Spark
    spark = SparkSession.builder \
        .appName("Datagoblin-Customer-Analysis-Final") \
        .config("spark.sql.shuffle.partitions", "8") \
        .config("spark.executor.memory", "2g") \
        .config("spark.driver.memory", "2g") \
        .getOrCreate()
    
    spark.sparkContext.setLogLevel("INFO")
    
    # STEP 1: READ DATA FROM CLOUD STORAGE
    print("\n[1/5] Reading data from Cloud Storage...")
    
    input_path = "gs://datagoblin-customer-behavior/data/customer_data.csv"
    
    df = spark.read.csv(
        input_path,
        header=True,
        inferSchema=True
    )
    
    print(f"✓ Loaded {df.count():,} records")
    df.printSchema()
    
    # STEP 2: DATA CLEANING
    print("\n[2/5] Cleaning data...")
    
    df_clean = df \
        .withColumn('id', trim(col('id'))) \
        .withColumn('product_category', trim(col('product_category'))) \
        .withColumn('gender', trim(col('gender'))) \
        .withColumn('region', trim(col('region'))) \
        .withColumn('loyalty_status', trim(col('loyalty_status'))) \
        .withColumn('purchase_frequency', trim(col('purchase_frequency'))) \
        .na.drop(subset=['id', 'purchase_amount', 'product_category'])
    
    print(f"✓ After cleaning: {df_clean.count():,} records")
    
    # Cache for multiple operations
    df_clean.cache()
    
    # STEP 3: FREQUENCY ANALYSIS (Sprint 2 Recreation)
    print("\n[3/5] Computing frequency distributions...")
    
    # Product category frequency
    freq_category = df_clean.groupBy('product_category') \
        .count() \
        .orderBy(desc('count')) \
        .withColumnRenamed('count', 'frequency')
    
    print("Product Category Distribution:")
    freq_category.show()
    
    # Loyalty status frequency
    freq_loyalty = df_clean.groupBy('loyalty_status') \
        .count() \
        .orderBy(desc('count')) \
        .withColumnRenamed('count', 'frequency')
    
    print("Loyalty Status Distribution:")
    freq_loyalty.show()
    
    # Regional distribution
    freq_region = df_clean.groupBy('region') \
        .count() \
        .orderBy(desc('count')) \
        .withColumnRenamed('count', 'frequency')
    
    print("Regional Distribution:")
    freq_region.show()
    
    # STEP 4: TOP SPENDERS ANALYSIS
    print("\n[4/5] Finding top spenders...")
    
    top_spenders = df_clean \
        .select('id', 'age', 'gender', 'income', 'purchase_amount', 
                'product_category', 'loyalty_status') \
        .orderBy(desc('purchase_amount')) \
        .limit(30)
    
    print("Top 30 Spenders:")
    top_spenders.show(30, truncate=False)
    
    # STEP 5: WRITE RESULTS TO CLOUD STORAGE
    print("\n[5/5] Writing results to Cloud Storage...")
    
    output_base = "gs://datagoblin-customer-behavior/output"
    
    # Write frequency tables (coalesce to avoid many small files)
    freq_category.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv(f"{output_base}/freq_category")
    print("✓ Wrote product category frequencies")
    
    freq_loyalty.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv(f"{output_base}/freq_loyalty")
    print("✓ Wrote loyalty status frequencies")
    
    freq_region.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv(f"{output_base}/freq_region")
    print("✓ Wrote regional frequencies")
    
    # Write top spenders
    top_spenders.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv(f"{output_base}/top_spenders")
    print("✓ Wrote top spenders")
    
    # Write full cleaned dataset as Parquet (partitioned)
    df_clean.repartition(4, "product_category") \
        .write.mode("overwrite") \
        .partitionBy("product_category") \
        .parquet(f"{output_base}/customer_data_clean")
    print("✓ Wrote partitioned customer data (Parquet)")
    
    print("\n" + "=" * 70)
    print("PIPELINE COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    
    spark.stop()

if __name__ == "__main__":
    main()