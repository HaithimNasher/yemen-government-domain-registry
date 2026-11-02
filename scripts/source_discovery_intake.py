#!/usr/bin/env python3
"""Register a discovered source for human review."""

import argparse
import sys
from datetime import date

from scripts import add_source_candidate


def main():
    parser = argparse.ArgumentParser(
        description="Register a discovered source candidate"
    )
    parser.add_argument("--entity-id", required=True)
    parser.add_argument("--url", required=True)
    parser.add_argument("--discovered-from", required=True)
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()

    if not args.discovered_from.strip():
        parser.error("Discovery origin is required")

    if not args.notes.strip():
        parser.error("Discovery notes are required")

    try:
        url = add_source_candidate.validate_url(args.url)
    except ValueError as exc:
        parser.error(f"Invalid source URL: {exc}")

    discovery_notes = (
        f"Discovered at: {date.today().isoformat()}; "
        f"Discovery origin: {args.discovered_from.strip()}; "
        f"Notes: {args.notes.strip()}"
    )

    original_argv = sys.argv

    try:
        sys.argv = [
            "add_source_candidate.py",
            "--entity-id", args.entity_id,
            "--url", url,
            "--notes", discovery_notes,
        ]

        add_source_candidate.locked_main()
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    main()
