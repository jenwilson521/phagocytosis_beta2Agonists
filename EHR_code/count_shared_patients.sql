INSERT INTO @results_schema.@results_table (
        cohort_definition_id,
        cohort_start_date,
        cohort_end_date,
        subject_id)
SELECT DISTINCT @cohort_id, -- Patients with diagnosis following treatment 
        s.cohort_start_date,
        s.cohort_end_date,
        s.subject_id
        FROM @results_schema.@results_table t -- salmeterol treatment
        INNER JOIN @results_schema.@results_table s -- schizophrenia diagnosis
        ON s.subject_id = t.subject_id
        AND t.cohort_definition_id=@treat_id
        AND s.cohort_definition_id=@diagnose_id;
