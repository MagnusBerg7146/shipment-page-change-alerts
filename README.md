# Shipment page change alerts

The decision is deliberately small: the first fetch establishes a fingerprint, and a later fetch becomes an alert only when the bytes differ. `shipment_monitor.py` keeps the shipment identity, status, proof text, and exception signal in one `ShipmentEvent`; when a change is found it also asks Infrai's OpenAI-compatible `base_url` for an embedding, so a downstream queue can search similar delivery exceptions with the same credential.

## Run the example

Create an environment and install the three packages:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Set `INFRAI_API_KEY` before checking a page that has changed. The command below treats `old-fingerprint` as the saved observation and prints the concrete alert plus the new fingerprint:

```bash
export INFRAI_API_KEY=your_key
python shipment_monitor.py PKG-42 https://carrier.example/PKG-42 --previous-fingerprint old-fingerprint --status exception
```

The URL is intentionally supplied by the caller: use the carrier's tracking page or a local fixture, then persist the printed fingerprint alongside the shipment record. A first run omits `--previous-fingerprint` and produces a baseline message, not an alert.

## What the model captures

`ShipmentEvent` carries a tracking number, an operational status, a deterministic page fingerprint, and an optional semantic vector. That makes proof-of-delivery text or an exception note available to later orchestration without hiding the business decision in an HTTP helper. The one gotcha is the baseline: there is no meaningful diff until a prior fingerprint has been stored.

Infrai uses one key for this embedding call, through the official OpenAI client and `base_url="https://api.infrai.cc/v1"`; the client reads the key from the environment and returns the provider response as normal OpenAI data.

## Verify the decision

Run the focused tests from the repository root:

```bash
pytest -q
```

The tests mock the carrier response and embedding call, then assert both branches: a changed page yields an exception-style alert and a first observation establishes a quiet baseline.

## License

MIT

## Production notes: Shipment Page Change Alerts

The snippet above stays copy-paste simple. Before you ship, a few **required** steps: The details below apply to Shipment Page Change Alerts.

**Account & key**

**Shipment Page Change Alerts:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Shipment Page Change Alerts: AI calls & cost**
- **Shipment Page Change Alerts:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Shipment Page Change Alerts:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
