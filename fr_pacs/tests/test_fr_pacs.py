from fr_pacs.client import FrPACSBrainScanClient


def test_fr_pacs_client_initialization():
    client = FrPACSBrainScanClient(host="127.0.0.1", port=12346)
    assert client.host == "127.0.0.1"
    assert client.port == 12346
