import sqlite3
from pathlib import Path

DB = (
    Path(__file__).resolve().parent.parent
    / "data/registry.db"
)

ALLOWED_CATEGORIES = {
    "governorate",
    "district",
    "ministry",
    "university",
    "company",
    "organization",
    "bank",
}


def search_entities(
    query=None,
    category=None,
    limit=20,
    offset=0,
):
    if category and category not in ALLOWED_CATEGORIES:
        raise ValueError("Invalid category")

    if not isinstance(limit, int) or not 1 <= limit <= 100:
        raise ValueError("Limit must be between 1 and 100")

    if not isinstance(offset, int) or offset < 0:
        raise ValueError("Offset must be non-negative")

    conditions = []
    params = []

    if query:
        conditions.append("""
            (
                name_ar LIKE ?
                OR name_en LIKE ?
                OR domain LIKE ?
                OR entity_id LIKE ?
            )
        """)

        pattern = f"%{query}%"
        params.extend([pattern] * 4)

    if category:
        conditions.append("category = ?")
        params.append(category)

    where = (
        " WHERE " + " AND ".join(conditions)
        if conditions else ""
    )

    with sqlite3.connect(DB) as conn:
        conn.row_factory = sqlite3.Row

        total = conn.execute(
            "SELECT COUNT(*) FROM entities" + where,
            params
        ).fetchone()[0]

        rows = conn.execute(
            """
            SELECT *
            FROM entities
            """
            + where +
            """
            ORDER BY category, name_en, entity_id
            LIMIT ? OFFSET ?
            """,
            params + [limit, offset]
        ).fetchall()

    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "results": [dict(row) for row in rows],
    }
