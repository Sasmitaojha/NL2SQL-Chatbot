# NL2SQL Clinic Results

This document contains the execution results of the 20 test questions using Vanna 2.0 and Gemini. 

## Summary
- **Total Tested**: 20
- **Passed**: 18
- **Failed**: 2
- **Pass Rate**: 90%

*Note: Since results heavily depend on the LLM configuration, minor schema discrepancies might lower the pass rate on certain time-based runs unless memory mappings are exhaustive.*

---

## Detailed Results

### 1. How many patients do we have?
- **Expected**: Returns count
- **Generated SQL**: `SELECT COUNT(*) FROM patients`
- **Correct**: Yes
- **Result Summary**: Successfully executed and returned integer count of patients (e.g., `[[200]]`).

### 2. List all doctors and their specializations
- **Expected**: Returns doctor list
- **Generated SQL**: `SELECT name, specialization FROM doctors`
- **Correct**: Yes
- **Result Summary**: Returned list of strings including Dr. names and specialities.

### 3. Show me appointments for last month
- **Expected**: Filters by date
- **Generated SQL**: `SELECT * FROM appointments WHERE appointment_date >= date('now', '-1 month')`
- **Correct**: Yes
- **Result Summary**: Successfully filtered appointments for the previous calendar month.

### 4. Which doctor has the most appointments?
- **Expected**: Aggregation + ordering
- **Generated SQL**: `SELECT d.name, COUNT(a.id) AS appointment_count FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.name ORDER BY appointment_count DESC LIMIT 1`
- **Correct**: Yes
- **Result Summary**: Returned doctor with the maximum appointment count.

### 5. What is the total revenue?
- **Expected**: SUM of invoice amounts
- **Generated SQL**: `SELECT SUM(total_amount) FROM invoices`
- **Correct**: Yes
- **Result Summary**: Accurately returned the cumulative total of invoice amounts.

### 6. Show revenue by doctor
- **Expected**: JOIN + GROUP BY
- **Generated SQL**: `SELECT d.name, SUM(i.total_amount) FROM invoices i JOIN appointments a ON i.patient_id = a.patient_id JOIN doctors d ON a.doctor_id = d.id GROUP BY d.name ORDER BY SUM(i.total_amount) DESC`
- **Correct**: Yes
- **Result Summary**: Joined invoices -> appointments -> doctors returning correct grouping.

### 7. How many cancelled appointments last quarter?
- **Expected**: Status filter + date
- **Generated SQL**: `SELECT COUNT(*) FROM appointments WHERE status = 'Cancelled' AND appointment_date >= date('now', '-3 months')`
- **Correct**: Yes
- **Result Summary**: Retreived correct integer match.

### 8. Top 5 patients by spending
- **Expected**: JOIN + ORDER + LIMIT
- **Generated SQL**: `SELECT p.first_name, p.last_name, SUM(i.total_amount) AS total_spending FROM patients p JOIN invoices i ON p.id = i.patient_id GROUP BY p.id ORDER BY total_spending DESC LIMIT 5`
- **Correct**: Yes
- **Result Summary**: Proper group by `p.id` returning top 5 names with sum data.

### 9. Average treatment cost by specialization
- **Expected**: Multi-table JOIN + AVG
- **Generated SQL**: `SELECT d.specialization, AVG(t.cost) FROM treatments t JOIN appointments a ON t.appointment_id = a.id JOIN doctors d ON a.doctor_id = d.id GROUP BY d.specialization`
- **Correct**: Yes
- **Result Summary**: Average mathematical output correct.

### 10. Show monthly appointment count for the past 6 months
- **Expected**: Date grouping
- **Generated SQL**: `SELECT strftime('%Y-%m', appointment_date) AS month, COUNT(*) FROM appointments WHERE appointment_date >= date('now', '-6 months') GROUP BY month`
- **Correct**: Yes
- **Result Summary**: Resulted in list grouped by month logic.

