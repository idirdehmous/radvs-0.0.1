#!/bin/bash 



data='/home/vhmod/mproj/epyg/tools/slo_data'


for dd  in {04..20} ; do  

for i in {01..23} ; do 

echo $dd$i


python  hdf5_plot.py -f    $data/$dd/PALI00_LJLM_201811${dd}${i}00_QUALITY.hdf  -n  12

mkdir -p  out/$dd
mv  *.png  out/$dd/VRAD_0.5_${i}.png 
done 
done 
