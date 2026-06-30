from dataclasses import dataclass, field


@dataclass
class KnowledgeReport:
    documents: list[dict] = field(default_factory=list)
    symbols: list[dict] = field(default_factory=list)
    relationships: list[dict] = field(default_factory=list)
    graph: dict = field(default_factory=dict)
    summary: dict = field(default_factory=dict)

    def as_dict(self):
        return {
            "documents": self.documents,
            "symbols": self.symbols,
            "relationships": self.relationships,
            "graph": self.graph,
            "summary": self.summary,
        }

