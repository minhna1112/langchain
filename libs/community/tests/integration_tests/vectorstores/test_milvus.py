"""Test Milvus functionality."""
from typing import List, Optional

from langchain_core.documents import Document

from langchain_community.vectorstores import Milvus
from tests.integration_tests.vectorstores.fake_embeddings import (
    FakeEmbeddings,
    fake_texts,
)


def _milvus_from_texts(
    metadatas: Optional[List[dict]] = None,
    ids: Optional[List[str]] = None,
    drop: bool = True,
) -> Milvus:
    return Milvus.from_texts(
        fake_texts,
        FakeEmbeddings(),
        metadatas=metadatas,
        ids=ids,
        connection_args={"host": "127.0.0.1", "port": "19530"},
        drop_old=drop,
    )


def test_milvus() -> None:
    """Test end to end construction and search."""
    docsearch = _milvus_from_texts()
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo")]


def test_milvus_with_metadata() -> None:
    """Test with metadata"""
    docsearch = _milvus_from_texts(metadatas=[{"label": "test"}] * len(fake_texts))
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo", metadata={"label": "test"})]


def test_milvus_with_id() -> None:
    """Test with ids"""
    ids = ["id_" + str(i) for i in range(len(fake_texts))]
    docsearch = _milvus_from_texts(ids=ids)
    output = docsearch.similarity_search("foo", k=1)
    assert output == [Document(page_content="foo")]

    output = docsearch.delete(ids=ids)
    assert output.delete_count == len(fake_texts)

    try:
        ids = ["dup_id" for _ in fake_texts]
        _milvus_from_texts(ids=ids)
    except Exception as e:
        assert isinstance(e, AssertionError)


def test_milvus_with_score() -> None:
    """Test end to end construction and search with scores and IDs."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": i} for i in range(len(texts))]
    docsearch = _milvus_from_texts(metadatas=metadatas)
    output = docsearch.similarity_search_with_score("foo", k=3)
    docs = [o[0] for o in output]
    scores = [o[1] for o in output]
    assert docs == [
        Document(page_content="foo", metadata={"page": 0}),
        Document(page_content="bar", metadata={"page": 1}),
        Document(page_content="baz", metadata={"page": 2}),
    ]
    assert scores[0] < scores[1] < scores[2]


def test_milvus_max_marginal_relevance_search() -> None:
    """Test end to end construction and MRR search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": i} for i in range(len(texts))]
    docsearch = _milvus_from_texts(metadatas=metadatas)
    output = docsearch.max_marginal_relevance_search("foo", k=2, fetch_k=3)
    assert output == [
        Document(page_content="foo", metadata={"page": 0}),
        Document(page_content="baz", metadata={"page": 2}),
    ]


def test_milvus_add_extra() -> None:
    """Test end to end construction and MRR search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": i} for i in range(len(texts))]
    docsearch = _milvus_from_texts(metadatas=metadatas)

    docsearch.add_texts(texts, metadatas)

    output = docsearch.similarity_search("foo", k=10)
    assert len(output) == 6


def test_milvus_no_drop() -> None:
    """Test end to end construction and MRR search."""
    texts = ["foo", "bar", "baz"]
    metadatas = [{"page": i} for i in range(len(texts))]
    docsearch = _milvus_from_texts(metadatas=metadatas)
    del docsearch

    docsearch = _milvus_from_texts(metadatas=metadatas, drop=False)

    output = docsearch.similarity_search("foo", k=10)
    assert len(output) == 6


# if __name__ == "__main__":
#     test_milvus()
#     test_milvus_with_metadata()
#     test_milvus_with_score()
#     test_milvus_max_marginal_relevance_search()
#     test_milvus_add_extra()
#     test_milvus_no_drop()
