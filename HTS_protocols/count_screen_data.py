 # written 12-17-20 JLW to count drug
# compounds and normalized results

import pandas as pd
import os,csv,pickle
import matplotlib
matplotlib.use("AGG")
import matplotlib.pyplot as plt
from collections import defaultdict

rfile = 'Spark_MEGF10_qHTS_explained.xlsx'

lopac_res = pd.read_excel(rfile,sheet_name="LOPAC Results")
lopac_compounds = set(lopac_res["compound_NAME"].to_list())
drug_cat = dict(zip(lopac_res["Corp_ID"].to_list(),lopac_res["Comments"].to_list()))

count_cats = defaultdict(int)
for (dname,dstatus) in drug_cat.items():
	count_cats[dstatus]+=1
count_cats.pop(1)
count_cats.pop('Increase Cell Number?')

wd_df = pd.read_excel(rfile,sheet_name="Well Data")
lp_wd = wd_df[wd_df["Cpd Plate"].str.contains("LP")]
lp_doses = set(lp_wd["uM"].dropna().to_list())

bm_wd = wd_df[wd_df["Cpd Plate"].str.contains("MS")]	
bm_doses = set(bm_wd["uM"].dropna().to_list())

ms_res = pd.read_excel(rfile,sheet_name="MS_BM_Results")
msbm_comp = set(ms_res["MolName"].to_list())
msbm_cat = dict(zip(ms_res["Corp_ID"].to_list(),ms_res["Comments"].to_list()))

ms_cnt_cats = defaultdict(int)
for (dname,dstatus) in msbm_cat.items():
	ms_cnt_cats[dstatus]+=1

bar_labels = ['Inactive','Decrease Phagocytosis','Dec. Phag 20 uM','Increase Phagocytosis','Inc Phag 20 uM','Toxic','Possibly Toxic, Dec Phag','Toxic, Dec Phag']
plot_colors = {'Increase Phagocytosis':'red','Inc Phag 20 uM':'tomato','Dec. Phag 20 uM':'darkturquoise','Decrease Phagocytosis':'dodgerblue','Possibly Toxic, Dec Phag':'gold','Toxic':'gold','Toxic, Dec Phag':'gold'}
bar_colors = [plot_colors[bl] if bl in plot_colors else "lightgrey" for bl in bar_labels]
y_pos = range(len(bar_labels))

# plot bar charts counting categorized compounds
fig,ax_arr = plt.subplots(1,2,sharey=True)
for (i,(ddic,lib_nm)) in enumerate([(count_cats,"LOPAC"),(ms_cnt_cats,"MS BM")]):
	ax = ax_arr[i]
	y_height = [ddic[bl] for bl in bar_labels]
	rects = ax.barh(y_pos,y_height,color=bar_colors)
	ax_arr[0].set_xlabel("Number of compounds")
	ax.set_title(lib_nm)
	for rect, label in zip(rects,y_height):
		height = rect.get_height()
		ax.text(900,rect.get_y(),label,ha='center',va='bottom')
	
ax_arr[0].set_yticks(y_pos)
ax_arr[0].set_yticklabels(bar_labels)
plt.subplots_adjust(left=0.4)
plt.suptitle("Number of compounds in each category")
plt.savefig("Num_categorized_compounds.png",format="png")
		

# plot all dose response data?
drug_df = wd_df[wd_df["Well type"]=="Data"]
dr_doses = defaultdict(list)
for (sid,ddose,normp) in zip(drug_df["STF_ID"].to_list(),drug_df["uM"].to_list(),drug_df["% Pos W2/W1"].to_list()):
	dr_doses[sid].append((ddose,normp)) 

fig,ax = plt.subplots()
for (dname,plot_data) in dr_doses.items():
	if dname in drug_cat:
		drug_status = drug_cat[dname]
	elif dname in msbm_cat:
		drug_status = msbm_cat[dname]
	else:
		drug_status = 'Inactive'
	if drug_status in plot_colors:
		plotc = plot_colors[drug_status]
	else:
		plotc = 'lightgrey'
	plot_data = sorted(plot_data,key = lambda x: x[0])
	(x,y) = zip(*plot_data)
	n = ax.semilogx(x,y,color=plotc, alpha = 0.25, linewidth=0.5)
ax.set_xlabel("Compound dose (uM)")
doses = x
ax.set_xticks(x)
ax.set_xticklabels(doses)
ax.set_ylabel("Normalized phagocytosis")
ax.set_yticks([1.0,10,50.0])
ax.set_ylim([0,50])
ax.set_title("Normalized phagocytosis across compound libraries")
plt.savefig("all_normalized_dose_response.png",format="png")


