#!/usr/bin/env python3
"""Add a candidate source without verifying it."""

import argparse
import fcntl
import ipaddress
import json
import os
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
QUEUE = ROOT / "data/governance/source_candidates.json"


def validate_url(value):
    if not isinstance(value, str):
        raise ValueError("URL must be a string")

    if value != value.strip():
        raise ValueError("URL has surrounding whitespace")

    try:
        parsed = urlsplit(value)
        host = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise ValueError("Malformed URL") from exc

    if parsed.scheme not in ("http", "https"):
        raise ValueError("Only HTTP(S) URLs are allowed")

    if not host or parsed.username or parsed.password:
        raise ValueError("Invalid URL host or credentials")

    if any(c.isspace() for c in value):
        raise ValueError("URL contains whitespace")

    if port is not None and not 1 <= port <= 65535:
        raise ValueError("Invalid port")

    if host.lower() == "localhost":
        raise ValueError("Localhost is not a valid source")

    try:
        address = ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        if not address.is_global:
            raise ValueError("Non-public IP is not allowed")

    if "." not in host:
        raise ValueError("Host must be a domain name")

    return value


def atomic_write(path, data):
    fd, name = tempfile.mkstemp(
        prefix=".v017-",
        suffix=".tmp",
        dir=path.parent,
    )

    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()

    url = validate_url(args.url)

    if not args.notes.strip():
        parser.error("Review notes cannot be empty")

    reviews_path = (
        ROOT / "data/governance/source_reviews.json"
    )

    reviews = json.loads(
        reviews_path.read_text(encoding="utf-8")
    )

    if not isinstance(reviews, list):
        raise ValueError("Invalid source reviews")

    matches = [
        item for item in reviews
        if item.get("entity_id") == args.entity_id
    ]

    if len(matches) != 1:
        raise ValueError(
            "Entity not found or duplicated in source reviews"
        )

    review = matches[0]

    if review.get("verification_status") not in (
        "unverified",
        "under_review",
    ):
        raise ValueError("Entity is not eligible for candidates")

    data = json.loads(QUEUE.read_text(encoding="utf-8"))

    if not isinstance(data, dict):
        raise ValueError("Invalid candidate registry")

    records = data.get("records")

    if not isinstance(records, list):
        raise ValueError("Invalid candidate records")

    for record in records:
        if not isinstance(record, dict):
            raise ValueError("Invalid candidate record")

        if record.get("entity_id") == args.entity_id:
            if record.get("candidate_source_url") == url:
                raise ValueError("Duplicate source candidate")

    records.append({
        "entity_id": args.entity_id,
        "source_file": review["source_file"],
        "candidate_source_url": url,
        "review_status": "pending",
        "review_notes": args.notes.strip(),
        "ownership_verified": False,
    })

    atomic_write(QUEUE, data)

    print("SOURCE CANDIDATE ADDED")
    print("Entity:", args.entity_id)
    print("URL:", url)
    print("Status: pending")
    print("Ownership verified: NO")


def locked_main():
    """Serialize candidate registration across processes."""
    lock_path = QUEUE.with_name(QUEUE.name + ".lock")

    with open(lock_path, "a+b") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)
        try:
            return main()
        finally:
            fcntl.flock(lock.fileno(), fcntl.LOCK_UN)


if __name__ == "__main__":
    locked_main()
