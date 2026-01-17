#!/usr/bin/env python3
"""
Project Athena - REST API Server
Created: December 20, 2025
Fixed: December 20, 2025 - AVG query fix

Provides API access to the drug intelligence knowledge graph.
"""

import os
import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from neo4j import GraphDatabase

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASS = os.getenv("NEO4J_PASS", "Athena2025")
API_PORT = int(os.getenv("API_PORT", "8080"))

class Neo4jConnection:
    _driver = None

    @classmethod
    def get_driver(cls):
        if cls._driver is None:
            cls._driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASS))
        return cls._driver

class AthenaAPIHandler(BaseHTTPRequestHandler):

    def _send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def log_message(self, format, *args):
        print(f"[API] {args[0]}")

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        try:
            if path == "/health":
                self._send_json({"status": "healthy", "service": "athena-api"})

            elif path == "/stats":
                self._handle_stats()

            elif path == "/molecule/search":
                name = query.get("name", [""])[0]
                self._search_molecule(name)

            elif path.startswith("/molecule/"):
                cid = path.split("/")[-1]
                self._get_molecule(cid)

            elif path == "/suggest":
                disorder = query.get("disorder", [""])[0]
                self._suggest_treatments(disorder)

            else:
                self._send_json({"error": "Not found", "endpoints": [
                    "/health", "/stats", "/molecule/{cid}",
                    "/molecule/search?name=aspirin", "/suggest?disorder=headache"
                ]}, 404)
        except Exception as e:
            self._send_json({"error": str(e)}, 500)

    def _handle_stats(self):
        driver = Neo4jConnection.get_driver()
        with driver.session() as session:
            stats = session.run("""
                MATCH (m:Molecule)
                WITH count(m) as total_count,
                     avg(toFloat(m.weight)) as avg_weight
                RETURN total_count, avg_weight
            """).single()

            self._send_json({
                "molecules": stats["total_count"],
                "avg_molecular_weight": round(stats["avg_weight"], 2) if stats["avg_weight"] else 0,
                "status": "operational"
            })

    def _search_molecule(self, name):
        if not name:
            self._send_json({"error": "name parameter required"}, 400)
            return

        driver = Neo4jConnection.get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (m:Molecule)
                WHERE toLower(m.name) CONTAINS toLower($name)
                RETURN m.cid as cid, m.name as name, m.formula as formula, m.smiles as smiles
                LIMIT 20
            """, name=name)
            molecules = [dict(record) for record in result]
            self._send_json({"results": molecules, "count": len(molecules)})

    def _get_molecule(self, cid):
        try:
            cid = int(cid)
        except ValueError:
            self._send_json({"error": "Invalid CID"}, 400)
            return

        driver = Neo4jConnection.get_driver()
        with driver.session() as session:
            result = session.run("""
                MATCH (m:Molecule {cid: $cid})
                RETURN m
            """, cid=cid)
            record = result.single()
            if record:
                mol = dict(record["m"])
                self._send_json(mol)
            else:
                self._send_json({"error": "Molecule not found"}, 404)

    def _suggest_treatments(self, disorder):
        self._send_json({
            "disorder": disorder,
            "status": "Phase 1 - Basic lookup only",
            "message": "Full pathway analysis coming in Phase 2",
            "disclaimer": "Research tool only, not medical advice"
        })

def run_server():
    server = HTTPServer(("0.0.0.0", API_PORT), AthenaAPIHandler)
    print(f"Athena API running on port {API_PORT}")
    print("Endpoints: /health /stats /molecule/{cid} /molecule/search?name=X /suggest?disorder=X")
    server.serve_forever()

if __name__ == "__main__":
    run_server()
