#!/bin/bash
# Create histogram with proper binning

# Method 1: Use gnuplot's binning feature
cat > ~/plot_histogram_binned.gp << 'GNUPLOT_EOF'
set terminal png size 800,600
set output '/mnt/scratch/CS131_jelenag/students/ryank/cluster_histogram_fixed.png'

# Define bin width and function
binwidth = 5000
bin(x,width) = width*floor(x/width) + binwidth/2.0

# Set up histogram style
set style fill solid 0.7 border -1
set boxwidth binwidth*0.9

# Labels and title
set xlabel "Cluster Size (Number of Customers)"
set ylabel "Number of Product Categories"
set title "Distribution of Customer Cluster Sizes (Binned by 5000)"
set grid ytics

# Use smooth frequency to create histogram bins
plot '/mnt/scratch/CS131_jelenag/students/ryank/cluster_sizes.tsv' \
     using (bin($2,binwidth)):(1.0) smooth freq with boxes \
     linecolor rgb "steelblue" notitle
GNUPLOT_EOF

gnuplot ~/plot_histogram_binned.gp
echo "Fixed histogram saved: ~/cluster_histogram_fixed.png"
ls -lh ~/cluster_histogram_fixed.png
