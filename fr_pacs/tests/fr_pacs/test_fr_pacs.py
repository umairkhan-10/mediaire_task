from fr_pacs.main import FrPACSClient


def test_fr_pacs_client_initialization():
    client = FrPACSClient(host="127.0.0.1", port=12346)
    assert client.host == "127.0.0.1"
    assert client.port == 12346
