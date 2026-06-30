class KnowledgeSearch:

    def search_symbols(self, query, symbols):
        query = query.lower()

        results = [
            symbol
            for symbol in symbols
            if query in symbol["name"].lower()
            or query in symbol["qualified_name"].lower()
        ]

        priority = {
            "class": 0,
            "function": 1,
            "module": 2,
        }

        return sorted(
            results,
            key=lambda item: (
                priority.get(item["kind"], 99),
                item["qualified_name"],
            ),
        )

    def search_documents(self, query, documents):
        query = query.lower()
        results = []

        for document in documents:
            content = document["content"].lower()
            title = document["title"].lower()

            if query not in content and query not in title:
                continue

            results.append(
                {
                    "path": document["path"],
                    "title": document["title"],
                    "matches": content.count(query) + title.count(query),
                }
            )

        return sorted(results, key=lambda item: (-item["matches"], item["path"]))

    def search_relationships(self, query, relationships):
        query = query.lower()

        return [
            relationship
            for relationship in relationships
            if query in relationship["source"].lower()
            or query in relationship["target"].lower()
            or query in relationship["type"].lower()
        ]
