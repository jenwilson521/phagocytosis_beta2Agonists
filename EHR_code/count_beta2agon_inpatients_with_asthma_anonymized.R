# Counting exposures in patients with schiz.
# written 8-6-20 JLW
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

# counts from previous analysis
        #   COHORT_DEFINITION_ID    COUNT
        #1                     1   132952 # diagnosis of schizophrenia
        #2                    11  1295938 # young adult diagnosis of schizphrenia (SYA) (age >=18)
        #3                    22    15504 # pediatric exposure to beta2 agonist
        #4                    33      600 # pediatric exposure to beta2 agonist + SYA
        #5                    44    14904 # SYA - pediatric exposure to beta2 agonist
        #6                    55 10770098 # all in patient visits
        #7                    66    29100 # in patient visits by pulmonary specialist
        #8                    77 10740998 # in patient visits NOT by pulmonary expert
        #9                    88       42 # PEbeta2 +SYA + inPatient
        #10                   99     2383 # SYA + inPatient
	#11                  100  5546876 # patients with asthma diagnosis
	#12                  200      443 # SYA + pediatric exposure + asthma
	#13                  300     2334 # SYA w/o pediatric exposure + asthma
	#14                  400       35 # SYA + pediatric exposure + asthma + inpatient, non-pulmonary inpatient
	#15                  500      514 # SYA non-pediatric +astham, non-pulmonary inpatient

# look at Asthma patients and then count the overlaps with the other cohorts
#print("adding patients to the table")
#sql <- readSql("count_dmes_outcomes.sql")
#sql <- render(sql, results_schema = results_schema,results_table = results_table,vocabulary_database_schema = source_schema,cohort_id=100, rel_concept_id= 317009) # asthma and ancestors 
#sql <- translate(sql, targetDialect = connectionDetails$dbms)
#executeSql(connection, sql)
#
## count patients in both cohorts
sql <- readSql("count_shared_patients.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=200,treat_id=33,diagnose_id=100)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- readSql("count_shared_patients.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=300,treat_id=44,diagnose_id=100)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- readSql("count_shared_patients.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=400,treat_id=88,diagnose_id=100)
sql <- translate(sql, targetDialect = connectionDetails$dbms)
executeSql(connection, sql)

sql <- readSql("count_shared_patients.sql")
sql <- render(sql,results_schema=results_schema,results_table=results_table,cohort_id=500,treat_id=99,diagnose_id=100)
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

	

