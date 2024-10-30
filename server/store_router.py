from fastapi import APIRouter, Depends
import traceback
from utils import log
from services.create_store import create_store, CreateStoreEntity
from .auth import get_current_username


store_router = APIRouter(prefix="/vector_store", dependencies=[Depends(get_current_username)])


# 1. 创建知识库
@store_router.post('/create')
async def vector_store_create(request: CreateStoreEntity):
    """
        创建向量知识库：支持pdf、docx、doc、txt、md文件上传，切分。
    """
    return "OK"
