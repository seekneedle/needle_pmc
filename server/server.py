import uvicorn
import base64
from fastapi.responses import JSONResponse
from config import config
from .router import run_in_threadpool
from security import sha256_encode
from fastapi import FastAPI
from .router import router

def verify_credentials(cre_username, cre_password):
    username = config['username']
    password = config['password']
    if cre_username == username and sha256_encode(cre_password) == password:
        return True
    return False


def get_credentials(request):
    credentials = None
    if request.headers.get('Authorization'):
        scheme, _, token = request.headers['Authorization'].partition(' ')
        if scheme.lower() == 'basic':
            decoded_token = base64.b64decode(token).decode('utf-8')
            username, _, password = decoded_token.partition(':')
            if verify_credentials(username, password):
                credentials = username
    return credentials


def create_middleware():
    @app.middleware('http')
    async def basic_auth_middleware(request, call_next):
        if request.url.path in ["/docs", "/openapi.json"]:
            return await call_next(request)
        credentials = await run_in_threadpool(get_credentials, request)
        if not credentials:
            return JSONResponse({'detail': 'Invalid credentials'}, status_code=401)
        response = await call_next(request)
        return response


def create_app() -> FastAPI:
    app = FastAPI()
    # 包含路由
    app.include_router(router)

    return app


app = create_app()


def start_server():
    create_middleware()
    ip = config['ip']
    port = config['port']
    uvicorn.run(app, host=ip, port=port)
    # uvicorn.run(app="server.router:app", host=ip, port=port,reload=True,workers=1)

