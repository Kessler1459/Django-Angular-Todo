from rest_framework import status
from rest_framework.exceptions import ValidationError

class ConflictError(ValidationError):
    status_code = status.HTTP_409_CONFLICT
    def __init__(self,message: str):
        super().__init__({'detail':message})
 