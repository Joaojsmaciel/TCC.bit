#!/usr/bin/env python3
"""
Teste E2E do TP2 - Sistema P2P Hibrido / Tematica 5.

Orquestra Tracker + Peers reais via subprocess, envia comandos pela CLI dos
peers e valida replicacao, download, hash e re-replicacao no nivel do SO.
"""

import hashlib
import json
import os
import random
import shutil
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parent
TRACKER_HOST = "127.0.0.1"
TRACKER_PORT = 5000
FILENAME = "teste_tcc.zip"
HEARTBEAT_TIMEOUT_SECONDS = 60
TRACKER_SCAN_INTERVAL_SECONDS = 10

PEERS = {
    "peerA": 6101,
    "peerB": 6102,
    "peerC": 6103,
    "peerD": 6104,
}

GREEN = "\033[92m"
YELLOW = "\033[93m"
RED = "\033[91m"
RESET = "\033[0m"


class ProcessHandle:
    def __init__(self, name, process, log_path, log_file):
        self.name = name
        self.process = process
        self.log_path = log_path
        self.log_file = log_file


def sha256_file(path):
    digest = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def storage_dir(peer_id):
    return ROOT / f"files_{peer_id}"


def file_in_peer(peer_id, filename=FILENAME):
    return storage_dir(peer_id) / filename


def read_process_log(handle):
    try:
        handle.log_file.flush()
    except Exception:
        pass
    try:
        return Path(handle.log_path).read_text(encoding="utf-8", errors="replace")
    except Exception as exc:
        return f"<erro ao ler log {handle.name}: {exc}>"


def fail(message, handles=None):
    print(f"{RED}ERRO: {message}{RESET}", file=sys.stderr)
    if handles:
        print("\n===== LOGS DE DEBUG =====", file=sys.stderr)
        for handle in handles:
            print(f"\n----- {handle.name}: {handle.log_path} -----", file=sys.stderr)
            print(read_process_log(handle)[-6000:], file=sys.stderr)
    raise AssertionError(message)


def cleanup_files(dummy_path=None):
    for peer_id in PEERS:
        shutil.rmtree(storage_dir(peer_id), ignore_errors=True)
    if dummy_path and Path(dummy_path).exists():
        Path(dummy_path).unlink()


def stop_process(handle, kill=False):
    process = handle.process
    if process.poll() is None:
        try:
            if kill:
                process.kill()
            else:
                process.terminate()
            process.wait(timeout=8)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)
    try:
        handle.log_file.close()
    except Exception:
        pass


def stop_all(handles):
    for handle in reversed(handles):
        stop_process(handle)


def start_process(name, command, log_dir, env=None, stdin_pipe=False):
    log_path = Path(log_dir) / f"{name}.log"
    log_file = open(log_path, "w", encoding="utf-8", buffering=1)
    process_env = os.environ.copy()
    process_env["PYTHONUNBUFFERED"] = "1"
    process_env["TERM"] = "dumb"
    if env:
        process_env.update(env)

    process = subprocess.Popen(
        command,
        cwd=ROOT,
        env=process_env,
        stdin=subprocess.PIPE if stdin_pipe else subprocess.DEVNULL,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        start_new_session=True,
    )
    return ProcessHandle(name, process, log_path, log_file)


def assert_process_alive(handle, handles):
    if handle.process.poll() is not None:
        fail(f"Processo {handle.name} morreu com exit code {handle.process.returncode}", handles)


def wait_for_port(host, port, timeout=15):
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with socket.create_connection((host, port), timeout=1):
                return True
        except OSError:
            time.sleep(0.2)
    return False


def send_json_tcp(host, port, payload, timeout=5):
    with socket.create_connection((host, port), timeout=timeout) as sock:
        sock.settimeout(timeout)
        sock.sendall(json.dumps(payload).encode("utf-8") + b"\n")
        data = bytearray()
        while True:
            chunk = sock.recv(1)
            if not chunk:
                break
            if chunk == b"\n":
                break
            data.extend(chunk)
        if not data:
            raise RuntimeError("Resposta JSON vazia")
        return json.loads(data.decode("utf-8"))


def tracker_request(payload):
    return send_json_tcp(TRACKER_HOST, TRACKER_PORT, payload)


def wait_until(predicate, timeout, description, interval=0.5, handles=None):
    deadline = time.time() + timeout
    last_error = None
    while time.time() < deadline:
        try:
            if predicate():
                return True
        except Exception as exc:
            last_error = exc
        time.sleep(interval)

    suffix = f" Ultimo erro: {last_error}" if last_error else ""
    fail(f"Timeout aguardando: {description}.{suffix}", handles)


