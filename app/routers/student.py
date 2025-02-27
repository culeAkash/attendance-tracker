from fastapi import APIRouter,Depends,Query
from app.models.staff import Staff
from app.models.standard import Standard
from app.utils.auth import check_current_user_admin_principal,get_current_user
from app.databases import get_sqlite_db
from sqlalchemy.orm import Session
from app.models  import Student,Parent,Address,Standard,GovtId,UserType
from fastapi.exceptions import HTTPException
from fastapi.responses import JSONResponse
from typing import Annotated
from app.schemas import ApiResponse,GovtIdSchema,StandardQueryParams,StudentCreateParams,DeleteStudentParams,CreateStudent,StudentResponse,UpdateStudentParams,UpdateParentSchema,UpdateAddressSchema,UpdateGovtIdSchema,UpdateStudentSchema
from app.exceptions import NotPermittedException
student_router = APIRouter()



@student_router.post("/create_student",status_code=201)
async def create_student(student_data :CreateStudent,standard_query :Annotated[StudentCreateParams,Query()],current_user : Staff =Depends(check_current_user_admin_principal),db : Session = Depends(get_sqlite_db)):
    try:
        # begin a transaction
        # db.close()
        # db.begin()
        
        # create address data
        # current_user = await check_current_user_admin_principal(current_user)
        address_data = student_data.address
        address_model_data = Address(**address_data.model_dump())
        db.add(address_model_data)
        db.flush()
        
        
        # create parent data
        student_parent_data = student_data.parent
        student_parent_model_data = Parent(**student_parent_data.model_dump())
        db.add(student_parent_model_data)
        db.flush()
        
        
        #TODO : check if standard exists of given grade and section
        standard = Standard.get_standard_by_grade_and_section(standard_query.grade, standard_query.section,db=db)
        
        # create student data
        student_data.__delattr__("address")
        student_data.__delattr__("parent")
        
        db.refresh(student_parent_model_data)
        db.refresh(address_model_data)
        
        govt_id_data = student_data.govt_id
        student_data.__delattr__("govt_id")
        
        student_data = student_data.model_dump()
    
    # Convert date_of_birth from string to date
        if isinstance(student_data["date_of_birth"], str):
            student_data["date_of_birth"] = datetime.strptime(student_data["date_of_birth"], "%Y-%m-%d").date()
        
        student_model_data = Student(**student_data)
        student_model_data.standard_id = standard.standard_id
        student_model_data.parent_id = student_parent_model_data.parent_id
        student_model_data.address_id = address_model_data.address_id
        student_model_data.roll_number = await Student.get_next_roll_number(db=db)

        db.add(student_model_data)
        db.flush()
        db.refresh(student_model_data)
        # print(student_data.address,address_model_data)
        
        
        # TODO : ADD govt id to database after checking
        # check if govt id exists in the database
        GovtId.check_if_id_exists(id_number=govt_id_data.id_number,user_type=UserType.STUDENT,db=db)
        # create date for govt id
        govt_id_model = GovtId(**govt_id_data.model_dump(),user_id=student_model_data.student_id,user_type=UserType.STUDENT)
        db.add(govt_id_model)
        db.flush()
        db.refresh(govt_id_model)
        student_response = StudentResponse(student_id=student_model_data.student_id,name=student_model_data.name,roll_number=student_model_data.roll_number,date_of_birth=student_model_data.date_of_birth,gender=student_model_data.gender,standard=standard, parent=student_parent_model_data, address=address_model_data,govt_id=GovtIdSchema(
            id_number=govt_id_model.id_number,
            id_type=govt_id_model.id_type
        ))

        db.commit()
        api_response = ApiResponse(message="Student created successfully",status_code=201,data=student_response)
        return api_response
    except HTTPException as e:
        db.rollback()
        print(e)
        return JSONResponse(content={"message": e.detail}, status_code=e.status_code)
    finally:
        # commit the transaction
        db.close()
    
    
@student_router.get("/get_all_students")
async def get_all_students(db:Session =  Depends(get_sqlite_db)):
    all_students = db.query(Student).all()
    student_responses = []
    # fetch govtid for all students
    for student in all_students:
        govt_id = GovtId.get_govt_id_by_user_id(user_id=student.student_id,user_type=UserType.STUDENT,db=db)
        if not govt_id:
            continue
        else:
            govt_id = GovtIdSchema(
                id_number=govt_id.id_number,
                id_type=govt_id.id_type
            )
        student_response = StudentResponse(
            student_id=student.student_id,
            name=student.name,
            roll_number=student.roll_number,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            standard=student.standard,
            parent=student.parent,
            address=student.address,
            govt_id=govt_id
        )
        student_responses.append(student_response) 
    return ApiResponse(status="success", message="All Students", status_code=200, data=student_responses)
    
    
@student_router.get("/get_all_students_of_standard")
async def get_all_students_of_standard(standard_query : Annotated[StandardQueryParams,Query()],db:Session =  Depends(get_sqlite_db)):
    # get standard data of the given standard query
    standard =  Standard.get_standard_by_grade_and_section(standard_query.grade, standard_query.section,db)
    
    # fetch all students of the given standard
    all_students = db.query(Student).filter(Student.standard_id == standard.standard_id).all()
    student_responses = []
    # fetch govtid for all students
    for student in all_students:
        govt_id = GovtId.get_govt_id_by_user_id(user_id=student.student_id,user_type=UserType.STUDENT,db=db)
        if not govt_id:
            continue
        else:
            govt_id = GovtIdSchema(
                id_number=govt_id.id_number,
                id_type=govt_id.id_type
            )
        student_response = StudentResponse(
            student_id=student.student_id,
            name=student.name,
            roll_number=student.roll_number,
            date_of_birth=student.date_of_birth,
            gender=student.gender,
            standard=student.standard,
            parent=student.parent,
            address=student.address,
            govt_id=govt_id
        )
        student_responses.append(student_response) 
    return ApiResponse(status="success", message="All Students", status_code=200, data=student_responses)



