# YNDR HTTP API

Base URL: http://127.0.0.1:8000

## Endpoints

### GET /
Returns project information and available endpoints.

### GET /health
Returns server health status.

### GET /api/v1/entities
Lists registry entities with optional category and search filters.

### GET /api/v1/domains
Lists national domain suffix records.

### GET /api/v1/stats
Returns entity totals grouped by category.

### GET /api/v1/search
Searches registry entities.

Parameters:
- q: optional search term
- category: optional entity category
- limit: integer from 1 to 100, default 20
- offset: non-negative integer, default 0

Examples:

GET /api/v1/search?q=صنعاء

GET /api/v1/search?category=ministry

GET /api/v1/search?category=university&limit=10

## Disclaimer

YNDR is an independent, unofficial prototype.
Registry inclusion does not establish government recognition,
domain registration, or verified domain ownership.

## Institutional Evidence API (v0.5.0)

### GET /api/v1/evidence

Returns institutional evidence records.

Optional query parameter:

- `entity_id`: filter by institution identifier.

Examples:

```text
GET /api/v1/evidence
GET /api/v1/evidence?entity_id=YE-UNI-SANAA
```

Successful response:

```json
{
  "total": 1,
  "results": [
    {
      "entity_id": "YE-UNI-SANAA",
      "evidence_type": "institution_website",
      "source_url": "https://su.edu.ye",
      "domain": "su.edu.ye",
      "review_status": "pending",
      "ownership_verified": false,
      "verified_at": null,
      "notes": "Institution-domain association requires authoritative verification."
    }
  ]
}
```

Invalid, empty, or repeated parameters return HTTP 400.

This registry is an independent, unofficial prototype.
Website availability and internal record consistency do not
establish institutional ownership or official endorsement.
