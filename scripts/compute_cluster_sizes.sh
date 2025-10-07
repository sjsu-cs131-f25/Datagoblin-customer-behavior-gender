echo "Computing cluster sizes from thresholded edges..."

# For each product category, count how many customers it has
cut -f1 out/edges_thresholded.tsv | sort | uniq -c | \
  awk '{print $2"\t"$1}' | sort -k2,2n > out/cluster_sizes.tsv

# Verify output
echo "Cluster size statistics:"
echo "Total clusters: $(wc -l < out/cluster_sizes.tsv)"
echo "Smallest cluster: $(cut -f2 out/cluster_sizes.tsv | sort -n | head -1)"
echo "Largest cluster: $(cut -f2 out/cluster_sizes.tsv | sort -n | tail -1)"

# Show the clusters
echo ""
echo "All cluster sizes:"
cat out/cluster_sizes.tsv
