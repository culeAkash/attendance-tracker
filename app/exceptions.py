from fastapi import Request,status
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.responses import JSONResponse


class ResourceNotFoundException(HTTPException):
    def __init__(self,resource:str,field_name:str,value:str):
        message = f"{resource} with {field_name} = {value} not found"
        super().__init__(status_code=404, detail=message)
        
class PasswordMismatchException(HTTPException):
    def __init__(self):
        message = "Password does not match, Please try again!"
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)
        
class DuplicateKeyException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )
        
class NotPermittedException(HTTPException):
    def __init__(self):
        message = "You are not permitted to perform this action"
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=message)

class BadDataException(HTTPException):
    def __init__(self, detail: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        )

async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=400,
        content={"message": "Validation error", "details": str(exc)},
    )

async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"details": exc.detail},
    )
    
async def resource_not_found_exception_handler(request: Request, exc: ResourceNotFoundException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
    
async def password_mismatch_exception_handler(request, exc: PasswordMismatchException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
    
async def duplicate_key_exception_handler(request: Request, exc: DuplicateKeyException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )
    

async def not_permitted_exception_handler(request: Request, exc: NotPermittedException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )


async def bad_data_exception_handler(request: Request, exc: BadDataException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"message": exc.detail},
    )