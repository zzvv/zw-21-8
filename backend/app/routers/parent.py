from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime, timedelta
from app.core.database import get_db
from app.models.models import User, ParentStudent, Student, Enrollment, CourseSchedule, LessonRecord, ExamRecord, Course, Classroom, Teacher
from app.schemas.schemas import ParentStudentOut, ParentStudentCreate, ParentScheduleOut, ParentLessonRecordOut, ParentExamOut, ParentDashboardOut, StudentOut
from app.routers.auth import get_current_user, require_role

router = APIRouter()

def get_parent_students(db: Session, parent_id: int) -> List[Student]:
    return db.query(Student).join(ParentStudent, ParentStudent.student_id == Student.id).filter(ParentStudent.parent_id == parent_id).all()

def get_student_ids(db: Session, parent_id: int) -> List[int]:
    return [ps.student_id for ps in db.query(ParentStudent).filter(ParentStudent.parent_id == parent_id).all()]

@router.get("/children", response_model=List[StudentOut])
def list_children(db: Session = Depends(get_db), current_user: User = require_role("parent")):
    return get_parent_students(db, current_user.id)

@router.post("/children", response_model=ParentStudentOut)
def bind_child(data: ParentStudentCreate, db: Session = Depends(get_db), current_user: User = require_role("parent")):
    student = db.query(Student).filter(Student.id == data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="学员不存在")
    existing = db.query(ParentStudent).filter(ParentStudent.parent_id == current_user.id, ParentStudent.student_id == data.student_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="已绑定该学员")
    ps = ParentStudent(parent_id=current_user.id, student_id=data.student_id)
    db.add(ps); db.commit(); db.refresh(ps)
    return ps

@router.delete("/children/{student_id}")
def unbind_child(student_id: int, db: Session = Depends(get_db), current_user: User = require_role("parent")):
    ps = db.query(ParentStudent).filter(ParentStudent.parent_id == current_user.id, ParentStudent.student_id == student_id).first()
    if not ps:
        raise HTTPException(status_code=404, detail="绑定关系不存在")
    db.delete(ps); db.commit()
    return {"message": "解绑成功"}

@router.get("/dashboard", response_model=ParentDashboardOut)
def parent_dashboard(db: Session = Depends(get_db), current_user: User = require_role("parent")):
    student_ids = get_student_ids(db, current_user.id)
    if not student_ids:
        return {"children": [], "upcoming_lessons": [], "recent_lesson_records": [], "exam_progress": []}
    
    children = db.query(Student).filter(Student.id.in_(student_ids)).all()
    
    today = date.today()
    end_date = today + timedelta(days=14)
    
    upcoming_lessons = (
        db.query(CourseSchedule, Course, Classroom, Teacher, Enrollment, Student)
        .join(Enrollment, Enrollment.schedule_id == CourseSchedule.id)
        .join(Course, Course.id == CourseSchedule.course_id)
        .join(Classroom, Classroom.id == CourseSchedule.classroom_id)
        .join(Teacher, Teacher.id == CourseSchedule.teacher_id)
        .join(Student, Student.id == Enrollment.student_id)
        .filter(Enrollment.student_id.in_(student_ids))
        .filter(CourseSchedule.is_active == True)
        .filter(CourseSchedule.start_date <= end_date)
        .filter(CourseSchedule.end_date == None or CourseSchedule.end_date >= today)
        .order_by(CourseSchedule.weekday, CourseSchedule.start_time)
        .limit(10)
        .all()
    )
    
    schedule_list = []
    for sched, course, classroom, teacher, enrollment, student in upcoming_lessons:
        schedule_list.append({
            "id": sched.id,
            "course_id": course.id,
            "course_name": course.name,
            "instrument": course.instrument,
            "classroom_id": classroom.id,
            "classroom_name": classroom.name,
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "weekday": sched.weekday,
            "start_time": sched.start_time,
            "end_time": sched.end_time,
            "start_date": sched.start_date,
            "end_date": sched.end_date,
            "student_name": student.name
        })
    
    recent_records = (
        db.query(LessonRecord, Course, Teacher)
        .join(Enrollment, Enrollment.id == LessonRecord.enrollment_id)
        .join(Course, Course.id == Enrollment.course_id)
        .join(Teacher, Teacher.id == Course.teacher_id)
        .filter(Enrollment.student_id.in_(student_ids))
        .order_by(LessonRecord.lesson_date.desc())
        .limit(10)
        .all()
    )
    
    record_list = []
    for record, course, teacher in recent_records:
        record_list.append({
            "id": record.id,
            "lesson_date": record.lesson_date,
            "status": record.status,
            "content": record.content,
            "homework": record.homework,
            "course_name": course.name,
            "teacher_name": teacher.name
        })
    
    exam_progress = (
        db.query(ExamRecord)
        .filter(ExamRecord.student_id.in_(student_ids))
        .order_by(ExamRecord.exam_date.desc())
        .limit(10)
        .all()
    )
    
    return {
        "children": children,
        "upcoming_lessons": schedule_list,
        "recent_lesson_records": record_list,
        "exam_progress": exam_progress
    }

