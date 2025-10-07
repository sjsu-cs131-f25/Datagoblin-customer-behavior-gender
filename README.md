```bash
./run_project3.sh data/customer_data.csv
Outputs Generated
The script creates 11 deliverable files:
Edge Files:

edges.tsv - 100,000 customer-category relationships
entity_counts.tsv - Frequency count for each category (7 categories)
edges_thresholded.tsv - Edges after threshold filtering

Cluster Analysis:

cluster_sizes.tsv - Size of each cluster (sorted)
cluster_histogram.png - Bar chart of customer distribution by category

Top-30 Analysis:

top30_clusters.txt - 30 most frequent customers in filtered clusters
top30_overall.txt - 30 most frequent customers overall
diff_top30.txt - Differences between the two lists

Network Visualization:

viz_edges.tsv - 500 sample edges from largest cluster (Electronics)
cluster_viz.png - Network diagram showing hub-and-spoke structure

Statistics:

cluster_outcomes.tsv - Summary statistics (count, mean, median, min, max) by category

Requirements

UNIX/Linux environment
Standard tools: cut, sort, uniq, awk, join, tr
gnuplot (for visualizations)
datamash (for statistics)

Team Roles (Sprint 3)

PM: Ni Shinn Thant - Sprint coordination, quality gates
Eng 1: Nathan Jang - Edge extraction, entity counting
Eng 2: Ryan Kyaw - Cluster analysis, Top-30 comparison
Eng 3: Ivy Yee - Network visualization, summary statistics
Data Storyteller: Win Thurain Lin - Report writing, insights
Repository
https://github.com/sjsu-cs131-f25/Datagoblin-customer-behavior-gender
