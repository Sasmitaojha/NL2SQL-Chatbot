import asyncio
from vanna_setup import agent

async def seed_memory():
    # Pre-seed internal agent memory with standard interactions based on requirements.
    pairs = [
        # Patient queries
        ("How many patients do we have?", "SELECT COUNT(*) AS total_patients FROM patients"),
        ("List patients who visited more than 3 times", "SELECT p.first_name, p.last_name, COUNT(a.id) as visit_count FROM patients p JOIN appointments a ON p.id = a.patient_id GROUP BY p.id HAVING visit_count > 3"),
        ("Which city has the most patients?", "SELECT city, COUNT(*) AS patient_count FROM patients GROUP BY city ORDER BY patient_count DESC LIMIT 1"),
        ("Show patient registration trend by month", "SELECT strftime('%Y-%m', registered_date) AS month, COUNT(*) FROM patients GROUP BY month ORDER BY month"),
        ("List all female patients", "SELECT * FROM patients WHERE gender='F'"),
        
        # Doctor queries
        ("List all doctors and their specializations", "SELECT name, specialization FROM doctors"),
        ("Which doctor has the most appointments?", "SELECT d.name, COUNT(a.id) AS app_count FROM doctors d JOIN appointments a ON d.id = a.doctor_id GROUP BY d.name ORDER BY app_count DESC LIMIT 1"),
        ("Average appointment duration by doctor", "SELECT d.name, AVG(t.duration_minutes) as avg_duration FROM doctors d JOIN appointments a ON d.id = a.doctor_id JOIN treatments t ON a.id = t.appointment_id GROUP BY d.name ORDER BY avg_duration DESC"),
        
        # Appointment queries
        ("Show me appointments for last month", "SELECT * FROM appointments WHERE appointment_date >= date('now', '-1 month')"),
        ("How many cancelled appointments last quarter?", "SELECT COUNT(*) FROM appointments WHERE status='Cancelled' AND appointment_date >= date('now', '-3 months')"),
        ("Show the busiest day of the week for appointments", "SELECT strftime('%w', appointment_date) AS dow, COUNT(*) AS app_count FROM appointments GROUP BY dow ORDER BY app_count DESC LIMIT 1"),
        ("What percentage of appointments are no-shows?", "SELECT (CAST(SUM(CASE WHEN status='No-Show' THEN 1 ELSE 0 END) AS REAL) / COUNT(*)) * 100 AS noshow_perc FROM appointments"),
        
        # Financial queries
        ("What is the total revenue?", "SELECT SUM(total_amount) FROM invoices"),
        ("Show revenue by doctor", "SELECT d.name, SUM(i.total_amount) AS total_revenue FROM invoices i JOIN appointments a ON a.patient_id = i.patient_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.name ORDER BY total_revenue DESC"),
        ("Top 5 patients by spending", "SELECT p.first_name, p.last_name, SUM(i.total_amount) AS spend FROM patients p JOIN invoices i ON p.id = i.patient_id GROUP BY p.id ORDER BY spend DESC LIMIT 5"),
        ("Show unpaid invoices", "SELECT * FROM invoices WHERE status != 'Paid'"),
        ("List patients with overdue invoices", "SELECT p.first_name, p.last_name, i.total_amount FROM patients p JOIN invoices i ON p.id = i.patient_id WHERE i.status = 'Overdue'"),
        ("Compare revenue between departments", "SELECT d.department, SUM(i.total_amount) AS revenue FROM invoices i JOIN appointments a ON a.patient_id = i.patient_id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.department ORDER BY revenue DESC"),
        ("Average treatment cost by specialization", "SELECT d.specialization, AVG(t.cost) FROM treatments t JOIN appointments a ON t.appointment_id = a.id JOIN doctors d ON d.id = a.doctor_id GROUP BY d.specialization"),
    ]

    print(f"Seeding {len(pairs)} interactions into DemoAgentMemory...")
    for question, sql in pairs:
        # Vanna 2.0 learns by storing context and previous queries
        await agent.agent_memory.save_tool_usage(
            question=question,
            tool_name="RunSqlTool",
            args={"sql": sql},
            context=None,
            success=True
        )
    print("Agent memory seeded successfully.")

if __name__ == "__main__":
    asyncio.run(seed_memory())
