from app.api import roles, users, auth
from app.core.database import Base, engine
from app.models import role
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors: Dict[str, str] = {}

    for err in exc.errors():
        loc = err.get("loc")
        if loc and len(loc) > 1:
            field = loc[1]
            errors[field] = err.get("msg")

    return JSONResponse(
        status_code=422,
        content={"errors": errors}
    )

app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(roles.router, prefix="/api")

# uvicorn app.main:app --reload
# source venv/bin/activate