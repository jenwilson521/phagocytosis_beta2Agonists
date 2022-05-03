# written to use a matrix of genes
# as input to a logistic regression model
# to identify if network genes are
# associated with increased or decreased
# phagocytosis. Written 10-29-20 JLW

import pickle,os,csv,math
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_squared_error, r2_score, accuracy_score
from optparse import OptionParser

# mapping for output 
out_map = ['Increase', 'Decrease', 'No Effect']
def main():
	parser=OptionParser()
	parser.add_option('-f','--gene_file', dest='counting_file',help='A gene counting file with phagocytosis values')

	(options,args) = parser.parse_args()
	print(options.counting_file)
	df = pd.read_excel(options.counting_file)

	# save drugnames and drug banks ids but remove them for the regression
	dbids = df['Drug Bank ID'].to_list()
	dnames = df['Drug Name'].to_list()
	df = df.drop(['Unnamed: 0','Drug Bank ID','Drug Name'],axis=1)
	
	y = df.loc[:,'output']
	X = df.drop(['output'],axis=1)
	gnames = list(X.columns)

	split_row = math.ceil(X.shape[0]*0.2) # save 20% of rows for testing
	X_test = X.loc[:split_row,:]
	y_test = y.loc[:split_row,]
	X_train = X.loc[split_row:,:]
	y_train = y.loc[split_row:,]

	model = LogisticRegression()
	model.fit(X_train, y_train)
	predicted_classes = model.predict(X_test)

	print('Mean squared error: %.2f'% mean_squared_error(y_test, predicted_classes))
	print('Coefficient of determination: %.2f'% r2_score(y_test, predicted_classes))

	outf = options.counting_file.replace(".xlsx","regCoeff.xlsx")
	writer = pd.ExcelWriter(outf,engine='xlsxwriter')
	for (i,oname) in enumerate(out_map):
		reg_coef = list(zip(gnames, model.coef_[i]))
		sort_rc = sorted(reg_coef,key = lambda x:x[1],reverse=True)
		print(oname)
		print(sort_rc[0:10])
		out_df = pd.DataFrame({'Gene Names':gnames,'Regression Coefficients':model.coef_[i]})
		out_df = out_df.sort_values(by='Regression Coefficients', ascending=False)
		out_df.to_excel(writer,sheet_name=oname,index=False)
	writer.save()

if __name__ == "__main__":
        main()
