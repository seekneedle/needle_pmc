from fastapi import Request, APIRouter
import asyncio
import os
from pydantic import BaseModel
from typing import List
from server.search_service import search_service, SearchServiceError
from server.create_service import create_service
from server.upload_service import upload_service
from utils.es_utils import ESDatabase
from elasticsearch.exceptions import NotFoundError
from utils.db_utils import ConnectSQL
from utils.ragas_utils import get_score
from utils.files_utils import delete_directory,delete_file
from config import config
from .search_service import SearchRequestEntity
import traceback
from log import log


router = APIRouter()


async def run_in_threadpool(fn, *args):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, fn, *args)


class FileEntity(BaseModel):
    file_name: str   
    file_type: str = 'txt' 
    language: str = 'cn'
    file_base64: str


class StrategyEntity(BaseModel):
    chunk_type: int = 0    
    max_tokens: int = 200 
    overlap: int = 30       
    separator: str = 'word'


class KnowledgeCreate(BaseModel):  
    files: List[FileEntity] = []
    name: str   
    chunking_strategy: StrategyEntity  


class KnowledgeUpload(BaseModel):  
    files: List[FileEntity] = [] 
    chunking_strategy: StrategyEntity


# 1. 创建知识库
@router.post('/vector_stores/create')
async def vector_stores_create(request: KnowledgeCreate):       
    try:
        body = request.dict()
        index_id, filenames = create_service(body)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/create, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
            'status': 200,
            'data': {"index_id": int(index_id),
                     "filenames": filenames}
    }


# 2.查询向量知识库中的文件
@router.get('/vector_stores/{vector_store_id}/files')
async def get_vector_stores_files(vector_store_id: str):
    try:
        if(not ConnectSQL().check_index_id_exists(vector_store_id)):
            raise Exception("知识库不存在")
        filenames = ESDatabase(index=str(vector_store_id)).get_all_filenames()
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/{vector_store_id}/files, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
            'status': 200,
            'data': {"index_id":int(vector_store_id),
                    "filenames":filenames}
    }


# 3.查询所有知识库id
@router.get('/vector_stores/get_all_vector_store')
async def get_all_vector_stores():
    try:
        result = ConnectSQL().get_all_index_ids()
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/get_all_vector_store, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
            'status': 200,
            'data': result
    }


# 4. 删除向量知识库 https://kdb.homecredit.cn/display/IT/RAG+design
@router.delete('/vector_stores/{vector_store_id}')
async def del_vector_stores(vector_store_id: str):
    try:
        if(not ConnectSQL().check_index_id_exists(vector_store_id)):
            raise Exception("知识库不存在")
        ESDatabase().delete_document_store_by_index(vector_store_id)
        ConnectSQL().delete_index_name(vector_store_id)
        indexpath = os.path.join(config['filestore_root_dir'],str(vector_store_id))
        delete_directory(indexpath)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/{vector_store_id}, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'id': vector_store_id,
                'status':f"failed",
                'content': str(e)
            }
        }
    return {
        'status': 200,
        'data': {
            'id': vector_store_id,
            'status':f"success"
        }
    }


# 5. 向量知识库上传/更新文件
@router.post('/vector_stores/{vector_store_id}/upload')
async def vector_stores_upload_file(vector_store_id:str, request: KnowledgeUpload):
    try:
        body = request.dict()
        filenames = upload_service(body,vector_store_id)        
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/{vector_store_id}/upload, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return{
            'status': 200,
            'data': {"index_id":int(vector_store_id),
                    "filenames":filenames}
    }


# 6. 向量知识库删除文件
@router.delete('/vector_stores/{vector_store_id}/files/{file_id}')
async def del_vector_stores_file(vector_store_id: str, file_id: str):
    try:
        if(not ConnectSQL().check_index_id_exists(vector_store_id)):
            raise Exception("知识库不存在")
        ESDatabase(index=str(vector_store_id)).delete_documents_by_filename(file_id)
        file_path = os.path.join(config['filestore_root_dir'],str(vector_store_id),file_id)
        delete_file(file_path)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/{vector_store_id}/files/{file_id}, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
        'data': {
            'file_id': file_id,
            'status': f"success"
        }
    }


# 7. 查询文件chunks
@router.get('/vector_stores/{vector_store_id}/chunks/{file_name}')
async def get_vector_stores_chunk(vector_store_id:str,file_name:str):
    try:
        if(not ConnectSQL().check_index_id_exists(vector_store_id)):
            raise Exception("知识库不存在")
        result = ESDatabase(index=str(vector_store_id)).get_chunks_by_filename(file_name)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for /vector_stores/{vector_store_id}/chunks/{file_name}, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
        'data': result
    }


# 8. 更新chunk的元组信息--TODO
@router.post('/vector_stores/{vector_store_id}/file/{file_id}')
async def update_vector_stores_chunk(request: Request):
    try:
        body = await request.json()
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"vector_stores//file/, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
    }


# 9. RAG检索
@router.post('/vector_stores/{vector_store_id}/search')
async def vector_stores_search(vector_store_id: str, search_entity: SearchRequestEntity):
    try:
        search_list = await run_in_threadpool(search_service, search_entity, vector_store_id)
    except SearchServiceError as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for vector_stores/{vector_store_id}/search, e: {e}, trace: {trace_info}")
        return {
            'status': 403,
            'data': {
                'content': str(e)
            }
        }
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for vector_stores/{vector_store_id}/search, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
        'data': search_list
    }


# 10. RAGAS评分
@router.post('/ragas/score')
async def vector_stores_ragas_score(request: Request):
    try:
        body = await request.json()
        score = get_score(body)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for vector_stores//ragas/score, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
        'data': f"{score}"
    }


# 11. RAGAS评分(csv)
@router.post('/ragas/score/csv')
async def vector_stores_ragas_score_csv(request: Request):
    try:
        body = await request.json()
        # 先解析csv文件 然后调用get_score
        # score = await get_score(body)
    except Exception as e:
        trace_info = traceback.format_exc()
        log.info(f"Exception for vector_stores/ragas/score/csv, e: {e}, trace: {trace_info}")
        return {
            'status': 401,
            'data': {
                'content': str(e)
            }
        }
    return {
        'status': 200,
        # 'data': f"{score}"
    }