@router.get("/schedules", response_model=List[ParentScheduleOut])
def list_schedules(student_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = require_role("parent")):
    student_ids = get_student_ids(db, current_user.id)
    if student_id and student_id not in student_ids:
        raise HTTPException(status_code=403, detail="无权查看该学员信息")
    
    filters = [Enrollment.student_id.in_(student_ids if not student_id else [student_id])]
    filters.append(CourseSchedule.is_active == True)
    
    results = (
        db.query(CourseSchedule, Course, Classroom, Teacher, Enrollment, Student)
        .join(Enrollment, Enrollment.schedule_id == CourseSchedule.id)
        .join(Course, Course.id == CourseSchedule.course_id)
        .join(Classroom, Classroom.id == CourseSchedule.classroom_id)
        .join(Teacher, Teacher.id == CourseSchedule.teacher_id)
        .join(Student, Student.id == Enrollment.student_id)
        .filter(*filters)
        .order_by(CourseSchedule.weekday, CourseSchedule.start_time)
        .all()
    )
    
    return [{
        "id": sched.id,
        "course_id": course.id,
        "course_name": course.name,
        "instrument": course.instrument,
        "classroom_id": classroom.id,
        "classroom_name": classroom.name,
        "teacher_id": teacher.id,
        "teacher_name": teacher.name,
        "weekday": sched.weekday,
        "start_time": sched.start_time,
        "end_time": sched.end_time,
        "start_date": sched.start_date,
        "end_date": sched.end_date,
        "student_name": student.name
    } for sched, course, classroom, teacher, enrollment, student in results]

@router.get("/lesson-records", response_model=List[ParentLessonRecordOut])
def list_lesson_records(student_id: Optional[int] = None, start: Optional[date] = None, end: Optional[date] = None, db: Session = Depends(get_db), current_user: User = require_role("parent")):
    student_ids = get_student_ids(db, current_user.id)
    if student_id and student_id not in student_ids:
        raise HTTPException(status_code=403, detail="无权查看该学员信息")
    
    filters = [Enrollment.student_id.in_(student_ids if not student_id else [student_id])]
    if start:
        filters.append(LessonRecord.lesson_date >= start)
    if end:
        filters.append(LessonRecord.lesson_date <= end)
    
    results = (
        db.query(LessonRecord, Course, Teacher)
        .join(Enrollment, Enrollment.id == LessonRecord.enrollment_id)
        .join(Course, Course.id == Enrollment.course_id)
        .join(Teacher, Teacher.id == Course.teacher_id)
        .filter(*filters)
        .order_by(LessonRecord.lesson_date.desc())
        .all()
    )
    
    return [{
        "id": record.id,
        "lesson_date": record.lesson_date,
        "status": record.status,
        "content": record.content,
        "homework": record.homework,
        "course_name": course.name,
        "teacher_name": teacher.name
    } for record, course, teacher in results]

@router.get("/exams", response_model=List[ParentExamOut])
def list_exams(student_id: Optional[int] = None, db: Session = Depends(get_db), current_user: User = require_role("parent")):
    student_ids = get_student_ids(db, current_user.id)
    if student_id and student_id not in student_ids:
        raise HTTPException(status_code=403, detail="无权查看该学员信息")
    
    q = db.query(ExamRecord).filter(ExamRecord.student_id.in_(student_ids if not student_id else [student_id]))
    return q.order_by(ExamRecord.exam_date.desc()).all()