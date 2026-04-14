import sys
import types
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _install_sentence_transformers_stub() -> None:
    module = types.ModuleType("sentence_transformers")

    class SentenceTransformer:
        def __init__(self, model_name: str) -> None:
            self.model_name = model_name

        def get_sentence_embedding_dimension(self) -> int:
            return 3

        def encode(self, text: str, normalize_embeddings: bool = True):
            class FakeEmbedding:
                def __init__(self, values: list[float]) -> None:
                    self._values = values

                def tolist(self) -> list[float]:
                    return self._values

            length = float(len(text))
            return FakeEmbedding([length, length / 10, 1.0 if normalize_embeddings else 0.0])

    module.SentenceTransformer = SentenceTransformer
    sys.modules["sentence_transformers"] = module


def _install_qdrant_stub() -> None:
    qdrant_client_module = types.ModuleType("qdrant_client")
    http_module = types.ModuleType("qdrant_client.http")
    models_module = types.ModuleType("qdrant_client.http.models")

    class QdrantClient:
        def __init__(self, *args, **kwargs) -> None:
            self.args = args
            self.kwargs = kwargs

        def get_collections(self):
            return []

        def recreate_collection(self, **kwargs) -> None:
            self.recreate_collection_kwargs = kwargs

        def upsert(self, **kwargs) -> None:
            self.upsert_kwargs = kwargs

        def search(self, **kwargs):
            return []

    class VectorParams:
        def __init__(self, size: int, distance: str) -> None:
            self.size = size
            self.distance = distance

    class PointStruct:
        def __init__(self, id: int, vector: list[float], payload: dict) -> None:
            self.id = id
            self.vector = vector
            self.payload = payload

    class Distance:
        COSINE = "cosine"

    models_module.VectorParams = VectorParams
    models_module.PointStruct = PointStruct
    models_module.Distance = Distance

    qdrant_client_module.QdrantClient = QdrantClient
    http_module.models = models_module

    sys.modules["qdrant_client"] = qdrant_client_module
    sys.modules["qdrant_client.http"] = http_module
    sys.modules["qdrant_client.http.models"] = models_module


_install_sentence_transformers_stub()
_install_qdrant_stub()
