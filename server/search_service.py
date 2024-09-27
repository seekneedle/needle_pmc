# search_service.py
from core.es_bm25_retriever_pipeline import ESBM25RetrieverPipeline
from core.es_embedding_retriever_pipeline import ESEmbeddingRetrieverPipeline
from core.es_hybrid_retriever_pipeline import ESHybridRetrieverPipeline
from utils.es_utils import ESDatabase
from utils.db_utils import ConnectSQL
from pydantic import BaseModel
from typing import Any, Dict, Optional


class SearchServiceError(Exception):
    """自定义异常类，用于搜索服务错误"""


class SearchRequestEntity(BaseModel):
    text: str
    mode: Optional[str] = '1'
    top_k: Optional[int] = 10
    rerank_top_k: Optional[int] = None
    threshold: Optional[float] = None
    filters: Optional[Dict[str, Any]] = None


# /v1/vector_stores/{vector_store_id}/search
# vector_store_id str 必选 向量知识库的id
# need_rerank  bool  可选 是否rerank，默认不rerank
# mode         str        检索模式，如全文检索，语意检索，混合检索
# filters         str        haystack元组检索条件
# top_k         int        查询前多少条
# threshold         int        如果设置后，只返回score超过阈值的的结果
# text  str  必选   查询内容
def search_service(body: SearchRequestEntity, vector_store_id):
    vector_store = ConnectSQL().check_index_id_exists(vector_store_id)
    if not vector_store:
        raise SearchServiceError(" vector_store not exist")

    filenames = ESDatabase(index=str(vector_store_id)).get_all_filenames()
    if len(filenames) == 0:
        raise SearchServiceError(" vector has no files any more")

    if body.text:
        # 1. haystack 查询
        if body.mode == "1":  # 全文检索
            pipeline = ESBM25RetrieverPipeline(index_name=vector_store_id, top_k=body.top_k, threshold=body.threshold, filters=body.filters, rerank_top_k=body.rerank_top_k)
            result = pipeline.run(body.text)
        elif body.mode == "2":  # 语义检索
            pipeline = ESEmbeddingRetrieverPipeline(index_name=vector_store_id, top_k=body.top_k, threshold=body.threshold, filters=body.filters, rerank_top_k=body.rerank_top_k)
            result = pipeline.run(body.text)
        elif body.mode == "3":  # 混合检索
            pipeline = ESHybridRetrieverPipeline(index_name=vector_store_id, top_k=body.top_k, threshold=body.threshold, filters=body.filters, rerank_top_k=body.rerank_top_k)
            result = pipeline.run(body.text)
        return result
    else:
        raise SearchServiceError(" search text can not be null")


def search_from_es(text):
    return []
