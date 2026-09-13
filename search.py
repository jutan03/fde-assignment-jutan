"""
Natural-language search over the seeded catalogue, with an embedding-based
ranker backed by the gateway and a plain keyword fallback when the gateway
isn't configured or a call fails.
"""
import math

from catalogue import LISTINGS
from gateway import GATEWAY_CONFIGURED, EMBEDDING_MODEL, embedding_client

# In-memory cache for the catalogue's embedding vectors. Fine for a demo
# with a small, static catalogue; a real deployment would persist this.
_cached_index = None  # {"vectors": [...] or None, "mode": "embeddings" | "keyword"}


def _listing_text(item):
    return (
        f"{item['title']}. Category: {item['category']}. Condition: {item['condition']}. "
        f"Location: {item['location']}. Price: ${item['price']}. {item['description']}"
    )


def _cosine_similarity(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    denom = norm_a * norm_b
    return dot / denom if denom else 0.0


def _keyword_score(query, item):
    terms = [t for t in query.lower().split() if t]
    haystack = _listing_text(item).lower()
    return sum(1 for t in terms if t in haystack)


def _keyword_search(query, limit):
    ranked = sorted(
        ((item, _keyword_score(query, item)) for item in LISTINGS),
        key=lambda pair: pair[1],
        reverse=True,
    )
    matched = [item for item, score in ranked if score > 0][:limit]
    # If nothing matched at all, fall back to showing the full catalogue
    # rather than an empty page.
    return matched if matched else LISTINGS[:limit]


def _get_index():
    global _cached_index
    if _cached_index is not None:
        return _cached_index

    if not GATEWAY_CONFIGURED:
        _cached_index = {"vectors": None, "mode": "keyword"}
        return _cached_index

    try:
        res = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[_listing_text(item) for item in LISTINGS],
        )
        vectors = [None] * len(LISTINGS)
        for d in res.data:
            vectors[d.index] = d.embedding
        _cached_index = {"vectors": vectors, "mode": "embeddings"}
    except Exception as err:  # noqa: BLE001 - want to fall back on any failure
        print(f"[search] failed to build embedding index, using keyword search instead: {err}")
        _cached_index = {"vectors": None, "mode": "keyword"}

    return _cached_index


def search_listings(query, limit=8):
    """Returns (results, mode). mode is one of:
    - "embeddings": ranked by the gateway's embedding model
    - "keyword": gateway not configured, using substring matching
    - "keyword-fallback": gateway configured but the live call failed
    """
    index = _get_index()

    if index["mode"] == "keyword":
        return _keyword_search(query, limit), "keyword"

    try:
        query_embedding = embedding_client.embeddings.create(
            model=EMBEDDING_MODEL,
            input=[query],
        )
        q_vector = query_embedding.data[0].embedding
        ranked = sorted(
            (
                (item, _cosine_similarity(q_vector, index["vectors"][i]))
                for i, item in enumerate(LISTINGS)
            ),
            key=lambda pair: pair[1],
            reverse=True,
        )
        return [item for item, _score in ranked[:limit]], "embeddings"
    except Exception as err:  # noqa: BLE001
        print(f"[search] query embedding failed, using keyword search instead: {err}")
        return _keyword_search(query, limit), "keyword-fallback"


def retrieve_context(query, limit=5):
    results, _mode = search_listings(query, limit)
    return results
