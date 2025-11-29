"""
CS 131 Final Sprint - ML Customer Segmentation
Team: Datagoblin | Engineer 2: Machine Learning
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.ml.feature import VectorAssembler, StandardScaler
from pyspark.ml.clustering import KMeans
from pyspark.ml.evaluation import ClusteringEvaluator

def main():
    print("=" * 70)
    print("ML CUSTOMER SEGMENTATION - K-MEANS CLUSTERING")
    print("=" * 70)
    
    spark = SparkSession.builder \
        .appName("Datagoblin-ML-Segmentation") \
        .config("spark.sql.shuffle.partitions", "8") \
        .getOrCreate()
    
    # Load cleaned data
    df = spark.read.parquet("gs://datagoblin-customer-behavior/output/customer_data_clean")
    
    print(f"\nDataset: {df.count():,} customers")
    
    # FEATURE ENGINEERING
    print("\n[1/5] Feature Engineering...")
    print("-" * 70)
    
    # Convert ALL categorical features to numeric
    df_encoded = df.withColumn(
        'loyalty_numeric',
        when(col('loyalty_status') == 'Gold', 3)
        .when(col('loyalty_status') == 'Silver', 2)
        .otherwise(1)
    ).withColumn(
        'region_numeric',
        when(col('region') == 'North', 1)
        .when(col('region') == 'South', 2)
        .when(col('region') == 'East', 3)
        .otherwise(4)
    ).withColumn(
        'category_numeric',
        when(col('product_category') == 'Electronics', 7)
        .when(col('product_category') == 'Clothing', 6)
        .when(col('product_category') == 'Books', 5)
        .when(col('product_category') == 'Food', 4)
        .when(col('product_category') == 'Health', 3)
        .when(col('product_category') == 'Home', 2)
        .otherwise(1)
    ).withColumn(
        'frequency_numeric',
        when(col('purchase_frequency') == 'Weekly', 4)
        .when(col('purchase_frequency') == 'Bi-Weekly', 3)
        .when(col('purchase_frequency') == 'Monthly', 2)
        .otherwise(1)
    )
    
    # Select features for clustering
    feature_cols = [
        'age', 'income', 'purchase_amount', 'satisfaction_score',
        'frequency_numeric', 'loyalty_numeric', 'region_numeric', 'category_numeric'
    ]
    
    # Assemble features
    assembler = VectorAssembler(
        inputCols=feature_cols,
        outputCol="features_raw"
    )
    
    df_features = assembler.transform(df_encoded)
    
    # Scale features
    scaler = StandardScaler(
        inputCol="features_raw",
        outputCol="features",
        withStd=True,
        withMean=True
    )
    
    scaler_model = scaler.fit(df_features)
    df_scaled = scaler_model.transform(df_features)
    
    print("✓ Features prepared and scaled")
    
    # FIND OPTIMAL K
    print("\n[2/5] Finding Optimal Number of Clusters...")
    print("-" * 70)
    
    costs = []
    K_range = range(2, 7)
    
    for k in K_range:
        kmeans = KMeans(featuresCol="features", k=k, seed=42, maxIter=20)
        model = kmeans.fit(df_scaled)
        cost = model.summary.trainingCost
        costs.append((k, cost))
        print(f"K={k}: Cost = {cost:.2f}")
    
    print("\n✓ Selecting K=4 for customer segmentation")
    
    # TRAIN K-MEANS MODEL
    print("\n[3/5] Training K-Means Model (K=4)...")
    print("-" * 70)
    
    kmeans = KMeans(featuresCol="features", k=4, seed=42, maxIter=30)
    model = kmeans.fit(df_scaled)
    
    predictions = model.transform(df_scaled)
    
    evaluator = ClusteringEvaluator(featuresCol="features")
    silhouette = evaluator.evaluate(predictions)
    
    print(f"✓ Model trained successfully")
    print(f"✓ Silhouette Score: {silhouette:.4f}")
    
    # ANALYZE SEGMENTS
    print("\n[4/5] Analyzing Customer Segments...")
    print("-" * 70)
    
    segments = predictions.select('id', 'prediction').join(df, 'id')
    segments = segments.withColumnRenamed('prediction', 'segment')
    
    # Analyze each segment
    segment_profiles = segments.groupBy('segment') \
        .agg(
            count('*').alias('customer_count'),
            avg('age').alias('avg_age'),
            avg('income').alias('avg_income'),
            avg('purchase_amount').alias('avg_purchase'),
            avg('satisfaction_score').alias('avg_satisfaction')
        ) \
        .orderBy('segment')
    
    print("\nSegment Profiles:")
    segment_profiles.show(truncate=False)
    
    # SEGMENT PERSONAS
    print("\n" + "=" * 70)
    print("SEGMENT PERSONAS")
    print("=" * 70)
    
    segment_data = segment_profiles.collect()
    
    for row in segment_data:
        segment_id = row['segment']
        
        # Determine persona name based on characteristics
        avg_purchase = row['avg_purchase']
        avg_income = row['avg_income']
        
        if avg_purchase > 7000 and avg_income > 75000:
            persona = "High-Value VIPs"
        elif avg_purchase > 5000:
            persona = "Premium Buyers"
        elif avg_income < 50000:
            persona = "Budget Shoppers"
        else:
            persona = "Loyal Regulars"
        
        print(f"\n📊 SEGMENT {segment_id}: {persona}")
        print("-" * 70)
        print(f"Size: {row['customer_count']:,} customers ({row['customer_count']/100000*100:.1f}%)")
        print(f"Demographics:")
        print(f"  - Avg Age: {row['avg_age']:.1f} years")
        print(f"  - Avg Income: ${row['avg_income']:,.0f}")
        print(f"Behavior:")
        print(f"  - Avg Purchase: ${row['avg_purchase']:,.2f}")
        print(f"  - Satisfaction: {row['avg_satisfaction']:.2f}/7")
    
    # SAVE RESULTS
    print("\n[5/5] Saving Segmentation Results...")
    print("-" * 70)
    
    # Save segment assignments
    segments.select(
        'id', 'segment', 'age', 'income', 'purchase_amount',
        'loyalty_status', 'region', 'product_category'
    ).coalesce(4).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/ml_segmentation/customer_segments")
    
    print("✓ Customer segments saved")
    
    # Save segment profiles
    segment_profiles.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/ml_segmentation/segment_profiles")
    
    print("✓ Segment profiles saved")
    
    print("\n" + "=" * 70)
    print("ML SEGMENTATION COMPLETE!")
    print("Location: gs://datagoblin-customer-behavior/output/ml_segmentation/")
    print("=" * 70)
    
    spark.stop()

if __name__ == "__main__":
    main()