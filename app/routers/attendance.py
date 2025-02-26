from fastapi import APIRouter,Request,Response,Query,Depends
from typing import Annotated
from app.schemas import CreateAttendanceRequest,CreateAttendanceQueryParams,AttendanceResponse,ApiResponse
from app.databases import get_sqlite_db
from sqlalchemy.orm import Session
from app.models import Staff,Student,Standard,Attendance,StaffRole,StatusOptions
from app.utils.auth import get_current_user
from app.exceptions import BadDataException
from fastapi.exceptions import HTTPException

from fastapi.responses import JSONResponse
attendance_router = APIRouter()


@attendance_router.post("/mark_attendance",status_code=201)
async def mark_attendance(request : Request,attendance_request : CreateAttendanceRequest, attendance_params : Annotated[CreateAttendanceQueryParams,Query()],db : Session = Depends(get_sqlite_db),current_user :Staff = Depends(get_current_user)):
    try:
        # check if student exists of the given student_id
        student_to_be_marked = await Student.get_student_by_id(student_id=attendance_params.student_id,db=db)
        
        # check if standard_id in the request matches with the standard of the student
        if student_to_be_marked.standard_id!=attendance_request.standard_id:
            raise BadDataException("Standard ID doesn't match with the standard of the student")
        
        # Fetch standard data and check if current_user is assigned as class_teacher to the standard
        student_standard =  Standard.get_standard_by_id(standard_id=attendance_request.standard_id,db=db)
        if current_user.role==StaffRole.TEACHER and student_standard.class_teacher_id!=current_user.staff_id:
            raise BadDataException("You are not authorized to mark attendance for this standard")
        
        
        
        # check if attendance is already marked for the student
        already_marked_attendance = db.query(Attendance).filter(Attendance.date_of_attendance==attendance_request.date_of_attendance,Attendance.student_id==student_to_be_marked.student_id,Attendance.standard_id==student_standard.standard_id).first()
        
        if already_marked_attendance:
            #change the status of the student for that day
            if(already_marked_attendance.status==StatusOptions.PRESENT):
                already_marked_attendance.status=StatusOptions.ABSENT
            else:
                already_marked_attendance.status=StatusOptions.PRESENT
            db.commit()
            db.refresh(already_marked_attendance)
            attendance_response = AttendanceResponse(attendance_id=already_marked_attendance.attendance_id,status=already_marked_attendance.status,date_of_attendance=already_marked_attendance.date_of_attendance,student_id=already_marked_attendance.student_id,standard_id=already_marked_attendance.standard_id,recorded_by_id=already_marked_attendance.recorded_by_id)
            api_response = ApiResponse(status="success",message="Attendance status changed successfully",status_code=200,data=attendance_response)
            return api_response
        
        # create attendance object
        attendance_data_obj = Attendance(date_of_attendance=attendance_request.date_of_attendance,student_id=student_to_be_marked.student_id,standard_id=student_standard.standard_id,recorded_by_id=current_user.staff_id)
        db.add(attendance_data_obj)
        db.flush()
        db.refresh(attendance_data_obj)
        attendance_response = AttendanceResponse(attendance_id=attendance_data_obj.attendance_id,status=attendance_data_obj.status,date_of_attendance=attendance_data_obj.date_of_attendance,student_id=attendance_data_obj.student_id,standard_id=attendance_data_obj.standard_id,recorded_by_id=attendance_data_obj.recorded_by_id)
        api_response = ApiResponse(status="success",message="Attendance marked successfully",status_code=201,data=attendance_response)
        db.commit()
        return api_response
    except HTTPException as e:
        db.rollback()
        return JSONResponse(status_code=400, content={"message": e.detail})
    finally:
        db.close()