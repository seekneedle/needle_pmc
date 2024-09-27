from haystack_integrations.components.retrievers.elasticsearch import ElasticsearchEmbeddingRetriever

from haystack import Pipeline
from haystack.components.embedders import OpenAITextEmbedder
from custom_components.retriever_answer_builder import RetrieverAnswerBuilderComponent
from typing import Any, Dict, Optional
from utils.es_utils import ESDatabase
from custom_components.openai_similarity_ranker import OpenAISimilarityRanker


class ESEmbeddingRetrieverPipeline(object):
    def __init__(self, index_name: str, top_k: int, threshold: Optional[float] = 0, filters: Optional[Dict[str, Any]] = None, rerank_top_k: Optional[int] = None):
        self.index_name = index_name
        self.top_k = top_k
        self.filters = filters
        self.threshold = threshold

        document_store = ESDatabase(index=index_name).get_es_document_store()
        retriever = ElasticsearchEmbeddingRetriever(document_store=document_store)

        self.rag_pipeline = Pipeline()
        self.rag_pipeline.add_component("embedder", OpenAITextEmbedder(model="bge-m3"))
        self.rag_pipeline.add_component(name="retriever", instance=retriever)
        self.rag_pipeline.add_component(name="answer_builder", instance=RetrieverAnswerBuilderComponent())
        self.rag_pipeline.add_component("ranker", OpenAISimilarityRanker(top_k=rerank_top_k))

        self.rag_pipeline.connect("embedder.embedding", "retriever")
        self.rag_pipeline.connect("retriever", "ranker")
        self.rag_pipeline.connect("ranker", "answer_builder")

    def run(self, question):
        result = self.rag_pipeline.run(
            {
                "embedder": {"text": question},
                "retriever": {"filters": self.filters, "top_k": self.top_k},
                "answer_builder": {"threshold": self.threshold},
                "ranker": {"query": question}
            }
        )
        return result["answer_builder"]
