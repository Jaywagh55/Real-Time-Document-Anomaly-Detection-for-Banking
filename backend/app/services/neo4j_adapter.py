"""Simple Neo4j adapter stub.

This module provides a pluggable interface that will attempt to use the `neo4j` driver
if available, otherwise it falls back to no-op implementations so the codebase remains runnable.
"""
from typing import Any, Dict, List


class Neo4jAdapter:
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        try:
            from neo4j import GraphDatabase

            self._driver = GraphDatabase.driver(uri or "bolt://localhost:7687", auth=(user or "neo4j", password or "neo4j"))
            self.available = True
        except Exception:
            self._driver = None
            self.available = False

    def close(self):
        if self._driver:
            self._driver.close()

    def write_entities(self, entities: List[Dict[str, Any]]):
        if not self.available:
            return {"status": "noop", "written": 0}
        # Implement write logic when driver is configured
        with self._driver.session() as session:
            # Placeholder: user should implement their Cypher queries here
            return {"status": "ok", "written": len(entities)}

    def query_shared_entities(self, key: str, value: str) -> List[Dict[str, Any]]:
        if not self.available:
            return []
        with self._driver.session() as session:
            # Placeholder: implement queries returning matching nodes/relationships
            return []
