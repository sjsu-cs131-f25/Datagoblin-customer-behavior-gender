#!/usr/bin/awk -f
# Purchase amount buckets and per-category summaries
# Engineer 2 - Task 4

BEGIN { FS = OFS = "\t" }

NR == 1 { next }

{
    amt = $4
    category = $5
    
    # Bucket purchase amounts (guard against zero division)
    if (amt == 0) bucket = "ZERO"
    else if (amt < 5000) bucket = "LOW"
    else if (amt < 15000) bucket = "MID"
    else bucket = "HIGH"
    
    bucket_count[bucket]++
    
    # Per-category aggregation
    cat_sum[category] += amt
    cat_count[category]++
    
    if (amt > cat_max[category] || cat_max[category] == "") 
        cat_max[category] = amt
    if (amt < cat_min[category] || cat_min[category] == "") 
        cat_min[category] = amt
}

END {
    # Bucket distribution
    print "Bucket\tCount\tPercentage"
    total = 0
    for (b in bucket_count) total += bucket_count[b]
    
    # Guard against division by zero
    if (total > 0) {
        for (b in bucket_count) {
            pct = (bucket_count[b] / total) * 100
            printf "%s\t%d\t%.2f\n", b, bucket_count[b], pct
        }
    }
    
    print ""
    
    # Per-category summary with guards
    print "Category\tCount\tAvgAmount\tMinAmount\tMaxAmount"
    for (c in cat_count) {
        avg = (cat_count[c] > 0) ? cat_sum[c] / cat_count[c] : 0
        printf "%s\t%d\t%.2f\t%.2f\t%.2f\n", c, cat_count[c], avg, cat_min[c], cat_max[c]
    }
}
