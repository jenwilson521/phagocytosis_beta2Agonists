import pickle,os,csv
import pandas as pd
import openpyxl
import xlsxwriter

from pandas import DataFrame

# this name_dic will be used later to 
name_dic = pickle.load(open('/Users/ellenbowen/PathFX2.0/PathFX/rscs/drugbankid_to_name.pkl','rb'))
c2g = pickle.load(open('/Users/ellenbowen/PathFX2.0/PathFX/rscs/merged_unique_cuis2genes.pkl','rb'))

#this creates a list of all the genes related to the phenotype schizophrenia in PathFX
scz_gene_list = c2g['C0036341']
rdir = os.path.join('/Users/ellenbowen/PathFX2.0/PathFX/results/pathFX_multiDrug_increase_phagocytosis')

#this steps through all of the Drugs in the file collection and selects for just the genes colom
allf = [(dir_nm,sub_dirs,flist) for (dir_nm,sub_dirs,flist) in os.walk(rdir)]
ftext ='_merged_neighborhood__assoc_table_.txt'
netfs_and_dirs = [(dn,f) for (dn,sdlist,flist) in allf for f in flist if ftext in f]
assoc_fdic = dict([(f.replace(ftext,''),os.path.join(dn,f)) for (dn,f) in netfs_and_dirs])
select_cols = ['cui','genes']

#prepares to write the output dataframe to Excel
writer = pd.ExcelWriter('Gene_counting.xlsx',engine='xlsxwriter')

#This preps the first row of the dataframe --> the header, which will consist of the DBID followed by the drug name and all of the schizophrenia associated genes
first_row = ['Drug Bank ID']
for gene in scz_gene_list:
    first_row.append(gene)

output_df = DataFrame([first_row])

#loop through all of the drug files 
for (dname,asf) in assoc_fdic.items():
    genes_in_dname = []
    genes_in_dname.append(dname)
    df = pd.read_table(asf)
    df = df[select_cols]
    df_cuis = df['cui'].to_list()
    scui = 'C0036341'
    if scui in df_cuis:
        #grab the row of the cui of interest
        schiz_row = df.loc[df['cui'] == scui]
        #this returns a string of genes and allows you to get the gene list associated with the row with a cui of interest
        schiz_genes = schiz_row['genes'].iloc[0]
        drug_gene_list = schiz_genes.split(',')
        for gene in scz_gene_list:
            if gene in drug_gene_list:
                genes_in_dname.append(1)
            else:
                genes_in_dname.append(0)
    else:
        for gene in scz_gene_list:
            genes_in_dname.append(0)
    output_df.loc[len(output_df)] = genes_in_dname
header_row = 0
output_df.columns = output_df.iloc[header_row]
print(output_df.head())


#add in the drug names above DB ID
map_list = output_df['Drug Bank ID'].tolist()
map_results = []
for item in map_list:
    if item in name_dic:
        map_results.append(name_dic[item])
    else:
        map_results.append('Not Mapped')
output_df.insert(1,'Drug Name',map_results)

print(output_df)




#output the DataFrame to Excel 

output_df.to_excel(writer,sheet_name = 'Increase Phagocytosis', index=False)
writer.save()
    
