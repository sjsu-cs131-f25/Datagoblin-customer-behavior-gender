# datagoblin-customer-behavior-gender

Gender Differences in Customer Shopping Patterns
- Nathan - Product Manager
- Hnin Lei Yee - Data Engineer
- Win Thurain Lin - Data Engineer
- Ni Shinn Thant - Data Engineer
- Ryan Kyaw - Data Storyteller
## Data Card

**Source:** [Kaggle - Customer Purchases Behaviour Dataset](https://www.kaggle.com/datasets/sanyamgoyal401/customer-purchases-behaviour-dataset)

**Description:** Simulated customer purchase behavior data, including demographics, purchase amounts, product categories, and shopping patterns

**Format:**
- File type: CSV (comma-delimited)
- Encoding: UTF-8
- Compression: None
- Size: ~7.7 MB
- Rows: 100,001 (1 header + 100,000 data records)
- Columns: 12

**Fields:**
- id, age, gender, income, education, region, loyalty_status
- purchase_frequency, purchase_amount, product_category
- promotion_usage, satisfaction_score

**Delimiter:** Comma (`,`)  
**Header:** Present in row 1  

**Quality Notes:**
- Complete dataset with no missing values
- Product categories: Electronics, Clothing, Books, Food, Health, Home, Beauty
- Simulated data (not real customer transactions)
- No temporal fields (dates/timestamps)

## How to Run
```bash
./scripts/run_project2.sh data/customer_data.csv
