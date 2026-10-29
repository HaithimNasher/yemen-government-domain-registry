# Yemen National Domain Registry (YNDR)

An independent open-source prototype for cataloguing
Yemeni national, government, academic, commercial
and non-profit domains.

## Version
0.2.0

## Scope
- National domain categories
- Ministries and government agencies
- 22 governorates
- Districts
- Universities
- Companies
- Organizations

## Features
- SQLite registry
- Read-only REST API
- Entity search and filtering
- Proposed domain naming
- Domain ownership verification fields
- Arabic and English entity names

## Quick Start
python scripts/seed_data.py
python scripts/build_registry.py
python app/main.py

## API
GET /health
GET /api/v1/domains
GET /api/v1/entities
GET /api/v1/entities?category=governorate
GET /api/v1/entities?search=Ibb
GET /api/v1/stats

## Important
This is an independent and unofficial technical project.
It is not endorsed by or affiliated with the Government
of Yemen or the .ye registry operator.

Proposed domains are not evidence of ownership.
The project does not register or control domains.

## License
MIT
