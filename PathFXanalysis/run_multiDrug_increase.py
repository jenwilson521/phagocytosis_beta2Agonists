
import pickle,os,csv

# Example scripting for running multiple drugs from DrugBank

analysis_name = 'PathFX_multiDrug_increase_phagocytosis'

drug_list = ['DB00280','DB00291','DB00328','DB00437','DB00544','DB00575','DB00594','DB00636','DB00747','DB00750','DB00765',
'DB00809','DB00839','DB00960','DB00982','DB00983','DB00996','DB01016','DB01050','DB01054','DB01064','DB01080','DB01177',
'DB01400','DB01412','DB01971','DB02116','DB02224','DB02959','DB02999','DB03953','DB04223','DB04224','DB04786','DB04819',
'DB05381','DB06693','DB06729','DB08849','DB09203','DB09242','DB11371','DB12110','DB12870','DB12947','DB13069','DB13100',
'DB13251','DB13601','DB14010','DB14043']

for drug_name in drug_list:
	### call the algorithm without phenotype clustering
	cmd = 'python phenotype_enrichment_pathway.py -d %s -a %s'%(drug_name,analysis_name)
	os.system(cmd)
