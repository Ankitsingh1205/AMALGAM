from knowledge.documents import DocumentReader
from knowledge.graph import KnowledgeGraph
from knowledge.index import KnowledgeIndex
from knowledge.relationships import RelationshipBuilder
from knowledge.report import KnowledgeReport
from knowledge.search import KnowledgeSearch
from knowledge.symbols import SymbolIndex
from workspace import Workspace


class KnowledgeEngine:

    def __init__(self, start_path="."):
        self.workspace = Workspace(start_path)
        self.documents = DocumentReader()
        self.symbols = SymbolIndex()
        self.relationships = RelationshipBuilder()
        self.graph = KnowledgeGraph()
        self.index_builder = KnowledgeIndex()
        self.search = KnowledgeSearch()

    def build(self):
        workspace_report = self.workspace.report()
        root = workspace_report.project.root
        paths = self.workspace.scan()
        documents = self.documents.read(root)
        symbols = self.symbols.build(root, paths)
        relationships = self.relationships.build(
            root,
            paths,
            workspace_report.project.python_packages,
        )
        graph = self.graph.build(symbols, relationships)

        return KnowledgeReport(
            documents=documents,
            symbols=symbols,
            relationships=relationships,
            graph=graph,
            summary=self.summary(documents, symbols, relationships, graph),
        )

    def index(self):
        report = self.build()

        return self.index_builder.build(
            report.documents,
            report.symbols,
            report.relationships,
        )

    def search_symbols(self, query):
        return self.search.search_symbols(query, self.build().symbols)

    def search_documents(self, query):
        return self.search.search_documents(query, self.build().documents)

    def search_relationships(self, query):
        return self.search.search_relationships(query, self.build().relationships)

    def summary(self, documents, symbols, relationships, graph):
        return {
            "document_count": len(documents),
            "symbol_count": len(symbols),
            "module_count": len([item for item in symbols if item["kind"] == "module"]),
            "class_count": len([item for item in symbols if item["kind"] == "class"]),
            "function_count": len([item for item in symbols if item["kind"] == "function"]),
            "relationship_count": len(relationships),
            "graph_node_count": len(graph["nodes"]),
            "graph_edge_count": len(graph["edges"]),
        }

