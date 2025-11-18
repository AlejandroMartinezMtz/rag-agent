from . import (
    rag_query,
    list_corpora,
    add_data,
    create_corpus,
    delete_corpus,
    delete_document,
    get_corpus_info,
)

TOOLS_MAP = {
    "rag_query": rag_query,
    "list_corpora": list_corpora,
    "add_data_corpus": add_data,
    "create_corpus": create_corpus,
    "delete_corpus": delete_corpus,
    "delete_document": delete_document,
    "get_corpus_info": get_corpus_info,
}