def send_cli(peer_handle, lines):
    if peer_handle.process.poll() is not None:
        raise RuntimeError(f"{peer_handle.name} nao esta rodando")
    assert peer_handle.process.stdin is not None
    peer_handle.process.stdin.write("\n".join(lines) + "\n")
    peer_handle.process.stdin.flush()


def start_tracker(handles, log_dir):
    handle = start_process(
        "tracker",
        [sys.executable, "-u", "tracker/tracker.py"],
        log_dir,
    )
    handles.append(handle)
    if not wait_for_port(TRACKER_HOST, TRACKER_PORT, timeout=15):
        fail("Tracker nao abriu a porta 5000", handles)
    assert_process_alive(handle, handles)
    return handle


def start_peer(peer_id, port, handles, log_dir):
    handle = start_process(
        peer_id,
        [sys.executable, "-u", "peer/peer.py"],
        log_dir,
        env={
            "TRACKER_HOST": TRACKER_HOST,
            "TRACKER_PORT": str(TRACKER_PORT),
            "PEER_ID": peer_id,
            "PEER_PORT": str(port),
        },
        stdin_pipe=True,
    )
    handles.append(handle)
    if not wait_for_port(TRACKER_HOST, port, timeout=20):
        fail(f"{peer_id} nao abriu a porta {port}", handles)
    assert_process_alive(handle, handles)
    return handle


def wait_for_registered_peers(expected_ids, handles):
    expected = set(expected_ids)

    def has_peers():
        response = tracker_request({"command": "LIST", "target": "peers"})
        peers = {peer["peer_id"] for peer in response.get("peers", [])}
        return expected.issubset(peers)

    wait_until(has_peers, 15, f"peers registrados {sorted(expected)}", handles=handles)


def wait_for_file_holders(file_hash, expected_holders, handles, timeout=20):
    expected = set(expected_holders)

    def has_holders():
        response = tracker_request({"command": "WHEREIS", "hash": file_hash})
        holders = {peer["peer_id"] for peer in response.get("peers", [])}
        return expected.issubset(holders)

    wait_until(has_holders, timeout, f"holders {sorted(expected)} para hash {file_hash[:12]}", handles=handles)


def get_active_holders(file_hash):
    response = tracker_request({"command": "WHEREIS", "hash": file_hash})
    assert response.get("status") == "success", response
    return {peer["peer_id"] for peer in response.get("peers", [])}


def download_from_peer(peer_info, file_hash, save_path, filename=FILENAME):
    with socket.create_connection((peer_info["ip"], int(peer_info["port"])), timeout=10) as sock:
        sock.settimeout(20)
        request = {
            "command": "DOWNLOAD",
            "hash": file_hash,
            "filename": filename,
        }
        sock.sendall(json.dumps(request).encode("utf-8") + b"\n")

        response_data = bytearray()
        while True:
            chunk = sock.recv(1)
            if not chunk:
                break
            if chunk == b"\n":
                break
            response_data.extend(chunk)

        response = json.loads(response_data.decode("utf-8"))
        assert response.get("status") == "success", response

        file_size = int(response["file_size"])
        sock.sendall(json.dumps({"status": "ack"}).encode("utf-8") + b"\n")

        save_path.parent.mkdir(parents=True, exist_ok=True)
        received = 0
        with open(save_path, "wb") as output:
            while received < file_size:
                data = sock.recv(min(4096, file_size - received))
                if not data:
                    break
                output.write(data)
                received += len(data)

        assert received == file_size, f"Download incompleto: {received}/{file_size}"


def create_dummy_zip(path):
    random_bytes = os.urandom(4096)
    payload = b"PK\x03\x04TP2-Redes-P2P-Backup-Academico\n" + random_bytes
    Path(path).write_bytes(payload)


