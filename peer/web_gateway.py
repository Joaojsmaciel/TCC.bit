#!/usr/bin/env python3
"""
Gateway HTTP para integrar o hotsite ao backend P2P real.

O navegador nao consegue abrir sockets TCP puros para o Tracker/Peers. Este
processo atua como um Peer real da rede e expoe uma API HTTP pequena que chama
as mesmas operacoes da CLI: publicar, buscar, baixar, listar locais, listar rede,
listar peers e status.
"""

import cgi
import json
import os
import tempfile
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from peer import Peer


TRACKER_HOST = os.environ.get("TRACKER_HOST", "tracker")
TRACKER_PORT = int(os.environ.get("TRACKER_PORT", "5000"))
PEER_ID = os.environ.get("PEER_ID", "web-ui")
PEER_PORT = int(os.environ.get("PEER_PORT", "6200"))
API_HOST = os.environ.get("API_HOST", "0.0.0.0")
API_PORT = int(os.environ.get("API_PORT", "8080"))

peer = Peer(TRACKER_HOST, TRACKER_PORT, PEER_PORT, PEER_ID)
operation_lock = threading.Lock()


def response_payload(status, **kwargs):
    payload = {"status": status}
    payload.update(kwargs)
    return payload


class GatewayHandler(BaseHTTPRequestHandler):
    server_version = "P2PWebGateway/1.0"

    def log_message(self, fmt, *args):
        print("[WEB_GATEWAY]", fmt % args)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        if length <= 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        query = parse_qs(parsed.query)

        try:
            if parsed.path == "/api/status":
                self.send_json(200, response_payload(
                    "success",
                    peer_id=peer.peer_id,
                    ip=peer.peer_ip,
                    port=peer.peer_port,
                    local_files=len(peer.file_manager.list_files()),
                    heartbeat=peer.heartbeat.running,
                    storage_dir=peer.file_manager.storage_dir,
                ))
                return

            if parsed.path == "/api/files/local":
                self.send_json(200, response_payload("success", files=peer.file_manager.list_files()))
                return

            if parsed.path == "/api/files/network":
                self.send_json(200, peer.network.list_files())
                return

            if parsed.path == "/api/peers":
                self.send_json(200, peer.network.list_peers())
                return

            if parsed.path == "/api/search":
                term = query.get("term", [""])[0]
                self.send_json(200, response_payload("success", results=peer.search_files(term)))
                return

            if parsed.path == "/api/file":
                filename = os.path.basename(query.get("filename", [""])[0])
                file_path = peer.file_manager.get_file_path(filename)
                if not filename or not file_path:
                    self.send_json(404, response_payload("error", message="Arquivo local nao encontrado"))
                    return

                path = Path(file_path)
                data = path.read_bytes()
                self.send_response(200)
                self.send_header("Content-Type", "application/zip")
                self.send_header("Content-Disposition", f'attachment; filename="{filename}"')
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)
                return

            self.send_json(404, response_payload("error", message="Endpoint nao encontrado"))

        except Exception as exc:
            self.send_json(500, response_payload("error", message=str(exc)))

    def do_POST(self):
        parsed = urlparse(self.path)

        try:
            if parsed.path == "/api/upload":
                self.handle_upload()
                return

            if parsed.path == "/api/download":
                payload = self.read_json()
                filename = os.path.basename(payload.get("filename", ""))
                if not filename:
                    self.send_json(400, response_payload("error", message="filename obrigatorio"))
                    return

                with operation_lock:
                    success = peer.download_file(filename)

                if success:
                    self.send_json(200, response_payload(
                        "success",
                        message="Download concluido",
                        file=peer.file_manager.get_file_info(filename),
                    ))
                else:
                    self.send_json(502, response_payload("error", message="Falha ao baixar arquivo"))
                return

            if parsed.path == "/api/heartbeat":
                self.send_json(200, peer.network.send_heartbeat(peer.peer_id))
                return

            if parsed.path == "/api/unregister":
                self.send_json(200, peer.network.unregister_peer(peer.peer_id))
                return

            self.send_json(404, response_payload("error", message="Endpoint nao encontrado"))

        except Exception as exc:
            self.send_json(500, response_payload("error", message=str(exc)))

    def handle_upload(self):
        content_type = self.headers.get("Content-Type", "")
        if not content_type.startswith("multipart/form-data"):
            self.send_json(400, response_payload("error", message="Use multipart/form-data com campo file"))
            return

        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={
                "REQUEST_METHOD": "POST",
                "CONTENT_TYPE": content_type,
                "CONTENT_LENGTH": self.headers.get("Content-Length", "0"),
            },
        )

        if "file" not in form:
            self.send_json(400, response_payload("error", message="Campo file obrigatorio"))
            return

        field = form["file"]
        filename = os.path.basename(field.filename or "")
        if not filename:
            self.send_json(400, response_payload("error", message="Nome do arquivo invalido"))
            return

        if not filename.lower().endswith(".zip"):
            self.send_json(400, response_payload("error", message="A tematica exige arquivos .zip"))
            return

        with tempfile.NamedTemporaryFile(delete=False, suffix=".zip") as temp_file:
            temp_path = temp_file.name
            while True:
                chunk = field.file.read(1024 * 1024)
                if not chunk:
                    break
                temp_file.write(chunk)

        try:
            final_temp_path = str(Path(temp_path).with_name(filename))
            os.replace(temp_path, final_temp_path)

            with operation_lock:
                success = peer.publish_file(final_temp_path)

            file_info = peer.file_manager.get_file_info(filename)
            if success and file_info:
                self.send_json(200, response_payload(
                    "success",
                    message="Arquivo publicado e replicacao iniciada",
                    filename=filename,
                    hash=file_info.get("hash"),
                    size=file_info.get("size"),
                ))
            else:
                self.send_json(502, response_payload("error", message="Falha ao publicar arquivo"))
        finally:
            for candidate in (temp_path, str(Path(temp_path).with_name(filename))):
                try:
                    if os.path.exists(candidate):
                        os.remove(candidate)
                except OSError:
                    pass


def main():
    if not peer.start():
        raise SystemExit("Nao foi possivel iniciar o peer do gateway web")

    server = ThreadingHTTPServer((API_HOST, API_PORT), GatewayHandler)
    print(f"[WEB_GATEWAY] API HTTP em {API_HOST}:{API_PORT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.shutdown()
        peer.stop()


if __name__ == "__main__":
    main()
