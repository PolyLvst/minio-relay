from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from service.minio_file import MinIOFileService
import routers
import routers.minio_file

class MinIORelayBackend:
    def __init__(self):
        self.__api_prefix = "/reminio/v1"
        self.__app = FastAPI(title="Relay MinIO FastAPI Backend", version="1.0.0 reminio")

    def register_routers(self):
        self.__app.include_router(router=routers.minio_file.router, prefix=self.__api_prefix, tags=["File"])
    
    def setup_config_app(self):
        self.__app.add_middleware(
            CORSMiddleware,
            allow_origins=['*'],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
    
    def startup_event(self):
        self.__app.add_event_handler("startup", MinIOFileService.create_bucket_startup)

    def get_app(self):
        self.startup_event()
        self.register_routers()
        self.setup_config_app()
        return self.__app

MinIORelay_backend = MinIORelayBackend()
app = MinIORelay_backend.get_app()