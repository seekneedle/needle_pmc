from haystack import Document, component
from typing import List, Optional
from xinference_client import RESTfulClient as Client


@component
class OpenAISimilarityRanker:
    def __init__(
        self,
        model: str = "bge-reranker-large",
        top_k: int = Optional[int],
        query_prefix: str = "",
        document_prefix: str = "",
        meta_fields_to_embed: Optional[List[str]] = None,
        embedding_separator: str = "\n",
        scale_score: bool = True,
        calibration_factor: Optional[float] = 1.0,
        score_threshold: Optional[float] = None,
    ):
        """
        Creates an instance of TransformersSimilarityRanker.

        :param model:
            The name from oneapi.
        :param top_k:
            The maximum number of Documents to return per query.
        :param query_prefix:
            A string to add to the beginning of the query text before ranking.
            Can be used to prepend the text with an instruction, as required by some reranking models, such as bge.
        :param document_prefix:
            A string to add to the beginning of each Document text before ranking. Can be used to prepend the text with
            an instruction, as required by some embedding models, such as bge.
        :param meta_fields_to_embed:
            List of meta fields that should be embedded along with the Document content.
        :param embedding_separator:
            Separator used to concatenate the meta fields to the Document content.
        :param scale_score:
            Whether the raw logit predictions will be scaled using a Sigmoid activation function.
            Set this to False if you do not want any scaling of the raw logit predictions.
        :param calibration_factor:
            Factor used for calibrating probabilities calculated by `sigmoid(logits * calibration_factor)`.
            This is only used if `scale_score` is set to True.
        :param score_threshold:
            If provided only returns documents with a score above this threshold.

        :raises ValueError:
            If `top_k` is not > 0.
            If `scale_score` is True and `calibration_factor` is not provided.
        """

        self.model = model
        self.query_prefix = query_prefix
        self.document_prefix = document_prefix
        self.top_k = top_k
        self.meta_fields_to_embed = meta_fields_to_embed or []
        self.embedding_separator = embedding_separator
        self.scale_score = scale_score
        self.calibration_factor = calibration_factor
        self.score_threshold = score_threshold

        # Parameter validation
        if self.scale_score and self.calibration_factor is None:
            raise ValueError(
                f"scale_score is True so calibration_factor must be provided, but got {calibration_factor}"
            )
        self._xinference = 'http://10.26.9.148:9997'

    @component.output_types(documents=List[Document])
    def run(
            self,
            query: str,
            documents: List[Document],
            scale_score: Optional[bool] = None,
            calibration_factor: Optional[float] = None,
            embedding_documents: Optional[List[Document]] = None,
            score_threshold: Optional[float] = None,
    ):
        """
        Returns a list of Documents ranked by their similarity to the given query.

        :param query:
            Query string.
        :param documents:
            List of Documents.
        :param top_k:
            The maximum number of Documents you want the Ranker to return.
        :param scale_score:
            Whether the raw logit predictions will be scaled using a Sigmoid activation function.
            Set this to False if you do not want any scaling of the raw logit predictions.
        :param calibration_factor:
            Factor used for calibrating probabilities calculated by
            `sigmoid(logits * calibration_factor)`. This is only used if `scale_score` is set to True.
        :param score_threshold:
            If provided only returns documents with a score above this threshold.
        :returns:
            A dictionary with the following keys:
            - `documents`: List of Documents most similar to the given query in descending order of similarity.

        :raises ValueError:
            If `top_k` is not > 0.
            If `scale_score` is True and `calibration_factor` is not provided.
        :raises RuntimeError:
            If the model is not loaded because `warm_up()` was not called before.
        """
        # If a model path is provided but the model isn't loaded
        if self.top_k is None:
            return {"documents": documents}
        if embedding_documents is not None:
            documents = documents + embedding_documents
        rerank_model = Client(self._xinference).get_model(self.model)
        docs = []
        docs_dict = {}
        for doc in documents:
            docs.append(doc.content)
            docs_dict[doc.content] = doc
        results = rerank_model.rerank(documents=docs, query=query, return_documents=True)['results']

        out_docs = []
        for i, result in enumerate(results):
            doc = docs_dict[result['document']['text']]
            doc.score = result['relevance_score']
            if i < self.top_k:
                if score_threshold is not None and doc.score > score_threshold:
                    out_docs.append(doc)
                elif score_threshold is None:
                    out_docs.append(doc)
                else:
                    break
            else:
                break

        return {"documents": out_docs}


if __name__ == '__main__':
    documents = [
        Document(
            content="Use pip to install a basic version of Haystack's latest release: pip install farm-haystack. All "
                    "the core Haystack components live in the haystack repo. But there's also the haystack-extras "
                    "repo which contains components that are not as widely used, and you need to install them "
                    "separately."
        ),
        Document(
            content="Use pip to install a basic version of Haystack's latest release: pip install farm-haystack["
                    "inference]. All the core Haystack components live in the haystack repo. But there's also the "
                    "haystack-extras repo which contains components that are not as widely used, and you need to "
                    "install them separately."
        ),
        Document(
            content="Use pip to install only the Haystack 2.0 code: pip install haystack-ai. The haystack-ai package "
                    "is built on the main branch which is an unstable beta version, but it's useful if you want to "
                    "try the new features as soon as they are merged."
        ),
    ]
    rancher = OpenAISimilarityRanker(top_k=2)
    output_docs = rancher.run(query='Please introduce the second version of haystack.', documents=documents)
    print(output_docs)