def main():
    handles = []
    log_dir = tempfile.mkdtemp(prefix="tp2_e2e_logs_")
    dummy_path = ROOT / FILENAME

    print(f"{YELLOW}[E2E] Logs dos processos: {log_dir}{RESET}")

    try:
        cleanup_files(dummy_path)

        print("[E2E] 1/5 Bootstrapping: iniciando Tracker e Peers A, B, C...")
        start_tracker(handles, log_dir)
        peer_a = start_peer("peerA", PEERS["peerA"], handles, log_dir)
        peer_b = start_peer("peerB", PEERS["peerB"], handles, log_dir)
        peer_c = start_peer("peerC", PEERS["peerC"], handles, log_dir)
        time.sleep(2)
        wait_for_registered_peers(["peerA", "peerB", "peerC"], handles)

        print("[E2E] 2/5 Upload: criando teste_tcc.zip e publicando no Peer A...")
        create_dummy_zip(dummy_path)
        original_hash = sha256_file(dummy_path)
        send_cli(peer_a, ["1", str(dummy_path), ""])

        wait_until(
            lambda: file_in_peer("peerB").exists() and file_in_peer("peerC").exists(),
            25,
            "replicas fisicas em peerB e peerC",
            handles=handles,
        )
        assert sha256_file(file_in_peer("peerB")) == original_hash, "Hash da replica em peerB diverge"
        assert sha256_file(file_in_peer("peerC")) == original_hash, "Hash da replica em peerC diverge"
        wait_for_file_holders(original_hash, ["peerA", "peerB", "peerC"], handles)

        # Para exercitar a tolerancia sobre as replicas voluntarias, o origin
        # sai do indice do Tracker. Assim, B e C sao as duas replicas ativas.
        unregister_origin = tracker_request({"command": "UNREGISTER", "peer_id": "peerA"})
        assert unregister_origin.get("status") == "success", unregister_origin
        wait_until(
            lambda: get_active_holders(original_hash) == {"peerB", "peerC"},
            10,
            "peerA removido do indice para testar replicas voluntarias B/C",
            handles=handles,
        )

        print("[E2E] 3/5 Lookup/Download: iniciando Peer D e baixando arquivo...")
        peer_d = start_peer("peerD", PEERS["peerD"], handles, log_dir)
        time.sleep(2)
        wait_for_registered_peers(["peerB", "peerC", "peerD"], handles)

        lookup = tracker_request({"command": "LOOKUP", "term": FILENAME})
        assert lookup.get("status") == "success", lookup
        assert any(item.get("hash") == original_hash for item in lookup.get("results", [])), lookup

        # LOOKUP pela CLI do Peer D para exercitar o cliente; o download binario
        # abaixo e feito via socket direto e salvo no storage do Peer D sem
        # publicar no Tracker, para que D continue sendo candidato de
        # re-replicacao no cenario de falha.
        send_cli(peer_d, ["2", FILENAME, ""])
        whereis = tracker_request({"command": "WHEREIS", "hash": original_hash})
        assert whereis.get("status") == "success", whereis
        source_peer = next(peer for peer in whereis["peers"] if peer["peer_id"] in {"peerB", "peerC"})
        download_from_peer(source_peer, original_hash, file_in_peer("peerD"))
        wait_until(
            lambda: file_in_peer("peerD").exists(),
            25,
            "download do arquivo no peerD",
            handles=handles,
        )
        assert sha256_file(file_in_peer("peerD")) == original_hash, "Hash do download no Peer D diverge do original"
        assert "peerD" not in get_active_holders(original_hash), "Peer D ainda nao deve estar publicado antes da re-replicacao"

        print("[E2E] 4/5 Falha: derrubando Peer B com kill -9 e aguardando re-replicacao...")
        os.killpg(os.getpgid(peer_b.process.pid), signal.SIGKILL)
        peer_b.process.wait(timeout=5)
        peer_b.log_file.close()

        wait_until(
            lambda: "peerB" not in get_active_holders(original_hash),
            HEARTBEAT_TIMEOUT_SECONDS + TRACKER_SCAN_INTERVAL_SECONDS + 20,
            "Tracker remover peerB inativo apos heartbeat timeout",
            interval=2,
            handles=handles,
        )

        def restored_two_replicas():
            holders = get_active_holders(original_hash)
            return "peerB" not in holders and len(holders) >= 2

        wait_until(
            restored_two_replicas,
            35,
            "re-replicacao restaurar pelo menos 2 replicas ativas",
            interval=1,
            handles=handles,
        )

        holders = get_active_holders(original_hash)
        assert len(holders) >= 2, f"Esperado >=2 replicas ativas, obtido {holders}"
        assert "peerB" not in holders, f"peerB morto ainda aparece como ativo: {holders}"
        assert "peerD" in holders, f"Peer D deveria entrar no indice apos FORCE_REPLICATE, holders={holders}"
        assert file_in_peer("peerD").exists(), "Peer D deve manter ou receber copia valida apos re-replicacao"
        assert sha256_file(file_in_peer("peerD")) == original_hash, "Hash no Peer D diverge apos re-replicacao"

        print(f"{GREEN}✅ SUCESSO: Fluxo Completo do TP2 Validado com Sucesso!{RESET}")

    except Exception:
        fail("Teste E2E falhou", handles)
    finally:
        stop_all(handles)
        cleanup_files(dummy_path)


if __name__ == "__main__":
    main()
