"""
CS 131 Final Sprint - Data Visualizations
Team: Datagoblin | Engineer 2: Visualizations
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 6)

def main():
    print("=" * 70)
    print("GENERATING VISUALIZATIONS FROM AGGREGATED DATA")
    print("=" * 70)
    
    spark = SparkSession.builder \
        .appName("Datagoblin-Visualizations") \
        .getOrCreate()
    
    # Load cleaned data
    df = spark.read.parquet("gs://datagoblin-customer-behavior/output/customer_data_clean")
    
    # VIZ 1: SPENDING BY AGE GROUP
    print("\n[1/6] Creating Age Group Spending Chart...")
    
    df_age_groups = df.withColumn(
        'age_group',
        when(col('age') < 25, '18-24')
        .when(col('age') < 35, '25-34')
        .when(col('age') < 50, '35-49')
        .otherwise('50+')
    )
    
    age_spending = df_age_groups.groupBy('age_group') \
        .agg(avg('purchase_amount').alias('avg_spending')) \
        .orderBy('age_group') \
        .toPandas()
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(age_spending['age_group'], age_spending['avg_spending'], 
                   color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728'])
    plt.title('Average Customer Spending by Age Group', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Age Group', fontsize=12)
    plt.ylabel('Average Purchase Amount ($)', fontsize=12)
    plt.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for i, (idx, row) in enumerate(age_spending.iterrows()):
        plt.text(i, row['avg_spending'] + 200, f"${row['avg_spending']:,.0f}", 
                ha='center', va='bottom', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/tmp/viz1_age_spending.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz1_age_spending.png")
    plt.close()
    
    # VIZ 2: LOYALTY STATUS DISTRIBUTION
    print("[2/6] Creating Loyalty Distribution Chart...")
    
    loyalty_dist = df.groupBy('loyalty_status') \
        .count() \
        .orderBy(desc('count')) \
        .toPandas()
    
    plt.figure(figsize=(8, 8))
    colors = ['#FFD700', '#C0C0C0', '#4169E1']  # Gold, Silver, Blue
    explode = (0.05, 0.05, 0.05)
    
    plt.pie(loyalty_dist['count'], labels=loyalty_dist['loyalty_status'], 
            autopct='%1.1f%%', startangle=90, colors=colors, explode=explode,
            textprops={'fontsize': 12, 'fontweight': 'bold'})
    plt.title('Customer Distribution by Loyalty Status', fontsize=16, fontweight='bold', pad=20)
    plt.axis('equal')
    plt.tight_layout()
    plt.savefig('/tmp/viz2_loyalty_distribution.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz2_loyalty_distribution.png")
    plt.close()
    
    # VIZ 3: PRODUCT CATEGORY REVENUE
    print("[3/6] Creating Category Revenue Chart...")
    
    category_revenue = df.groupBy('product_category') \
        .agg(sum('purchase_amount').alias('total_revenue')) \
        .orderBy(desc('total_revenue')) \
        .toPandas()
    
    plt.figure(figsize=(12, 6))
    bars = plt.barh(category_revenue['product_category'], 
                    category_revenue['total_revenue'], 
                    color=sns.color_palette('viridis', len(category_revenue)))
    plt.title('Total Revenue by Product Category', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Total Revenue ($)', fontsize=12)
    plt.ylabel('Product Category', fontsize=12)
    plt.grid(axis='x', alpha=0.3)
    
    # Add value labels
    for i, (idx, row) in enumerate(category_revenue.iterrows()):
        plt.text(row['total_revenue'] + 50000, i, 
                f"${row['total_revenue']/1000000:.1f}M", 
                va='center', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/tmp/viz3_category_revenue.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz3_category_revenue.png")
    plt.close()
    
    # VIZ 4: INCOME VS SPENDING SCATTER
    print("[4/6] Creating Income vs Spending Scatter Plot...")
    
    # Sample 10% for visualization
    sample_data = df.sample(fraction=0.1, seed=42).toPandas()
    
    plt.figure(figsize=(10, 6))
    
    for loyalty in ['Gold', 'Silver', 'Regular']:
        subset = sample_data[sample_data['loyalty_status'] == loyalty]
        plt.scatter(subset['income'], subset['purchase_amount'], 
                   label=loyalty, alpha=0.6, s=50)
    
    plt.title('Income vs Purchase Amount by Loyalty Status', 
              fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Annual Income ($)', fontsize=12)
    plt.ylabel('Purchase Amount ($)', fontsize=12)
    plt.legend(title='Loyalty Status', fontsize=10)
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig('/tmp/viz4_income_spending.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz4_income_spending.png")
    plt.close()
    
    # VIZ 5: SATISFACTION BY REGION
    print("[5/6] Creating Regional Satisfaction Chart...")
    
    region_satisfaction = df.groupBy('region') \
        .agg(
            avg('satisfaction_score').alias('avg_satisfaction'),
            count('*').alias('customer_count')
        ) \
        .orderBy(desc('avg_satisfaction')) \
        .toPandas()
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(region_satisfaction['region'], 
                   region_satisfaction['avg_satisfaction'],
                   color=['#2ca02c', '#ff7f0e', '#d62728', '#1f77b4'])
    plt.title('Average Satisfaction Score by Region', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Region', fontsize=12)
    plt.ylabel('Average Satisfaction Score', fontsize=12)
    plt.ylim(0, 7)
    plt.grid(axis='y', alpha=0.3)
    
    # Add labels with count
    for i, (idx, row) in enumerate(region_satisfaction.iterrows()):
        plt.text(i, row['avg_satisfaction'] + 0.15, 
                f"{row['avg_satisfaction']:.2f}\n(n={row['customer_count']:,})", 
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/tmp/viz5_region_satisfaction.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz5_region_satisfaction.png")
    plt.close()
    
    # VIZ 6: PURCHASE FREQUENCY DISTRIBUTION
    print("[6/6] Creating Purchase Frequency Chart...")
    
    freq_dist = df.groupBy('purchase_frequency') \
        .agg(
            count('*').alias('customers'),
            avg('purchase_amount').alias('avg_amount')
        ) \
        .toPandas()
    
    # Create grouped bar chart
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    x = range(len(freq_dist))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], freq_dist['customers'], 
            width, label='Customer Count', color='#1f77b4')
    ax1.set_xlabel('Purchase Frequency', fontsize=12)
    ax1.set_ylabel('Number of Customers', fontsize=12, color='#1f77b4')
    ax1.tick_params(axis='y', labelcolor='#1f77b4')
    ax1.set_xticks(x)
    ax1.set_xticklabels(freq_dist['purchase_frequency'])
    
    ax2 = ax1.twinx()
    ax2.bar([i + width/2 for i in x], freq_dist['avg_amount'], 
            width, label='Avg Purchase', color='#ff7f0e')
    ax2.set_ylabel('Average Purchase Amount ($)', fontsize=12, color='#ff7f0e')
    ax2.tick_params(axis='y', labelcolor='#ff7f0e')
    
    plt.title('Purchase Frequency: Customer Count vs Average Spending', 
              fontsize=16, fontweight='bold', pad=20)
    fig.legend(loc='upper right', bbox_to_anchor=(0.9, 0.9))
    plt.tight_layout()
    plt.savefig('/tmp/viz6_purchase_frequency.png', dpi=300, bbox_inches='tight')
    print("✓ Created: viz6_purchase_frequency.png")
    plt.close()
    
    # UPLOAD TO GCS
    print("\nUploading visualizations to Cloud Storage...")
    
    import subprocess
    
    viz_files = [
        'viz1_age_spending.png',
        'viz2_loyalty_distribution.png',
        'viz3_category_revenue.png',
        'viz4_income_spending.png',
        'viz5_region_satisfaction.png',
        'viz6_purchase_frequency.png'
    ]
    
    for viz_file in viz_files:
        subprocess.run([
            'gsutil', 'cp', f'/tmp/{viz_file}',
            'gs://datagoblin-customer-behavior/output/visualizations/'
        ])
        print(f"✓ Uploaded: {viz_file}")
    
    print("\n" + "=" * 70)
    print("ALL VISUALIZATIONS COMPLETE!")
    print("Location: gs://datagoblin-customer-behavior/output/visualizations/")
    print("=" * 70)
    
    spark.stop()

if __name__ == "__main__":
    main()