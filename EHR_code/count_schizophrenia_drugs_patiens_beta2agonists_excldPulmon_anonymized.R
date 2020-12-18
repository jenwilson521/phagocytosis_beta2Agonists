
# modified 11-9-20 to look at beta2 agonists, JLW
# modified 12-17-20 to exclude pulmonary visits

library(CohortMethod)
library(SqlRender)

## Check access to Optum??
connectionDetails <- createConnectionDetails(dbms = "postgresql",  server = "server.address", user="username", password="password")
connection = connect(connectionDetails)
source_schema = "schema_name"
results_schema = "results_schema"
results_table = "res_table_name"
cdmVersion = 5
outputFolder <- "./schiz_beta2_ExPlm"

# analyze relevant tables to expedite study
print("analyzing tables")
sql <- "ANALYZE @source_schema.CONCEPT;"
sql <- render(sql,source_schema=source_schema)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- "ANALYZE @source_schema.CONDITION_OCCURRENCE;"
sql <- render(sql,source_schema=source_schema)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- "ANALYZE @source_schema.observation_period;"
sql <- render(sql,source_schema=source_schema)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# create table
print("creating tables")
sql <- "IF OBJECT_ID('@results_schema.@results_table', 'U') IS NOT NULL DROP TABLE @results_schema.@results_table;"
sql <- render(sql, results_schema = results_schema,results_table = results_table)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- "CREATE TABLE @results_schema.@results_table (cohort_definition_id INT, cohort_start_date DATE,cohort_end_date DATE,subject_id BIGINT);"
sql <- render(sql, results_schema = results_schema,results_table = results_table)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# looking at a pediatric exposure to beta2agonist
print("adding patients to the table")
sql <- readSql("count_dmes_outcomes.sql")
sql <- render(sql, results_schema = results_schema,results_table = results_table,vocabulary_database_schema = source_schema,cohort_id=1, rel_concept_id= 435783) # schizophrenia outcome and ancestors
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# sql <- readSql("beta2agonist_pediatric_exposure.sql")
sql <- readSql("beta2agon_pediatric_exposure_noPriorObsReq.sql") # no prior observation required
sql <- render(sql, vocabulary_database_schema = source_schema,cdm_database_schema=source_schema, target_database_schema = results_schema, target_cohort_table = results_table, target_cohort_id = 11)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# looking at diagnosis from age 18-30
#sql <- readSql("Schizophrenia_young_adult_diagnosis_noPriorObsReq.sql") # no prior observation required?
sql <- readSql("Schizophrenia_young_adult_diagnosis_noPriorObsReq_v2.sql") # updated 11-10-20 to require age > 18 at diagnosis
sql <- render(sql, vocabulary_database_schema = source_schema,cdm_database_schema=source_schema, target_database_schema = results_schema, target_cohort_table = results_table, target_cohort_id = 22)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# count patients in both cohorts
sql <- readSql("count_shared_patients.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=33,treat_id=11,diagnose_id=22)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# remove beta2agonist + schiz patients from the schiz cohort
sql <- readSql("remove_doubles_from_single_cohort.sql")
sql <- render(sql,results_schema = results_schema,results_table=results_table,cohort_id=44,double_cohort=33, single_cohort=22)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# Look at inpatient visits as the outcome
sql <- readSql("count_inpatient_visit.sql")
# sql <- readSql("count_inpatient_visit_psych_speciality.sql") # added 11-18-20 to look at inpatient visits with psych speciality
# sql <- readSql("count_psych_doctor_visits.sql") # added 11-19-20 to look at any visits with psychiatry
sql <- render(sql, vocabulary_database_schema = source_schema,cdm_database_schema=source_schema, target_database_schema = results_schema, target_cohort_table = results_table, target_cohort_id =55)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# Added 12-17-20, Look for in-patient visits with pulmonary provider specialty
sql <- readSql("find_pulmonary_inpatient_visits.sql")
sql <- render(sql, vocabulary_database_schema = source_schema,cdm_database_schema=source_schema, target_database_schema = results_schema, target_cohort_table = results_table, target_cohort_id=66)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# Remove pulmonary specialty from in-patient visits
sql <- readSql("remove_doubles_from_single_cohort.sql")
sql <- render(sql,results_schema = results_schema,results_table=results_table,cohort_id=77,double_cohort=66,single_cohort=55)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# count outcomes in beta2agonist-exposed compared to non-beta2agonist exposed
sql <- readSql("look_for_subsequent_outcomes.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=88,dme_id=77,drug_id=33)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- readSql("look_for_subsequent_outcomes.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=99,dme_id=77,drug_id=44)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

# repeat count with new definitions
print("counting cohorts")
sql <- paste("SELECT cohort_definition_id, COUNT(DISTINCT subject_id) AS count",
"FROM @results_schema.@results_table",
"GROUP BY cohort_definition_id")
sql <- render(sql, results_schema = results_schema,results_table = results_table)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
table <- querySql(connection, sql)
print(table)
	#   COHORT_DEFINITION_ID    COUNT
	#1                     1   132952 # diagnosis ofschizophrenia 
	#2                    11  1295938 # young adult diagnosis of schizphrenia (SYA) (age >=18)
	#3                    22    15504 # pediatric exposure to beta2 agonist
	#4                    33      600 # pediatric exposure to beta2 agonist + SYA
	#5                    44    14904 # SYA - pediatric exposure to beta2 agonist
	#6                    55 10770098 # all in patient visits
	#7                    66    29100 # in patient visits by pulmonary specialist
	#8                    77 10740998 # in patient visits NOT by pulmonary expert
	#9                    88       42 # PEbeta2 +SYA + inPatient
	#10                   99     2383 # SYA + inPatient
	
print('creating covariate settings')
covSettings <- createDefaultCovariateSettings(excludedCovariateConceptIds = c(21603311,435783,1137529,262,8717,8971,9201,32760), addDescendantsToExclude = TRUE)

print("creating cohort method data")
 cohortMethodData <- getDbCohortMethodData(connectionDetails = connectionDetails, cdmDatabaseSchema = source_schema,oracleTempSchema = results_schema, targetId = 33, comparatorId = 44, outcomeIds = 77, studyStartDate = "", studyEndDate = "", exposureDatabaseSchema = results_schema, exposureTable = results_table, outcomeDatabaseSchema = results_schema, outcomeTable = results_table, cdmVersion = cdmVersion, firstExposureOnly = TRUE, removeDuplicateSubjects = TRUE, restrictToCommonPeriod = FALSE, washoutPeriod = 180, covariateSettings = covSettings)

print("saving cohort method data")
cohortMethodName = "beta2_noPulm"
cohortFileName = paste(cohortMethodName,".zip",sep="")
 saveCohortMethodData(cohortMethodData, paste(outputFolder,cohortFileName,sep="/"))
print("Loading cohort method data, with drug combo")
cohortMethodData <- loadCohortMethodData(paste(outputFolder,cohortFileName,sep="/"))

print("Setting up studyPop and PS model")
studyPop <- createStudyPopulation(cohortMethodData = cohortMethodData, outcomeId = 77,firstExposureOnly = FALSE, restrictToCommonPeriod = FALSE, washoutPeriod = 0, removeDuplicateSubjects = "remove all",removeSubjectsWithPriorOutcome = FALSE, minDaysAtRisk = 1,riskWindowStart = 0, startAnchor = "cohort start", riskWindowEnd = 1825,endAnchor = "cohort end")
getAttritionTable(studyPop)

print("Creating PS")
ps <- createPs(cohortMethodData = cohortMethodData, population = studyPop,errorOnHighCorrelation=TRUE, control = createControl(tolerance =5e-01,maxIterations = 100000,noiseLevel="silent",startingVariance=-1,seed=0))
psauc<-computePsAuc(ps)
print("PS AUC")
print(psauc)
outcomeModel <- fitOutcomeModel(population = ps, modelType = "cox",inversePtWeighting = TRUE)
print("Outcome model, IPW:")
print(outcomeModel)

matchedPop <- matchOnPs(ps,caliper = 0.2, caliperScale = "standardized logit", maxRatio= 1)
outcomeModel <- fitOutcomeModel(population = matchedPop, modelType = "cox",)
print("Outcome model, Matched")
print(outcomeModel)

pdf("Optum_beta2agon_nonPulmInPatient_AttrDia.pdf")
drawAttritionDiagram(studyPop)
dev.off()
balance <- computeCovariateBalance(matchedPop, cohortMethodData)
fileConn <- file("Optum_beta2agon_nonPulmInPatient_CovBalTable.txt")
ctext <- createCmTable1(balance)
write.table(ctext,fileConn,sep='\t',quote=FALSE)
close(fileConn)


	#Removing 4 redundant covariates
	#Removing 24704 infrequent covariates
	#Normalizing covariates
	#Tidying covariates took 10.8 secs
	#Creating propensity scores took 22.2 secs
	#[1] "PS AUC"
	#[1] 0.8654047
	#Using prior: None
	#Using 1 thread(s)
	#Fitting outcome model took 0.318 secs
	#[1] "Outcome model, IPW:"
	#Model type: cox
	#Stratified: FALSE
	#Use covariates: FALSE
	#Use inverse probability of treatment weighting: TRUE
	#Status: OK
	#
	#          Estimate lower .95 upper .95    logRr seLogRr
	#treatment  0.71087   0.54597   0.90702 -0.34127  0.1295
	#Using prior: None
	#Using 1 thread(s)
	#Fitting outcome model took 0.15 secs
	#[1] "Outcome model, Matched"
	#Model type: cox
	#Stratified: FALSE
	#Use covariates: FALSE
	#Use inverse probability of treatment weighting: FALSE
	#Status: OK
	#
	#          Estimate lower .95 upper .95    logRr seLogRr
	#treatment  0.86041   0.65574   1.12726 -0.15035  0.1382


