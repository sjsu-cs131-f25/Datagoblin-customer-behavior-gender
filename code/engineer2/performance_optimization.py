"""
CS 131 Final Sprint - Performance Optimization
Team: Datagoblin | Engineer 2: Performance Testing
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time

def run_aggregation_test(spark, df, num_partitions, test_name):
    """Run aggregation with specific shuffle partition setting"""
    
    print(f"\n{'='*60}")
    print(f"Test: {test_name}")
    print(f"Shuffle Partitions: {num_partitions}")
    print(f"{'='*60}")
    
    # Set shuffle partitions
    spark.conf.set("spark.sql.shuffle.partitions", str(num_partitions))
    
    start_time = time.time()
    
    # Complex aggregation (similar to your analysis)
    result = df.groupBy('region', 'product_category', 'loyalty_status') \
        .agg(
            count('*').alias('count'),
            avg('purchase_amount').alias('avg_amount'),
            sum('purchase_amount').alias('total_revenue'),
            avg('satisfaction_score').alias('avg_satisfaction')
        ) \
        .orderBy(desc('total_revenue'))
    
    # Force evaluation
    count_result = result.count()
    
    duration = time.time() - start_time
    
    print(f"Results: {count_result} groups")
    print(f"Duration: {duration:.2f} seconds")
    print(f"{'='*60}\n")
    
    return duration, count_result

def main():
    print("=" * 70)
    print("PERFORMANCE OPTIMIZATION EXPERIMENTS")
    print("=" * 70)
    
    spark = SparkSession.builder \
        .appName("Datagoblin-Performance-Optimization") \
        .getOrCreate()
    
    # Load cleaned data
    input_path = "gs://datagoblin-customer-behavior/output/customer_data_clean"
    df = spark.read.parquet(input_path)
    
    print(f"\nDataset: {df.count():,} rows")
    
    # Cache data to ensure consistent testing
    df.cache()
    df.count()  # Force cache
    
    print("\nRunning performance tests with different shuffle partition settings...")
    
    # Store results
    results = {}
    
    # Test 1: Very few partitions
    duration, count = run_aggregation_test(spark, df, 2, "Very Few Partitions (2)")
    results['2_partitions'] = duration
    
    # Test 2: Default setting
    duration, count = run_aggregation_test(spark, df, 8, "Default (8)")
    results['8_partitions'] = duration
    
    # Test 3: More parallelism
    duration, count = run_aggregation_test(spark, df, 16, "More Parallelism (16)")
    results['16_partitions'] = duration
    
    # Test 4: Many partitions
    duration, count = run_aggregation_test(spark, df, 32, "Many Partitions (32)")
    results['32_partitions'] = duration
    
    # Test 5: Too many partitions
    duration, count = run_aggregation_test(spark, df, 64, "Too Many Partitions (64)")
    results['64_partitions'] = duration
    
    # SUMMARY
    print("\n" + "=" * 70)
    print("PERFORMANCE SUMMARY")
    print("=" * 70)
    
    # Sort by duration
    sorted_results = sorted(results.items(), key=lambda x: x[1])
    
    print("\nRanked by Speed (Fastest to Slowest):")
    print("-" * 70)
    for i, (config, duration) in enumerate(sorted_results, 1):
        print(f"{i}. {config:25s}: {duration:6.2f}s")
    
    # Find optimal
    optimal = sorted_results[0]
    print(f"\n✓ Optimal configuration: {optimal[0]} ({optimal[1]:.2f}s)")
    
    # Calculate improvement
    worst = sorted_results[-1]
    improvement = ((worst[1] - optimal[1]) / worst[1]) * 100
    print(f"✓ Performance improvement: {improvement:.1f}% faster than worst config")
    
    # Save results summary
    print("\nSaving performance results...")
    
    # Create results DataFrame
    results_data = [(k, v) for k, v in sorted_results]
    results_df = spark.createDataFrame(results_data, ["configuration", "duration_seconds"])
    
    results_df.coalesce(1).write.mode("overwrite") \
        .option("header", "true") \
        .csv("gs://datagoblin-customer-behavior/output/performance_results")
    
    print("✓ Results saved to gs://datagoblin-customer-behavior/output/performance_results/")
    
    print("\n" + "=" * 70)
    print("PERFORMANCE OPTIMIZATION COMPLETE!")
    print("=" * 70)
    
    spark.stop()

if __name__ == "__main__":
    main()