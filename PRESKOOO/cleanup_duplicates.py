import sqlite3

conn = sqlite3.connect("presko.db")
cursor = conn.cursor()

# This deletes duplicate subject enrollments for each student
cursor.execute("""
DELETE FROM student_subjects
WHERE id NOT IN (
    SELECT MIN(id)
    FROM student_subjects
    GROUP BY student_id, subject_code
)
""")

conn.commit()
conn.close()

print("✅ Duplicate subject enrollments removed.")
