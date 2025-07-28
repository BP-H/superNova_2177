class FastAPI:
    def __init__(self, *args, **kwargs):
        pass

class Depends:
    def __init__(self, dependency=None):
        self.dependency = dependency

class HTTPException(Exception):
    def __init__(self, status_code: int, detail=None):
        super().__init__(detail)
        self.status_code = status_code
        self.detail = detail

class status:
    HTTP_200_OK = 200
    HTTP_201_CREATED = 201
    HTTP_400_BAD_REQUEST = 400
    HTTP_401_UNAUTHORIZED = 401
    HTTP_500_INTERNAL_SERVER_ERROR = 500

class Query:
    def __init__(self, default=None, **kwargs):
        self.default = default

class Body:
    def __init__(self, default=None, **kwargs):
        self.default = default

class UploadFile:
    def __init__(self, *args, **kwargs):
        pass

class File:
    def __init__(self, *args, **kwargs):
        pass

class BackgroundTasks:
    def __init__(self, *args, **kwargs):
        pass

class HTMLResponse:
    def __init__(self, content=None, **kwargs):
        self.content = content

class JSONResponse:
    def __init__(self, content=None, **kwargs):
        self.content = content

class OAuth2PasswordBearer:
    def __init__(self, *args, **kwargs):
        pass

class OAuth2PasswordRequestForm:
    pass

class CORSMiddleware:
    def __init__(self, *args, **kwargs):
        pass
