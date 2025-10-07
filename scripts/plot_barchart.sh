#!/bin/bash
cat > ~/plot_bars.gp << 'GNUPLOT_EOF'
set terminal png size 1000,600 font "Arial,12"
set output '/mnt/scratch/CS131_jelenag/students/ryank/cluster_barchart.png'
set style data histogram
set style histogram cluster gap 1
set style fill solid 0.7 border -1
set boxwidth 0.9
set xlabel "Product Category" font "Arial,14"
set ylabel "Number of Customers" font "Arial,14"
set title "Customer Distribution by Product Category" font "Arial,16"
set xtics rotate by -45 scale 0 font "Arial,11"
set grid ytics linewidth 1
plot '/mnt/scratch/CS131_jelenag/students/ryank/cluster_sizes.tsv' using 2:xtic(1) title "Customers" linecolor rgb "steelblue"
GNUPLOT_EOF
gnuplot ~/plot_bars.gp
echo "Done"
