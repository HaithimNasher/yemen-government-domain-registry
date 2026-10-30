# YNDR Evidence Governance

## Project Status

YNDR is an independent, unofficial prototype.

It is not an authorized governmental domain registry
and does not establish legal ownership of any domain.

## Evidence Registry

Evidence records are validated for:

- Required metadata
- Unique evidence identifiers
- Referenced registry entities
- Source URL structure
- Review metadata
- Domain consistency where applicable

Passing validation does not establish authenticity.

## Domain Ownership

Domain ownership must not be marked as verified
solely because metadata or a source URL exists.

Ownership verification requires independent,
documented and authorized verification procedures.

## Review Workflow

Supported review decisions:

- needs_more_information
- accepted_for_review
- rejected

The decision accepted_for_review does not mean
domain ownership has been verified.

Rejected evidence is terminal under the current
transition policy.

## Review Chronology

Different review decisions for the same evidence
on the same date are rejected as ambiguous.

Date-only records do not establish precise event order.

## Current Limitations

- No independently verified domain ownership
- No production-grade reviewer authentication
- No cryptographic audit trail
- No immutable review history
- No governmental authorization
- No production readiness certification

## Release Policy

All validators and automated tests must pass
before a release is proposed.

A passing test suite demonstrates only the
behaviors covered by those tests.
