#!/usr/bin/awk -f
# Regional distribution and string pattern analysis
# Engineer 3 - Task 5

BEGIN { 
    FS = OFS = "\t" 
}

NR == 1 { next }

{
    region = $3
    amt = $4
    
    # Count by region
    region_count[region]++
    region_sum[region] += amt
    
    # Analyze region name length (string structure)
    len = length(region)
    if (len < 10) length_bucket = "SHORT"
    else if (len < 20) length_bucket = "MEDIUM"
    else length_bucket = "LONG"
    
    length_count[length_bucket]++
}

END {
    # Regional distribution
    print "Region\tCount\tAvgPurchase"
    for (r in region_count) {
        avg = region_sum[r] / region_count[r]
        printf "%s\t%d\t%.2f\n", r, region_count[r], avg
    }
    
    print ""
    
    # Region name length distribution
    print "NameLength\tCount"
    for (l in length_count) {
        print l, length_count[l]
    }
}