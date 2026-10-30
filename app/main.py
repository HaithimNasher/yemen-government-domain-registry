import json
import os
import sqlite3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from app.registry_search import search_entities
from app.evidence_registry import get_evidence

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "registry.db"

def query(sql, params=()):
    with sqlite3.connect(DB) as db:
        db.row_factory = sqlite3.Row
        return [dict(r) for r in db.execute(sql, params).fetchall()]

class Handler(BaseHTTPRequestHandler):
    def respond(self, status, data):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        args = parse_qs(parsed.query, keep_blank_values=True)

        if path == "/":
            return self.respond(200, {
                "project": "Yemen National Domain Registry",
                "version": "0.5.0",
                "disclaimer": "Independent, unofficial prototype",
                "endpoints": [
                    "/health",
                    "/api/v1/entities",
                    "/api/v1/domains",
                    "/api/v1/stats",
                    "/api/v1/search",
                    "/api/v1/evidence"
                ]
            })

        if path == "/health":
            return self.respond(200, {"status": "ok"})

        if path == "/api/v1/domains":
            return self.respond(200, query(
                "SELECT * FROM national_domains ORDER BY suffix"
            ))

        if path == "/api/v1/entities":
            sql = "SELECT * FROM entities WHERE 1=1"
            params = []

            kind = args.get("category", [None])[0]
            search = args.get("search", [None])[0]

            if kind:
                sql += " AND category = ?"
                params.append(kind)

            if search:
                sql += """
                AND (name_ar LIKE ? OR name_en LIKE ?
                     OR domain LIKE ?)
                """
                term = f"%{search}%"
                params.extend([term, term, term])

            sql += " ORDER BY category, name_en LIMIT 1000"
            return self.respond(200, query(sql, params))


        if path == "/api/v1/search":
            try:
                def single(name, default=None):
                    values = args.get(name, [])
                    if len(values) > 1:
                        raise ValueError(
                            f"Repeated parameter: {name}"
                        )
                    return values[0] if values else default

                limit = int(single("limit", "20"))
                offset = int(single("offset", "0"))

                result = search_entities(
                    query=single("q"),
                    category=single("category"),
                    limit=limit,
                    offset=offset,
                )

                return self.respond(200, result)

            except ValueError as exc:
                return self.respond(400, {
                    "error": str(exc)
                })

        if path == "/api/v1/evidence":
            try:
                allowed = {"entity_id"}
                unknown = set(args) - allowed

                if unknown:
                    raise ValueError(
                        "Unsupported parameter: " +
                        sorted(unknown)[0]
                    )

                values = args.get("entity_id", [])

                if len(values) > 1:
                    raise ValueError(
                        "Repeated parameter: entity_id"
                    )

                if "entity_id" in args and not values:
                    raise ValueError(
                        "Empty parameter: entity_id"
                    )

                entity_id = values[0] if values else None

                if entity_id is not None:
                    entity_id = entity_id.strip()
                    if not entity_id:
                        raise ValueError(
                            "Empty parameter: entity_id"
                        )

                return self.respond(
                    200,
                    get_evidence(entity_id)
                )

            except ValueError as exc:
                return self.respond(400, {
                    "error": str(exc)
                })

        if path == "/api/v1/stats":
            rows = query("""
                SELECT category, COUNT(*) AS total
                FROM entities
                GROUP BY category
            """)
            return self.respond(200, {
                "total": sum(r["total"] for r in rows),
                "by_category": rows
            })

        self.respond(404, {"error": "Not found"})

if __name__ == "__main__":
    if not DB.exists():
        raise SystemExit(
            "Run python scripts/build_registry.py first"
        )
    host = os.environ.get("HOST", "127.0.0.1")
    port = int(os.environ.get("PORT", "8000"))
    print(f"YNDR running at http://{host}:{port}")
    ThreadingHTTPServer((host, port), Handler).serve_forever()
