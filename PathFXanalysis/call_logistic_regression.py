# written to call the logistic regression script with
# a gene-counting data file
# written 11-2-20 JLW

import pickle,os,csv

rdir = 'Gene_Counting_Results_110220/'
all_files = [] ## Need to fix this

#for gene_count_f in all_files:
for gene_count_f in ['Gene_counting_C0036341._merged.xlsx']:
	full_path = os.path.join(rdir,gene_count_f)
	cmd = "python run_logistic_regression.py -f %s"%(full_path)
	print(cmd)
	os.system(cmd)
