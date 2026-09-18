from unittest.mock import Mock, patch

from shipment_monitor import alert_message, inspect_shipment, page_fingerprint


def test_changed_page_creates_alert_and_embedding():
    response = Mock(text="delivered at dock 4")
    response.raise_for_status.return_value = None
    fake_embedding = Mock(data=[Mock(embedding=[0.1, 0.2])])
    with patch("shipment_monitor.requests.get", return_value=response), patch(
        "shipment_monitor.OpenAI"
    ) as openai:
        openai.return_value.embeddings.create.return_value = fake_embedding
        event = inspect_shipment("PKG-42", "https://carrier.example/PKG-42", "old")
    assert event.changed is True
    assert event.semantic_vector == [0.1, 0.2]
    assert alert_message(event) == "PKG-42: shipment page changed while in_transit"


def test_first_observation_is_baseline():
    response = Mock(text="label created")
    response.raise_for_status.return_value = None
    with patch("shipment_monitor.requests.get", return_value=response):
        event = inspect_shipment("PKG-7", "https://carrier.example/PKG-7", None)
    assert event.changed is False
    assert alert_message(event) == "PKG-7: no page change"


def test_fingerprint_is_deterministic():
    assert page_fingerprint("same") == page_fingerprint("same")
