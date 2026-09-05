"""
Provider verification: replay the generated Pact file against a stub
server that mimics what we expect Open-Meteo to return, proving our
consumer's expectations are satisfiable.
"""
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs

import pytest

PACT_FILE = os.path.join(os.path.dirname(__file__), "pacts", "weatheraggregatorservice-openmeteoapi.json")


class StubOpenMeteoHandler(BaseHTTPRequestHandler):
    """Minimal stub that replays canned responses matching our Pact interactions."""

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        if parsed.path == "/v1/search" and query.get("name") == ["Timisoara"]:
            body = {
                "results": [
                    {"latitude": 45.75, "longitude": 21.23, "name": "Timisoara", "country": "Romania"}
                ]
            }
        elif parsed.path == "/v1/forecast" and query.get("latitude") == ["45.75"]:
            body = {
                "current_weather": {
                    "temperature": 22.4,
                    "windspeed": 14.2,
                    "weathercode": 3,
                    "time": "2024-06-01T14:00",
                }
            }
        else:
            self.send_response(404)
            self.end_headers()
            return

        payload = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, format, *args):
        pass  # silence default request logging


@pytest.fixture
def stub_server():
    server = HTTPServer(("localhost", 0), StubOpenMeteoHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield server
    server.shutdown()


def test_stub_satisfies_every_interaction_in_the_pact(stub_server):
    with open(PACT_FILE) as f:
        pact_data = json.load(f)

    port = stub_server.server_address[1]
    base_url = f"http://localhost:{port}"

    import requests

    for interaction in pact_data["interactions"]:
        request_spec = interaction["request"]
        response_spec = interaction["response"]

        response = requests.get(f"{base_url}{request_spec['path']}?{request_spec['query']}")

        assert response.status_code == response_spec["status"], interaction["description"]
        assert response.json() == response_spec["body"], interaction["description"]