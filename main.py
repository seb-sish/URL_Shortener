from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api import (
    publicRouter, privateRouter, authRouter, adminRouter,
    register_exception_handlers
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"]
)

app.include_router(privateRouter)
app.include_router(publicRouter)
app.include_router(authRouter)
app.include_router(adminRouter)
register_exception_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
