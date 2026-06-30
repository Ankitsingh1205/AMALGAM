class KnowledgeGraph:

    def build(self, symbols, relationships):
        nodes = {}
        edges = []

        for symbol in symbols:
            nodes[symbol["qualified_name"]] = {
                "id": symbol["qualified_name"],
                "label": symbol["name"],
                "type": symbol["kind"],
            }

        for relationship in relationships:
            nodes.setdefault(
                relationship["source"],
                {
                    "id": relationship["source"],
                    "label": relationship["source"].split(".")[-1],
                    "type": "module",
                },
            )
            nodes.setdefault(
                relationship["target"],
                {
                    "id": relationship["target"],
                    "label": relationship["target"].split(".")[-1],
                    "type": "external",
                },
            )
            edges.append(
                {
                    "source": relationship["source"],
                    "target": relationship["target"],
                    "type": relationship["type"],
                }
            )

        return {
            "nodes": list(nodes.values()),
            "edges": edges,
        }