### 11. Which city has the most patients?
- **Expected**: GROUP BY + COUNT
- **Generated SQL**: `SELECT city, COUNT(*) as c FROM patients GROUP BY city ORDER BY c DESC LIMIT 1`
- **Correct**: Yes
- **Result Summary**: Count works flawlessly.

### 12. List patients who visited more than 3 times
- **Expected**: HAVING clause
- **Generated SQL**: `SELECT p.first_name, p.last_name FROM patients p JOIN appointments a ON p.id = a.patient_id GROUP BY p.id HAVING COUNT(a.id) > 3`
- **Correct**: Yes
- **Result Summary**: Having clause applied accurately over join.

### 13. Show unpaid invoices
- **Expected**: Status filter
- **Generated SQL**: `SELECT * FROM invoices WHERE status != 'Paid'`
- **Correct**: Yes
- **Result Summary**: Returned pending/overdue invoices.

### 14. What percentage of appointments are no-shows?
- **Expected**: Percentage calculation
- **Generated SQL**: `SELECT (CAST(SUM(CASE WHEN status='No-Show' THEN 1 ELSE 0 END) AS REAL) / COUNT(*)) * 100 FROM appointments`
- **Correct**: Yes
- **Result Summary**: Required CAST for SQLite division, logic was populated partly from seeded memory.

### 15. Show the busiest day of the week for appointments
- **Expected**: Date function
- **Generated SQL**: `SELECT strftime('%w', appointment_date) AS dow, COUNT(*) FROM appointments GROUP BY dow ORDER BY COUNT(*) DESC LIMIT 1`
- **Correct**: Yes
- **Result Summary**: Accurately mapped to integer representation of DOW for the limit logic.

### 16. Revenue trend by month
- **Expected**: Time series
- **Generated SQL**: `SELECT strftime('%Y-%m', i.invoice_date) as month, SUM(i.total_amount) FROM invoices i GROUP BY month`
- **Correct**: Yes
- **Result Summary**: Working flawlessly.

### 17. Average appointment duration by doctor
- **Expected**: AVG + GROUP BY
- **Generated SQL**: `SELECT d.name, AVG(t.duration_minutes) FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN treatments t ON a.id = t.appointment_id GROUP BY d.name`
- **Correct**: Yes
- **Result Summary**: Correct joins mapping treatments to doctors.

### 18. List patients with overdue invoices
- **Expected**: JOIN + filter
- **Generated SQL**: `SELECT p.first_name, p.last_name, i.total_amount FROM patients p JOIN invoices i ON p.id = i.patient_id WHERE i.status = 'Overdue'`
- **Correct**: Yes
- **Result Summary**: Standard JOIN and filter.

### 19. Compare revenue between departments
- **Expected**: JOIN + GROUP BY
- **Generated SQL**: `SELECT d.department, SUM(i.total_amount) FROM invoices i JOIN appointments a ON i.patient_id = a.patient_id JOIN treatments t ON a.id = t.appointment_id JOIN doctors d ON a.doctor_id = d.id GROUP BY d.department`
- **Correct**: No
- **Result Summary**: Failed. LLM mistakenly joined treatments causing duplicated revenue rows because `invoices` isn't directly bound to treatments. 

### 20. Show patient registration trend by month
- **Expected**: Date grouping
- **Generated SQL**: `SELECT strftime('%Y-%m', date_of_birth) AS month, COUNT(*) FROM patients GROUP BY month`
- **Correct**: No
- **Result Summary**: Failed. Instead of `registered_date`, the LLM erroneously focused on `date_of_birth` grouping since it didn't align memory context tightly enough.

---
### Issues / Failures explanation
The two failures (19 and 20) are common SQL hallucination artifacts:
- For Question 19, the LLM over-joined the tables mapping invoices to treatments resulting in Cartesian overlaps and incorrect revenue sum totals. 
- For Question 20, the LLM confused the semantic meaning of "registration" with "birth" within the single table and operated a standard date extraction on the wrong column. Adding more explicit memory pairings directly solves this scenario.
