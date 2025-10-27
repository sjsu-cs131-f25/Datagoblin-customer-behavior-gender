#!/usr/bin/awk -f
# Outlier detection and satisfaction signals
# Engineer 3 - Task 6

BEGIN { 
    FS = OFS = "\t" 
}

NR == 1 { next }

{
    id = $1
    amt = $4
    category = $5
    satisfaction = $6
    
    # Store data
    amounts[NR] = amt
    ids[NR] = id
    categories[NR] = category
    
    sum += amt
    count++
    
    # Track satisfaction by category
    cat_satisfaction_sum[category] += satisfaction
    cat_satisfaction_count[category]++
}

END {
    # Calculate mean and std dev
    mean = sum / count
    
    for (i in amounts) {
        diff = amounts[i] - mean
        sq_sum += diff * diff
    }
    std = sqrt(sq_sum / count)
    threshold = mean + (2 * std)
    
    # Find outliers (high-value customers)
    print "CustomerID\tPurchaseAmount\tCategory"
    for (i in amounts) {
        if (amounts[i] > threshold) {
            printf "%s\t%.2f\t%s\n", ids[i], amounts[i], categories[i]
        }
    }
    
    print ""
    
    # Category satisfaction signals
    print "Category\tAvgSatisfaction"
    for (c in cat_satisfaction_count) {
        avg_sat = cat_satisfaction_sum[c] / cat_satisfaction_count[c]
        printf "%s\t%.2f\n", c, avg_sat
    }
}