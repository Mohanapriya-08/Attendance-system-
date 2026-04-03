from sqlalchemy import Table, Column, Integer, String
from database import metadata
students = Table(
    "students",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("roll_no", String),
    Column("section", String),
    Column("device_id", String),
)

teachers = Table(
    "teachers",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("subject", String),
    Column("device_id", String),
)

sessions = Table(
    "sessions",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("teacher_id", Integer),
    Column("subject", String),
    Column("section", String),
    Column("status", String, default="active"),
    Column("date", String),
    Column("time", String),
)

attendance = Table(
    "attendance",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("student_id", Integer),
    Column("session_id", Integer),
    Column("status", String, default="present"),
    Column("date", String),
    Column("time", String),
)