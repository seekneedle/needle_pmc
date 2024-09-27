from haystack import component
from haystack.dataclasses import Document
from typing import List, Optional


@component
class RetrieverAnswerBuilderComponent:
    """
      A retriever answer
      """
    @component.output_types(retriever_doc=dict)
    def run(self, documents: List[Document], threshold: Optional[float] = 0, **kwargs):
        # 生成回答，去掉不需要的属性
        if not documents:
            return {"error": "No documents found."}
        if threshold > 0:
            filtered_docs = [doc for doc in documents if doc.score > threshold]
        else:
            filtered_docs = documents
        cleaned_docs = [{"id": doc.id, "content": doc.content, "score": doc.score, "metadata": doc.meta} for doc in filtered_docs]
        return {"retriever_doc": cleaned_docs}


@component
class RetrieverHybridAnswerBuilderComponent:
    """
      A retriever answer
      """
    @component.output_types(retriever_doc=dict)
    def run(self, documents: List[Document], top_k: int, threshold: Optional[float] = 0, **kwargs):
        # 合并两个检索器的结果
        if not documents:
            return {"error": "No documents found."}
        if threshold > 0:
            filtered_docs = [doc for doc in documents if doc.score > threshold]        # 根据得分排序
        else:
            filtered_docs = documents
        sorted_docs = sorted(filtered_docs, key=lambda x: x.score, reverse=True)
        cleaned_docs = [{"id": doc.id, "content": doc.content, "score": doc.score, "metadata": doc.meta} for doc in sorted_docs]
        return {"retriever_doc": cleaned_docs[:top_k]}
