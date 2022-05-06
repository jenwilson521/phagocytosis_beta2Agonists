import pickle,os,csv

# Example scripting for running multiple drugs from DrugBank

analysis_name = 'PathFX_multiDrug_decrease_phagocytosis'

drug_list = ['DB00206''DB00257','DB00283','DB00450','DB00455','DB00472','DB00598','DB00602','DB00608','DB00623','DB00714',
'DB00836','DB00841','DB00866','DB00920','DB00938','DB00949','DB01118','DB01151','DB01200','DB01242','DB01388','DB02052',
'DB02587','DB03701','DB04209','DB04841','DB06266','DB07348','DB07352','DB07995','DB09202','DB11186','DB11937','DB11948','DB12551',
'DB12610','DB12783','DB12869','DB12890','DB13393','DB13520']

for drug_name in drug_list:
	### call the algorithm without phenotype clustering
	cmd = 'python phenotype_enrichment_pathway.py -d %s -a %s'%(drug_name,analysis_name)
	os.system(cmd)
