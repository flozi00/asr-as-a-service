import typesense
import os
from transformers import AutoTokenizer, AutoModel
import torch
import torch.nn.functional as F
from optimum.bettertransformer import BetterTransformer

from torch import Tensor

from atra.utilities.stats import timeit


class Embedder:
    def __init__(self, model_path: str) -> None:
        self.model = AutoModel.from_pretrained(model_path)
        if torch.cuda.is_available():
            self.model = self.model.cuda()
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.model = BetterTransformer.transform(self.model)

    def average_pool(
        self, last_hidden_states: Tensor, attention_mask: Tensor
    ) -> Tensor:
        last_hidden = last_hidden_states.masked_fill(
            ~attention_mask[..., None].bool(), 0.0
        )
        return last_hidden.sum(dim=1) / attention_mask.sum(dim=1)[..., None]

    def encode(self, sentences: list) -> torch.Tensor:
        # Tokenize the input texts
        batch_dict = self.tokenizer(
            sentences,
            max_length=512,
            padding=True,
            truncation=True,
            return_tensors="pt",
        )
        if torch.cuda.is_available():
            batch_dict = {k: v.cuda() for k, v in batch_dict.items()}

        outputs = self.model(**batch_dict)
        embeddings = self.average_pool(
            outputs.last_hidden_state, batch_dict["attention_mask"]
        )

        # normalize embeddings
        embeddings = F.normalize(embeddings, p=2, dim=1)

        return embeddings


class SemanticSearcher:
    def __init__(
        self, embedder: Embedder, api_key: str = None, collection="articles"
    ) -> None:
        self.embedder = embedder
        self.collection_name = collection
        if api_key is None:
            api_key = "xyz"
        self.client = typesense.Client(
            {
                "api_key": api_key,
                "nodes": [
                    {
                        "host": os.getenv("TYPESENSE_HOST") or "localhost",
                        "port": "8108",
                        "protocol": "http",
                    }
                ],
                "connection_timeout_seconds": 2,
            }
        )
        self.schema = {
            "name": self.collection_name,
            "fields": [
                {"name": "article", "type": "string"},
                {"name": "source", "type": "string"},
                {
                    "name": "embedding",
                    "type": "float[]",
                    "num_dim": 1024,
                },
            ],
        }

    def create_collection(self) -> None:
        self.client.collections.create(self.schema)

    @timeit
    def upsert_documents(self, articles: list, sources: list) -> None:
        for i in range(len(articles)):
            articles[i] = "passage: " + articles[i]
        embeddings = self.embedder.encode(articles)
        for article, source, embeds in zip(articles, sources, embeddings):
            document = {
                "article": article,
                "source": source,
                "embedding": embeds.tolist(),
            }
            self.client.collections[self.collection_name].documents.upsert(document)

    def delete_collection(self):
        self.client.collections[self.collection_name].delete()

    @timeit
    def semantic_search(self, query: str) -> list:
        search_params = {
            "searches": [
                {
                    "collection": self.collection_name,
                    "q": "*",
                    "vector_query": "embedding:(%s, k:50)"
                    % self.embedder.encode(["query: " + query])[0].tolist(),
                }
            ]
        }

        results = self.client.multi_search.perform(search_params, {})

        result = []
        for r in results["results"][0]["hits"]:
            if r["vector_distance"] < 0.7:
                result.append({r["document"]["source"]: r["document"]["article"]})

        return result
