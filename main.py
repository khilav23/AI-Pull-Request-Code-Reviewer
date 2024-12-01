from fastapi import FastAPI
from routes import router
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from fastapi.responses import JSONResponse


app = FastAPI(
    title="Code Review Agent API",
    description="An autonomous code review agent API for analyzing GitHub pull requests.",
    version="1.0.0",
)


limiter = Limiter(key_func=get_remote_address)


app.state.limiter = limiter


app.include_router(router)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Please try again later."},
    )


app.add_middleware(SlowAPIMiddleware)


@app.get("/")
def read_root():
    return {"message": "Welcome to the Code Review Agent API"}

