# written to convert excel file to 
# a single dataframe with all output values
# written 11-2-20 JLW

import pickle,os,csv
import pandas as pd

f = 'Gene_Counting_Results_110220/Gene_counting_C0036341.xlsx'
xls = pd.ExcelFile(f)
merge_df = pd.DataFrame()
map_dic = dict([x for x in zip(xls.sheet_names,[1,2,3])])
for sn in xls.sheet_names:
	temp_df = pd.read_excel(xls,sn)
	temp_df = temp_df.drop([0]) # it looks like there was an extra row by mistake
	temp_df['output'] = map_dic[sn]
	merge_df = pd.concat([merge_df,temp_df])
merge_df = merge_df.loc[:, (merge_df != 0).any(axis=0)]
outf = f.replace('.xlsx','_merged.xlsx')
merge_df.to_excel(outf)

