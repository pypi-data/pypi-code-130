import uvicorn
from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from .scripts.routers import c2dbRouter, vaspInputRouter, ribbonRouter, taskLogRouter, configRouter


class App:
    def __init__(self, host="0.0.0.0", port=8000):
        self.host = host
        self.port = port
        self.app = FastAPI(
            title="高通量纳米带计算",
            contact={
                "name": "Zhao Hao",
                "email": "601095001@qq.com",
            },
            license_info={
                "name": "Apache 2.0",
                "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
            },
        )

        @self.app.exception_handler(RequestValidationError)
        async def validation_exception_handler(request, exc: RequestValidationError):
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content=jsonable_encoder({"detail": exc.errors(), "code": status.HTTP_422_UNPROCESSABLE_ENTITY}),
            )

        self.app.include_router(ribbonRouter)
        self.app.include_router(c2dbRouter)
        self.app.include_router(vaspInputRouter)
        self.app.include_router(taskLogRouter)
        self.app.include_router(configRouter)

    def run(self):
        uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == '__main__':
    App().run()
