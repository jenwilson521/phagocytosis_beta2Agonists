# written to cluster drugs based on
# phenotype-associated genes
# written 7-30-20 JLW
# udpated 8-9-22 to improve heatmap figure colorbar

import pickle,os,csv,sys
import pandas as pd
import matplotlib
matplotlib.use("AGG")
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict
from matplotlib.colors import LinearSegmentedColormap

rdir = 'Gene_counting_results/'
df_excel_name = 'Gene_counting_C0036341.xlsx'

#Make three different dataframes 
multi_sheet_file = pd.ExcelFile(os.path.join(rdir,df_excel_name))
excel_sheet_names = multi_sheet_file.sheet_names

#Make data label dictionary
data_label_dic = {}

#Read each data sheet in to a dataframe and then concatenate. Store whether the drugs are increase, decrease, or no effect in a dictionary
color1 = 'magenta'
color2 = 'dodgerblue' 
color3 = 'darkviolet'


df1 = pd.read_excel(multi_sheet_file,'Increase', index_col=1,header=1)
df1_drugs = list(df1['Drug Bank ID'].to_list())
for drug_bank_id in df1_drugs:
    data_label_dic[drug_bank_id] = color1
df2 = pd.read_excel(multi_sheet_file,'Decrease',index_col = 1,header =1)
df2_drugs = list(df2['Drug Bank ID'].to_list())
for drug_bank_id in df2_drugs:
    data_label_dic[drug_bank_id] = color2
df3 = pd.read_excel(multi_sheet_file,'No Effect',index_col = 1,header=1)
df3_drugs = list(df3['Drug Bank ID'].to_list())
for drug_bank_id in df3_drugs:
    data_label_dic[drug_bank_id] = color3

#concatenate the dataframes
df = pd.concat([df1, df2,df3])

#make a list of the drugbank names
df_names = list(df.index)

# set index to DBIDs to match row colors
df = df.set_index('Drug Bank ID')

### WE MIGHT USE THIS IF THE GENE MATRIX IS TOO BIG ###
# only keep columns where genes are contained in at least 1 network
df = df.loc[:,(df.sum()>0)]
column_counts = df.sum(axis=0)

# create numpy array for use with scipy
data = df.loc[:, (df.columns != 'Drug Bank ID')]
print(data.head())

# format object for row colors
(dnames,dcolors) = zip(*[(k,v) for (k,v) in data_label_dic.items()])
rc_df = pd.DataFrame.from_dict({'Drugs': dnames,'Colors': dcolors})
rc_df = rc_df.set_index('Drugs')
# print(rc_df.head())

# formatting for better colorbar
myColors = ((0.0, 0.0, 0.0, 0.0), (0.6, 0.6, 0.6, 1.0))
cmap = LinearSegmentedColormap.from_list('Custom', myColors, len(myColors))

fig,ax = plt.subplots()
g = sns.clustermap(data,cmap=cmap,yticklabels=False,xticklabels=False,row_colors=rc_df)
g.cax.set_visible(False)

# colorbar = g.collections[0].colorbar
# colorbar = g.cax.colorbar
#colorbar.set_ticks([-1, 1])
#colorbar.set_ticklabels(['B', 'A', 'C'])
# print(pd.DataFrame(df.index.to_list())[0])

ax.set(xlabel= 'Network Proteins',ylabel='Drugs')
plt.savefig(os.path.join(rdir,'all_drugs_clustermap_090922.png'),format='png')