# route to update student data
# TODO : testing to be done
@student_router.patch('/update_student')
async def update_student(params : Annotated[UpdateStudentParams, Query()], student_data : UpdateStudentSchema, local_db : Session = Depends(get_sqlite_db), current_user : Staff = Depends(get_current_user)):
    try:
        # check if student with student id exists
        student = await Student.get_student_by_id(db=local_db,student_id=params.student_id)
        
        # fetch standard of the student
        student_standard = Standard.get_standard_by_id(db=local_db,standard_id=student.standard_id)
        
        # if the loggedin staff is a teacher, check if it is the class teacher of the student's class
        if current_user.user_type == UserType.TEACHER:
            if student_standard.class_teacher_id != current_user.staff_id:
                raise NotPermittedException("You are not allowed to update data for this student of standard with standard_id: %s" % student_standard.standard_id)
        
        # update address data before updating the student data
        update_address_data = student_data.address
        
        #fetch the existing address of the student
        student_address_id = student.address_id
        student_address = await Address.get_address_by_id(db=local_db,address_id=student_address_id)
        
        # update the address data
        if update_address_data:
            # update the address data
            if update_address_data.city :
                student_address.city = update_address_data.city
            if update_address_data.state :
                student_address.state = update_address_data.state
            if update_address_data.country :
                student_address.country = update_address_data.country
            if update_address_data.street :
                student_address.street = update_address_data.street
            local_db.flush()
            local_db.refresh(student_address)
        
        # update parent data before updating the student data
        update_parent_data = student_data.parent
        
        #fetch the existing parent of the student
        student_parent_id = student.parent_id
        student_parent = await Parent.get_parent_by_id(db=local_db,parent_id=student_parent_id)
        
        # update the parent data
        if update_parent_data:
            # update the parent data
            if update_parent_data.parent_name :
                student_parent.parent_name = update_parent_data.parent_name
            if update_parent_data.parent_contact_number :
                student_parent.parent_contact_number = update_parent_data.parent_contact_number
            if update_parent_data.parent_email :
                student_parent.parent_email = update_parent_data.parent_email
            local_db.flush()
            local_db.refresh(student_parent)
            
        # update govt information before updating the student data
        update_govt_data = student_data.govt_id
        
        #fetch the existing govt of the student
        student_govt_id = student.govt_id
        student_govt = await GovtId.get_govt_id_by_id(db=local_db,id=student_govt_id)
        
        # update the govt data
        if update_govt_data:
            # update the govt data
            if update_govt_data.id_number :
                student_govt.id_number = update_govt_data.id_number
            if update_govt_data.id_type :
                student_govt.id_type = update_govt_data.id_type
            local_db.flush()
            local_db.refresh(student_govt)
        
        # update student data
        student_data.__delattr__("address")
        student_data.__delattr__("parent")
        student_data.__delattr__("govt_id")
        
        # update the student data in the database
        if student_data.date_of_birth:
            student.date_of_birth = student_data.date_of_birth
        if student_data.gender:
            student.gender = student_data.gender
        if student_data.name:
            student.name = student_data.name
        
        local_db.commit()
        
        # fetch new student data
        student = await Student.get_student_by_id(db=local_db,student_id=params.student_id)
        
        student_response = StudentResponse(student_id=student.student_id,name=student.name,roll_number=student.roll_number,date_of_birth=student.date_of_birth,gender=student.gender,standard=student.standard, parent=student.parent, address=student.address,govt_id=GovtIdSchema(
            id_number=student_govt.id_number,
            id_type=student_govt.id_type
        ))
        
        return ApiResponse(status="success", message="Student data updated successfully", status_code=200, data=student_response)
        
    except HTTPException as e:
        local_db.rollback()
        raise e
    finally:
        local_db.close()


# TODO : testing to be done
@student_router.delete("/delete_student")
async def delete_student(params : Annotated[DeleteStudentParams,Query()],local_db : Session = Depends(get_sqlite_db),current_user : Staff = Depends(get_current_user)):
    try:
        # delete student by student id
        # check if student with student id exists
        student = await Student.get_student_by_id(db=local_db,student_id=params.student_id)
    
        # fetch standard of the student
        student_standard = Standard.get_standard_by_id(db=local_db,standard_id=student.standard_id)
    
        # if the loggedin staff is a teacher, check if it is the class teacher of the student's class
        if current_user.user_type == UserType.TEACHER:
            if student_standard.class_teacher_id != current_user.staff_id:
                raise NotPermittedException("You are not allowed to delete this student of standard with standard_id: %s" % student_standard.standard_id)
    
        # before deleting the student delete the govtId associated with the student
        govtId = GovtId.get_govt_id_by_user_id(db=local_db,user_type="STUDENT",user_id=student.student_id)
        if govtId:
            local_db.delete(govtId)
            local_db.flush()
        
        # delete the student
        local_db.delete(student)
        
        # TODO : add task to queue to delete the student from cloud_db
        
        
        local_db.commit()
        return ApiResponse(status="success", message="Student deleted successfully", status_code=200)
    except HTTPException as e:
        local_db.rollback()
        raise e
    finally:
        local_db.close()