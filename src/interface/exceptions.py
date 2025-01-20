from fastapi import HTTPException


class UserNotFoundException(HTTPException):
    def __init__(self, email):
        super().__init__(status_code=404, detail=f"User: {email} does not exist")
