# written to cluster drugs based on
# phenotype-associated genes
# written 7-30-20 JLW

import pickle,os,csv,sys
import pandas as pd
import matplotlib
matplotlib.use("AGG")
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.cluster.hierarchy as sch
from sklearn.cluster import AgglomerativeClustering
from collections import defaultdict

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
df1_drugs = list(df1.index)
for drug_bank_id in df1_drugs:
    data_label_dic[drug_bank_id] = color1
df2 = pd.read_excel(multi_sheet_file,'Decrease',index_col = 1,header =1)
df2_drugs = list(df2.index)
for drug_bank_id in df2_drugs:
    data_label_dic[drug_bank_id] = color2
df3 = pd.read_excel(multi_sheet_file,'No effect',index_col = 1,header=1)
df3_drugs = list(df3.index)
for drug_bank_id in df3_drugs:
    data_label_dic[drug_bank_id] = color3


#concatenate the dataframes
df = pd.concat([df1, df2,df3])


# dropped row index values
df = df.drop(df.columns[0],axis=1)

#make a list of the drugbank names
df_names = list(df.index)

### WE MIGHT USE THIS IF THE GENE MATRIX IS TOO BIG ###
# after looking at the data it looks like ~396 columns have unique values at 51,61,71 etc.
df = df.loc[:,(df.sum()>0)]
column_counts = df.sum(axis=0)

# create numpy array for use with scipy
data = df.loc[:, (df.columns != 'Drug Bank ID')]
print(data.head())

### THIS WILL ONLY PLOT DRUGS IN THE INPUT DATA FRAME, WE MIGHT
### MODIFY IF WE WANT TO SEE INCREASE/DECREASE/NO-EFFECT ON
### THE SAME PLOT
# plot clustermap of all data
fig,ax = plt.subplots()
(dnames,dcolors) = zip(*[(k,v) for (k,v) in data_label_dic.items()])
rc_df = pd.DataFrame.from_dict({'Drugs': dnames,'Colors': dcolors})
rc_df = rc_df.set_index('Drugs')
row_colors = rc_df
print(rc_df.head())

#row_colors = pd.DataFrame(df.index.to_list())[0].map(data_label_dic)
print(row_colors)
g = sns.clustermap(data,cmap="mako",yticklabels=False,xticklabels=False,row_colors=row_colors)
print(pd.DataFrame(df.index.to_list())[0])
ax.set(xlabel= 'Genes present in > 60 networks',ylabel='Drugs')
plt.savefig(os.path.join(rdir,'all_drugs_clustermap.png'),format='png')

# method for separating clusters based on distance
def get_cluster_members(Z,all_names,dist_thr):
        cluster_members = defaultdict(list)
        total_rows = len(all_names)
        for (i,[idx1,idx2,idist,inum]) in enumerate(Z):
                idx1 = int(idx1)
                idx2 = int(idx2)
                if idist < dist_thr:
                        iter_num = i+total_rows
                        if idx1 < total_rows:
                                names1 = [all_names[idx1]]
                        else:
                                names1 = cluster_members.pop(idx1) # remove this cluster from final
                        if idx2 < total_rows:
                                names2 = [all_names[idx2]]
                        else:
                                names2 = cluster_members.pop(idx2) # remove this cluster from final
                        cluster_members[iter_num] = names1 + names2
        return cluster_members

# test out scipy linkage instead -- this worked better
Z = sch.linkage(data,'ward')
fig,ax = plt.subplots()
dn = sch.dendrogram(Z)
plt.savefig('agg_clust_network_genes_scipy.png',format='png')
# plot distance vs. iterations
fig,ax = plt.subplots()
distances = Z[:,2]
(x,y) = zip(*[(i,d) for (i,d) in enumerate(distances)])
ax.plot(x,y)
ax.set_xlabel('Iteration Number')
ax.set_ylabel('Linkage Distance')
plt.savefig('agg_clust_network_genes_distVsIterNum.png',format='png')

# format data for output
cluster_members = get_cluster_members(Z,df_names,20) ### BASED ON THE ABOVE PLOT, WE MIGHT CHANGE THE 20 VALUE
# reformat as dictionary to apply to dataframe
drugs_to_cluster = dict([(d,cnum) for (cnum,drug_list) in cluster_members.items() for d in drug_list])
# get all column names, collapse to a string for non-zero genes
cols = df.columns
non_zero = df.apply(lambda x: x==1)
df['Genes'] = non_zero.apply(lambda x: ','.join(list(cols[x.values])),axis=1)

#use a name_dic to convert DrugBank IDs to drug names 
name_dic = pickle.load(open('drugbankid_to_name.pkl','rb'))
map_results=[]
for item in df_names:
    if item in name_dic:
        map_results.append(name_dic[item])
    else:
        map_results.append('Not Mapped')

# add back drug names and cluster IDs
df['Name'] = map_results
df['ClusterLabel'] = df.index.map(drugs_to_cluster)
out_colums = ['Name','ClusterLabel','Genes']
df_out = df[out_colums]
df_out.to_excel('clustered_based_on_network_genes.xlsx')

