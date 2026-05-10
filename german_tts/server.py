#!/usr/bin/env python3
"""
German TTS gRPC server — plays audio via macOS `say -v Anna`.
Run: python server.py [--port 50051]
"""

import argparse
import subprocess
import threading
import logging
import grpc
from concurrent import futures

import tts_pb2
import tts_pb2_grpc

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# Only one `say` process at a time; new requests cancel the current one.
_say_lock = threading.Lock()
_current_proc: subprocess.Popen | None = None


def _speak(text: str, rate: int) -> None:
    global _current_proc

    cmd = ["say", "-v", "Anna"]
    if rate > 0:
        cmd += ["-r", str(rate)]
    cmd.append(text)

    with _say_lock:
        if _current_proc and _current_proc.poll() is None:
            _current_proc.terminate()
            _current_proc.wait()
        _current_proc = subprocess.Popen(cmd)

    _current_proc.wait()


class TTSServicer(tts_pb2_grpc.TTSServiceServicer):
    def Speak(self, request, context):
        text = request.text.strip()
        if not text:
            return tts_pb2.SpeakResponse(success=False, message="Empty text")

        log.info("Speaking: %r (rate=%d)", text, request.rate)
        try:
            _speak(text, request.rate)
            return tts_pb2.SpeakResponse(success=True, message="OK")
        except Exception as exc:
            log.error("say failed: %s", exc)
            return tts_pb2.SpeakResponse(success=False, message=str(exc))


def serve(port: int) -> None:
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    tts_pb2_grpc.add_TTSServiceServicer_to_server(TTSServicer(), server)
    address = f"0.0.0.0:{port}"
    server.add_insecure_port(address)
    server.start()
    log.info("TTS server listening on %s", address)
    server.wait_for_termination()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=50051)
    args = parser.parse_args()
    serve(args.port)
