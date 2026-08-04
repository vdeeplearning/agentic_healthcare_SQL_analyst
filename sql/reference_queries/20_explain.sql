-- Question: Inspect the indexed hospital/date query plan. Shape: SQLite plan rows. Assumption: indexes installed. Concepts: EXPLAIN QUERY PLAN, optimization.
EXPLAIN QUERY PLAN SELECT COUNT(*) FROM encounters WHERE hospital_id=:hospital_id AND admission_date>=:start_date AND admission_date<:end_date;
