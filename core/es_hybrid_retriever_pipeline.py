from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever, ElasticsearchBM25Retriever

from haystack import Pipeline
from haystack.components.embedders import OpenAITextEmbedder
from custom_components.retriever_answer_builder import RetrieverHybridAnswerBuilderComponent
from typing import Any, Dict, Optional
from utils.es_utils import ESDatabase
from custom_components.openai_similarity_ranker import OpenAISimilarityRanker


class ESHybridRetrieverPipeline(object):
    def __init__(self, index_name: str, top_k: int, threshold: Optional[float] = 0, filters: Optional[Dict[str, Any]] = None, rerank_top_k: Optional[int] = None):
        self.index_name = index_name
        self.top_k = top_k
        self.filters = filters
        self.threshold = threshold

        document_store = ESDatabase(index=index_name).get_es_document_store()
        bm25_retriever = ElasticsearchBM25Retriever(document_store=document_store)
        embedding_retriever = ElasticsearchEmbeddingRetriever(document_store=document_store)

        self.rag_pipeline = Pipeline()
        self.rag_pipeline.add_component("embedder", OpenAITextEmbedder(model="bge-m3"))
        self.rag_pipeline.add_component(name="bm25_retriever", instance=bm25_retriever)
        self.rag_pipeline.add_component(name="embedding_retriever", instance=embedding_retriever)
        self.rag_pipeline.add_component(name="answer_builder", instance=RetrieverHybridAnswerBuilderComponent())
        self.rag_pipeline.add_component("ranker", OpenAISimilarityRanker(top_k=rerank_top_k))

        self.rag_pipeline.connect("embedder.embedding", "embedding_retriever")
        self.rag_pipeline.connect("bm25_retriever.documents", "ranker.documents")
        self.rag_pipeline.connect("embedding_retriever.documents", "ranker.embedding_documents")
        self.rag_pipeline.connect("ranker", "answer_builder")

    def run(self, question):
        result = self.rag_pipeline.run(
            {
                "embedder": {"text": question},
                "embedding_retriever": {"filters": self.filters, "top_k": self.top_k},
                "bm25_retriever": {"query": question, "filters": self.filters, "top_k": self.top_k},
                "answer_builder": {"top_k": self.top_k, "threshold": self.threshold},
                "ranker": {"query": question}
            }
        )
        return result["answer_builder"]
