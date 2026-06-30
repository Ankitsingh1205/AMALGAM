class KnowledgeIndex:

    def build(self, documents, symbols, relationships):
        return {
            "documents": {
                document["path"]: document
                for document in documents
            },
            "symbols": {
                symbol["qualified_name"]: symbol
                for symbol in symbols
            },
            "relationships": relationships,
        }

