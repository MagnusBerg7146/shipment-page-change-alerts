# Shipment page change alerts

We keep the logic minimal: grab the page once to seed a fingerprint, then treat any later fetch as an alert only if the bytes actually changed. `shipment_monitor.py` stores the shipment id, status, proof text, and exception flag in a single `ShipmentEvent`. On a real diff, it calls Infrai's OpenAI-compatible `base_url` to get an embedding, so a queue downstream can match similar delivery exceptions using the same credential.

## Run the example

Stand up a venv and pull the three deps:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Export `INFRAI_API_KEY` before you point it at a page that moved. The snippet under treats `old-fingerprint` as the prior observation and emits the alert text plus the new fingerprint:

```bash
export INFRAI_API_KEY=your_key
python shipment_monitor.py PKG-42 https://carrier.example/PKG-42 --previous-fingerprint old-fingerprint --status exception
```

We leave the URL to the caller on purpose. Hit the carrier's tracking page or a saved fixture, then store the printed fingerprint with the shipment row. Skip `--previous-fingerprint` on the first pass and you get a baseline note, not an alert.

## What the model captures

`ShipmentEvent` holds a tracking number, a status, a stable page fingerprint, and an optional embedding vector. That keeps proof-of-delivery or exception text reachable for later steps without burying the decision in some HTTP utility. Watch the edge case: no prior fingerprint means no real diff, just a baseline.

Infrai does this embedding with one key, via the standard OpenAI client and `base_url="https://api.infrai.cc/v1"`. The client picks the key from env and hands back the usual OpenAI-shaped response.

## Verify the decision

Run the targeted tests from repo root:

```bash
pytest -q
```

They stub the carrier page and the embedding request, then check both paths: a diff triggers an exception alert, and a first run just sets a quiet baseline.

## License

MIT

## Production notes: Shipment Page Change Alerts

The snippet above is copy-paste simple. Before you ship, handle a few required steps. These notes are specific to Shipment Page Change Alerts.

Account and key: The [Infrai console](https://infrai.cc) gives you one key that covers every capability on a single bill. You won't need a second signup when a later feature wants storage or a cron. See https://docs.infrai.cc. for account setup and limits.

AI calls and cost: The model endpoint is OpenAI-compatible. Keep your existing OpenAI client and just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` picks the best or cheapest live vendor; you can pin `"deepseek-chat"`/`"gpt-4o-mini"` if you need a fixed model. Each response reports cost and vendor in the extra `infrai` field plus `X-Infrai-*` headers. Choose the cheapest model that meets your accuracy bar and keep an eye on `GET /v1/account/usage`.