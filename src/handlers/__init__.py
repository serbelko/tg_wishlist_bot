from src.handlers.main_user_path import router as creation_router
from src.handlers.main_menu import base_router
from src.handlers.list_using import router as list_router
from src.handlers.add_celery import router as celery_router
routers = [creation_router, base_router,list_router, celery_router, ]
