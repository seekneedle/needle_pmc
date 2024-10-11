import asyncio
import json
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import faithfulness, answer_correctness,context_recall,context_precision,answer_relevancy,context_entity_recall,answer_similarity
from ragas.llms.base import LangchainLLMWrapper
from ragas.embeddings.base import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
import nest_asyncio
from langchain_openai import ChatOpenAI,OpenAIEmbeddings
from config import config

def get_score(data_samples):
    if data_samples is None:
        return 'no data_samples'
        
    data_metrics=data_samples['metrics']
    del data_samples['metrics']

    print(data_metrics)
    print(data_samples)

    metrics = []
    if 'faithfulness' in data_metrics:
        metrics.append(faithfulness)
    if 'answer_correctness' in data_metrics:
        metrics.append(answer_correctness)
    if 'context_recall' in data_metrics:
        metrics.append(context_recall)
    if 'context_precision' in data_metrics:
        metrics.append(context_precision)
    if 'context_relevancy' in data_metrics:
        metrics.append(context_precision)
    if 'answer_relevancy' in data_metrics:
        metrics.append(answer_relevancy)
    if 'context_entity_recall' in data_metrics:
        metrics.append(context_entity_recall)
    if 'answer_similarity' in data_metrics:
        metrics.append(answer_similarity)

    # if 'aspect_critique' in data_metrics:
    #     metrics.append(aspect_critique)

    nest_asyncio.apply()
    one_api_key = config['api_key']
    one_api_url = config['base_url']
    model_llm = ChatOpenAI(
        model="sf/Qwen1.5-7B-Chat" if 'answer_relevancy' in data_metrics  else "ds/deepseek-chat",
        api_key=one_api_key,  
        base_url=one_api_url
    )
    model_embeddings = OpenAIEmbeddings(
        model="bge-m3",
        base_url=one_api_url,
        api_key=one_api_key,
        openai_api_type="open-ai"
    )

    wrapper_llm = LangchainLLMWrapper(model_llm)
    wrapper_embeddings = LangchainEmbeddingsWrapper(model_embeddings)

    dataset = Dataset.from_dict(data_samples)
    score = evaluate(dataset,
                    metrics,
                    llm=wrapper_llm,
                    embeddings=wrapper_embeddings,
                    raise_exceptions=False)
    print(score)
    return score