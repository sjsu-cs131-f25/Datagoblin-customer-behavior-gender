#!/usr/bin/awk -f
# Quality filters for customer shopping data
# Engineer 2 - Task 3

BEGIN {
    FS = OFS = "\t"
    print "id", "gender", "region", "purchase_amount", "product_category", "satisfaction_score"
}

NR == 1 { next }

# Business rules:
# - Customer ID not empty
# - Purchase amount > 0
# - Product category not empty
# - Satisfaction score valid (1-5)
$1 != "" && $1 != "NA" &&
$4 > 0 &&
$5 != "" && $5 != "NA" &&
$6 >= 1 && $6 <= 5 {
    print
}
