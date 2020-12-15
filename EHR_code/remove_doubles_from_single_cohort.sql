INSERT INTO @results_schema.@results_table (
        cohort_definition_id,
        cohort_start_date,
        cohort_end_date,
        subject_id)
SELECT DISTINCT @cohort_id, -- Only keep subject IDs if they are not in the double cohort
        s.cohort_start_date,
        s.cohort_end_date,
        s.subject_id
        FROM @results_schema.@results_table s -- single treatment
	WHERE s.subject_id NOT IN (SELECT d.subject_id FROM @results_schema.@results_table d WHERE d.cohort_definition_id = @double_cohort)
	AND s.cohort_definition_id = @single_cohort;
