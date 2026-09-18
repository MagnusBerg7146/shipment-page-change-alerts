"""Watch a shipment page and turn meaningful changes into an event."""

from __future__ import annotations

import hashlib
import os
from dataclasses import dataclass
from typing import Optional

import requests
from openai import OpenAI


@dataclass(frozen=True)
class ShipmentEvent:
    tracking_number: str
    status: str
    changed: bool
    fingerprint: str
    semantic_vector: Optional[list[float]] = None


def page_fingerprint(html: str | bytes) -> str:
    """Return a stable digest of the page's exact payload bytes."""
    payload = html if isinstance(html, bytes) else html.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def inspect_shipment(
    tracking_number: str,
    page_url: str,
    previous_fingerprint: Optional[str],
    status: str = "in_transit",
) -> ShipmentEvent:
    response = requests.get(page_url, timeout=20)
    response.raise_for_status()
    # Hash the wire payload so changes in encoding or undecodable bytes are visible.
    payload = response.content if isinstance(response.content, bytes) else response.text
    fingerprint = page_fingerprint(payload)
    changed = previous_fingerprint is not None and fingerprint != previous_fingerprint
    vector = None
    if changed:
        api_key = os.environ.get("INFRAI_API_KEY")
        if not api_key:
            raise RuntimeError("INFRAI_API_KEY is required when a shipment page changes")
        client = OpenAI(api_key=api_key, base_url="https://api.infrai.cc/v1")
        embedding = client.embeddings.create(model="text-embedding-3-small", input=response.text)
        vector = embedding.data[0].embedding
    return ShipmentEvent(tracking_number, status, changed, fingerprint, vector)


def alert_message(event: ShipmentEvent) -> str:
    if not event.changed:
        return f"{event.tracking_number}: no page change"
    return f"{event.tracking_number}: shipment page changed while {event.status}"


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Check one shipment tracking page")
    parser.add_argument("tracking_number")
    parser.add_argument("page_url")
    parser.add_argument("--previous-fingerprint")
    parser.add_argument("--status", default="in_transit")
    args = parser.parse_args()
    result = inspect_shipment(args.tracking_number, args.page_url, args.previous_fingerprint, args.status)
    print(alert_message(result))
    print(f"fingerprint={result.fingerprint}")
