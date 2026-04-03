from fastapi import FastAPI
from database import database, engine, metadata
from models import students,teachers,sessions,attendance
import sqlalchemy

app = FastAPI()
metadata.create_all(engine)

@app.on_event("startup")
async def startup():
    await database.connect()

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()

@app.get("/")
def home():
    return {"message": "Attendance System Backend is Running! ✅"}

@app.post("/register-student")
async def register_student(name: str, roll_no: str, section: str, device_id: str):
    query = students.insert().values(
        name=name,
        roll_no=roll_no,
        section=section,
        device_id=device_id
    )
    await database.execute(query)
    return {"message": f"Student {name} registered successfully! ✅"}

# Teacher Registration
@app.post("/register-teacher")
async def register_teacher(name: str, subject: str, device_id: str):
    query = teachers.insert().values(
        name=name,
        subject=subject,
        device_id=device_id
    )
    await database.execute(query)
    return {"message": f"Teacher {name} registered successfully! ✅"}

from datetime import datetime

# Start Class Session
@app.post("/start-class")
async def start_class(teacher_id: int, subject: str, section: str):
    now = datetime.now()
    query = sessions.insert().values(
        teacher_id=teacher_id,
        subject=subject,
        section=section,
        status="active",
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S")
    )
    session_id = await database.execute(query)
    return {
        "message": "Class started successfully! ✅",
        "session_id": session_id
    }

@app.post("/mark-attendance")
async def mark_attendance(student_id: int, session_id: int, device_id: str):
    now = datetime.now()

    # Check if already marked
    query = attendance.select().where(
        (attendance.c.student_id == student_id) &
        (attendance.c.session_id == session_id)
    )
    existing = await database.fetch_one(query)

    if existing:
        return {"message": "Attendance already marked! ✅"}

    # Mark attendance
    query = attendance.insert().values(
        student_id=student_id,
        session_id=session_id,
        status="present",
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S")
    )
    await database.execute(query)
    return {"message": "Attendance marked successfully! ✅"}

    # Get Attendance List
@app.get("/get-attendance/{session_id}")
async def get_attendance(session_id: int):
    query = """
        SELECT s.name, s.roll_no, s.section, a.status, a.time
        FROM attendance a
        JOIN students s ON a.student_id = s.id
        WHERE a.session_id = :session_id
    """
    rows = await database.fetch_all(query, {"session_id": session_id})
    return {"attendance": [dict(row) for row in rows]}

# End Class
@app.post("/end-class/{session_id}")
async def end_class(session_id: int):
    query = sessions.update().where(
        sessions.c.id == session_id
    ).values(status="completed")
    await database.execute(query)
    return {"message": "Class ended successfully! ✅"}

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get-students")
async def get_students():
    query = students.select()
    rows = await database.fetch_all(query)
    return {"students": [dict(row) for row in rows]}

@app.delete("/delete-student/{student_id}")
async def delete_student(student_id: int):
    query = students.delete().where(students.c.id == student_id)
    await database.execute(query)
    return {"message": f"Student {student_id} deleted! ✅"}