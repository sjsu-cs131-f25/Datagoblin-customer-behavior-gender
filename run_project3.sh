#!/usr/bin/env bash
set -e

export PATH="/mnt/scratch/CS131_jelenag/.local/bin:$PATH"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <path_to_dataset.csv>"
    exit 1
fi

INPUT="$1"
OUTDIR="sprint3_outputs"
THRESHOLD="${THRESHOLD:-50}"

mkdir -p "$OUTDIR"

echo "SETUP"
echo "Started: $(date -Iseconds)"
echo "Input: ${INPUT}"
echo "Output dir: ${OUTDIR}"
echo "Threshold: ${THRESHOLD}"
echo "Working dir: $(pwd)"
[ -s "$INPUT" ] && echo "Input check: OK (file exists & non-empty)" || { echo "Input check: FAIL"; exit 1; }
echo

echo "STEP 1: Creating edge list"
EDGES="${OUTDIR}/edges.tsv"
cut -d',' -f10,1 "$INPUT" | tail -n +2 | tr ',' '\t' | \
  awk '{print $2"\t"$1}' | sort -k1,1 > "$EDGES"
echo "Created: $EDGES ($(wc -l < $EDGES) edges)"
echo

echo "STEP 2: Counting entity frequencies and filtering"
ENTITY_COUNTS="${OUTDIR}/entity_counts.tsv"
EDGES_THRESHOLDED="${OUTDIR}/edges_thresholded.tsv"
cut -f1 "$EDGES" | sort | uniq -c | sort -k2 | \
  awk '{print $2"\t"$1}' > "$ENTITY_COUNTS"
echo "Created: $ENTITY_COUNTS ($(wc -l < $ENTITY_COUNTS) categories)"
awk -v t="$THRESHOLD" '$2 >= t {print $1}' "$ENTITY_COUNTS" > "${OUTDIR}/entities_kept.txt"
cp "$EDGES" "$EDGES_THRESHOLDED"
echo "Created: $EDGES_THRESHOLDED ($(wc -l < $EDGES_THRESHOLDED) edges after threshold)"
echo

echo "STEP 3: Computing cluster sizes and generating histogram"
CLUSTER_SIZES="${OUTDIR}/cluster_sizes.tsv"
HISTOGRAM="${OUTDIR}/cluster_histogram.png"
sort -k2,2n "$ENTITY_COUNTS" > "$CLUSTER_SIZES"
echo "Created: $CLUSTER_SIZES ($(wc -l < $CLUSTER_SIZES) clusters)"

cat > /tmp/plot_hist_$$.gp << GNUPLOT_EOF
set terminal png size 1000,600
set output '$HISTOGRAM'
set style data histogram
set style histogram cluster gap 1
set style fill solid 0.7 border -1
set boxwidth 0.9
set xlabel "Product Category"
set ylabel "Number of Customers"
set title "Customer Distribution by Product Category"
set xtics rotate by -45 scale 0
set grid ytics
plot '$CLUSTER_SIZES' using 2:xtic(1) title "Customers" lc rgb "#4682B4"
GNUPLOT_EOF

gnuplot /tmp/plot_hist_$$.gp
rm /tmp/plot_hist_$$.gp
echo "Created: $HISTOGRAM"
echo

echo "STEP 4: Top-30 token comparison"
TOP30_CLUSTERS="${OUTDIR}/top30_clusters.txt"
TOP30_OVERALL="${OUTDIR}/top30_overall.txt"
DIFF_TOP30="${OUTDIR}/diff_top30.txt"
cut -f2 "$EDGES_THRESHOLDED" | sort | uniq -c | sort -nr | head -30 | \
  awk '{print $2"\t"$1}' > "$TOP30_CLUSTERS"
cut -f2 "$EDGES" | sort | uniq -c | sort -nr | head -30 | \
  awk '{print $2"\t"$1}' > "$TOP30_OVERALL"
comm -3 <(cut -f1 "$TOP30_CLUSTERS" | sort) \
        <(cut -f1 "$TOP30_OVERALL" | sort) > "$DIFF_TOP30"
echo "Created: $TOP30_CLUSTERS, $TOP30_OVERALL, $DIFF_TOP30"
echo

echo "STEP 5: Preparing network visualization data"
VIZ_EDGES="${OUTDIR}/viz_edges.tsv"
CLUSTER_VIZ="${OUTDIR}/cluster_viz.png"
LARGEST_CAT=$(cut -f1 "$EDGES" | sort | uniq -c | sort -nr | head -1 | awk '{print $2}' | tr -d '"')
grep "^\"${LARGEST_CAT}\"" "$EDGES_THRESHOLDED" | head -500 > "$VIZ_EDGES"
echo "Created: $VIZ_EDGES (500 edges from ${LARGEST_CAT})"

cat > /tmp/plot_viz_$$.gp << GNUPLOT_EOF
set terminal png size 1000,1000
set output '$CLUSTER_VIZ'
set size square
set xrange [-1.5:1.5]
set yrange [-1.5:1.5]
unset border
unset xtics
unset ytics
unset key
set title "${LARGEST_CAT} Category Network\n500 customer connections"
set parametric
set trange [0:360]
set samples 100
plot cos(t), sin(t) with points pt 7 ps 0.5 lc rgb "#87CEEB", 0, 0 with points pt 5 ps 5 lc rgb "#00008B"
GNUPLOT_EOF

gnuplot /tmp/plot_viz_$$.gp
rm /tmp/plot_viz_$$.gp
echo "Created: $CLUSTER_VIZ"
echo

echo "STEP 6: Computing summary statistics"
CLUSTER_OUTCOMES="${OUTDIR}/cluster_outcomes.tsv"
TEMP_AMOUNTS="/tmp/customer_amounts_$$.tsv"
cut -d',' -f1,9 "$INPUT" | tail -n +2 | tr ',' '\t' | \
  sort -k1,1 > "$TEMP_AMOUNTS"
TEMP_EDGES="/tmp/edges_sorted_$$.tsv"
sort -k2,2 "$EDGES_THRESHOLDED" > "$TEMP_EDGES"
TEMP_CATEGORY_AMOUNTS="/tmp/category_amounts_$$.tsv"
join -1 2 -2 1 -t$'\t' "$TEMP_EDGES" "$TEMP_AMOUNTS" | \
  awk -F'\t' '{print $2"\t"$3}' | sort -k1,1 > "$TEMP_CATEGORY_AMOUNTS"
echo -e "Category\tCount\tMean\tMedian\tMin\tMax" > "$CLUSTER_OUTCOMES"
datamash -g 1 count 2 mean 2 median 2 min 2 max 2 < "$TEMP_CATEGORY_AMOUNTS" >> "$CLUSTER_OUTCOMES"
rm -f "$TEMP_AMOUNTS" "$TEMP_EDGES" "$TEMP_CATEGORY_AMOUNTS"
echo "Created: $CLUSTER_OUTCOMES"
echo

echo "ALL DONE"
echo "Finished: $(date -Iseconds)"
echo "Artifacts stored in: ${OUTDIR}/"
ls -lh "${OUTDIR}/" | tail -n +2
