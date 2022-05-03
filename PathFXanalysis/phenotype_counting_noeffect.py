import pickle,os,csv
import pandas as pd
import openpyxl
import xlsxwriter

from pandas import DataFrame 
from openpyxl import load_workbook

#This code counts relevant phenotypes from the compilation of drugs that decrease phagocytosis (given that you've already created a .xlsx file and want to add data from other groups to that particular file)

name_dic = pickle.load(open('/Users/ellenbowen/PathFX/rscs/drugbankid_to_name.pkl','rb'))

#load previous workbook
path = os.path.join('/Users/ellenbowen/schizophrenia_spark/Phenotype_counting.xlsx')
book = load_workbook(path)
writer = pd.ExcelWriter(path, engine = 'openpyxl')
writer.book = book

#step through all the files 
rdir = os.path.join('/Users/ellenbowen/PathFX/results/pathFX_multiDrug_noeffect_phagocytosis')
allf = [(dir_nm,sub_dirs,flist) for (dir_nm,sub_dirs,flist) in os.walk(rdir)]
ftext ='_merged_neighborhood__assoc_table_.txt'
netfs_and_dirs = [(dn,f) for (dn,sdlist,flist) in allf for f in flist if ftext in f]
assoc_fdic = dict([(f.replace(ftext,''),os.path.join(dn,f)) for (dn,f) in netfs_and_dirs])
select_cols = ['phenotype','cui']

candidate_cuis = ['C0003469','C0002395','C0011570','C0009324','C0011581','C0003123','C0424295','C0525045','C0003467','C0041696','C1269683','C0006870','C0025261','C0003125','C1868649','C0004936','C0026769','C0021390','C0751292','C0751293','C0751294','C0013473','C0002622','C0030319','C0004364','C0017658','C0154588','C0376280','C0006012','C0338831','C1704377','C0005586','C0036421','C3875321','C0282126','C1527336','C0026896','C0025193','C0085159','C0013384','C0086133','C0020877','C0003431','C0042164','C0011303','C0036337','C2700439','C2700440','C4020884','C2700438','C0042165','C0017661','C0042384','C0036341','C0039103','C0011265','C0024713','C0027121','C0030567','C0018524','C1970943','C1970945','C1852197','C0398650','C0011265','C0038443','C0086132','C0011573','C0494463','C0546126','C1263846','C0041671','C0006370','C0021603','C0004930','C0564567','C0233523']

candidate_phens = ['Anxiety Disorders','Alzheimer disease','Mental Depression','Ulcerative Colitis','Depressive disorder','Anorexia','Hyperactive behavior','Mood Disorders','Anxiety','Unipolar Depression','Major depressive disorder','Cannabis Dependence','Memory Disorders','Anorexia Nervosa','Panic disorder 1','Mental disorders','Multiple Sclerosis','Inflammatory Bowel Diseases','Age-Related Memory Disorders','Memory Disorder, Semantic','Memory Disorder, Spatial','Eating Disorders','Amnesia','Panic Disorder','Autoimmune Diseases','Glomerulonephritis','Mixed anxiety and depressive disorder','Anxiety States, Neurotic','Borderline Personality Disorder','Manic','Bright Disease','Bipolar Disorder','Systemic Scleroderma','Inflammatory dermatosis','Depression, Neurotic','Sjogrens Syndrome','Myasthenia Gravis','Melancholia','Seasonal Affective Disorder','Dyskinetic syndrome','Depressive Syndrome','Ileitis','Antisocial Personality Disorder','Uveitis','Demyelinating Diseases','Schizoaffective Disorder','MAJOR AFFECTIVE DISORDER 8','MAJOR AFFECTIVE DISORDER 9','Anxiety disease','Major affective disorder 7','Anterior uveitis','IGA Glomerulonephritis','Vasculitis','Schizophrenia','Synovitis','Presenile dementia','Manic Disorder','Myositis','Parkinson disease','Hallucinations','MAJOR AFFECTIVE DISORDER 4','MAJOR AFFECTIVE DISORDER 6','MAJOR AFFECTIVE DISORDER 1','Autoimmune thrombocytopenia','Presenile dementia','Stress, Psychological','Depressive Symptoms','Endogenous depression','Alzheimer Disease, Late Onset','Acute Confusional Senile Dementia','Attention deficit hyperactivity disorder','Attention Deficit Disorder','Bulimia','Sleep Initiation and Maintenance Disorders','Behavior Disorders','Impulsive character (finding)','Antisocial behavior']

output_df = DataFrame(candidate_cuis)
output_df['Phenotypes'] = candidate_phens

for (dname,asf) in assoc_fdic.items():
    cuis_in_dname = []
    df = pd.read_table(asf)
    df = df[select_cols]
    for cui in candidate_cuis:
        if cui in df.values:
            cuis_in_dname.append(1)
        else:
            cuis_in_dname.append(0)
    output_df[dname] = cuis_in_dname


#add in drug name above DB ID
map_list = list(output_df.columns)
map_results = []
for item in map_list:
    if item in name_dic:
        map_results.append(name_dic[item])
    else:
        map_results.append('Not mapped')
output_df.loc[-1] = map_results
output_df = output_df.sort_index()
print(output_df.head)

output_df.to_excel(writer,sheet_name = 'No effect')
writer.save()
