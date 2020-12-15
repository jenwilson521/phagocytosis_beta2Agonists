# Counting exposures in patients with schiz.
# written 8-6-20 JLW
# modified 11-9-20 to look at beta2 agonists, JLW

library(CohortMethod)
library(SqlRender)

## Check access to Optum??
connectionDetails <- createConnectionDetails(dbms = "postgresql",  server = "server.address", user="username", password="password")
connection = connect(connectionDetails)
source_schema = "schema_name"
results_schema = "results_schema"
results_table = "res_table_name"
cdmVersion = 5
outputFolder <- "./schiz_beta2"

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

# count outcomes in beta2agonist-exposed compared to non-beta2agonist exposed
sql <- readSql("look_for_subsequent_outcomes.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=66,dme_id=55,drug_id=33)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- readSql("look_for_subsequent_outcomes.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=77,dme_id=55,drug_id=44)
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
	#[1] "counting cohorts"
	#  COHORT_DEFINITION_ID    COUNT
	#1                    1   132952
	#2                   11  1295938 beta2 agonist expsoure while age <=18 > 6
	#3                   22    15504 schizophrenia diagnosis while age >= 18
	#4                   33      600 patients with pediatric exposure and young adult diagnosis
	#5                   44    14904 schizophrenia young adult diagnosis minus those with pediatric exposure
	#6                   55 10770098 all inpatient visits
	#7                   66       42 patients with pediatric exposure and subsequent inpatient visits
	#8                   77     2384 patients without pediatric exposure and subsequet inpatient visits
	
print('creating covariate settings')
covSettings <- createDefaultCovariateSettings(excludedCovariateConceptIds = c(21603311,435783,1137529,262,8717,8971,9201,32760), addDescendantsToExclude = TRUE)

print("creating cohort method data")
 cohortMethodData <- getDbCohortMethodData(connectionDetails = connectionDetails, cdmDatabaseSchema = source_schema,oracleTempSchema = results_schema, targetId = 33, comparatorId = 44, outcomeIds = 55, studyStartDate = "", studyEndDate = "", exposureDatabaseSchema = results_schema, exposureTable = results_table, outcomeDatabaseSchema = results_schema, outcomeTable = results_table, cdmVersion = cdmVersion, firstExposureOnly = TRUE, removeDuplicateSubjects = TRUE, restrictToCommonPeriod = FALSE, washoutPeriod = 180, covariateSettings = covSettings)

print("saving cohort method data")
cohortMethodName = "beta2_hospital"
cohortFileName = paste(cohortMethodName,".zip",sep="")
 saveCohortMethodData(cohortMethodData, paste(outputFolder,cohortFileName,sep="/"))
print("Loading cohort method data, with drug combo")
cohortMethodData <- loadCohortMethodData(paste(outputFolder,cohortFileName,sep="/"))

print("Setting up studyPop and PS model")
studyPop <- createStudyPopulation(cohortMethodData = cohortMethodData, outcomeId = 55,firstExposureOnly = FALSE, restrictToCommonPeriod = FALSE, washoutPeriod = 0, removeDuplicateSubjects = "remove all",removeSubjectsWithPriorOutcome = FALSE, minDaysAtRisk = 1,riskWindowStart = 0, startAnchor = "cohort start", riskWindowEnd = 1825,endAnchor = "cohort end")
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

	#[1] "PS AUC"
	#[1] 0.8654047
	#Using prior: None 
	#Using 1 thread(s)
	#Fitting outcome model took 0.323 secs
	#[1] "Outcome model, IPW:"
	#Model type: cox
	#Stratified: FALSE
	#Use covariates: FALSE
	#Use inverse probability of treatment weighting: TRUE
	#Status: OK
	#
	#          Estimate lower .95 upper .95    logRr seLogRr
	#treatment  0.71055   0.54573   0.90661 -0.34172  0.1295
	#Using prior: None 
	#Using 1 thread(s)
	#Fitting outcome model took 0.727 secs
	#[1] "Outcome model, Matched"
	#Model type: cox
	#Stratified: FALSE
	#Use covariates: FALSE
	#Use inverse probability of treatment weighting: FALSE
	#Status: OK
	#
	#          Estimate lower .95 upper .95    logRr seLogRr
	#treatment  0.86041   0.65574   1.12726 -0.15035  0.1382
