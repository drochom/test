# German TTS gRPC Server (macOS · Anna voice)

Receives German text from an iOS app via gRPC and speaks it through the Mac's speaker using the built-in `say -v Anna` command.

## Mac setup

```bash
cd german_tts

# 1. Install Python deps
pip install -r requirements.txt

# 2. Generate gRPC Python bindings (once)
chmod +x generate_proto.sh && ./generate_proto.sh

# 3. Start the server
python server.py              # listens on 0.0.0.0:50051
python server.py --port 9000  # custom port
```

**Download Anna (Premium) voice** for best quality:  
*System Settings → Accessibility → Spoken Content → System Voice → Manage Voices → German → Anna (Premium)*

## iOS setup

1. Add the Swift gRPC package to your Xcode project:  
   `https://github.com/grpc/grpc-swift` (SwiftPM)

2. Add `tts.proto` to your proto generation step (e.g. via `protoc` + `grpc-swift` plugin).

3. Copy `ios/TTSClient.swift` into your app and call:

```swift
let tts = TTSClient(host: "192.168.1.42")  // your Mac's LAN IP
try await tts.speak("Guten Morgen!")
```

> In the iOS Simulator, use `host: "localhost"` (loopback reaches the Mac).

## Behaviour

- Requests are serialised — a new `Speak` call cancels any speech currently in progress.
- The server returns immediately after the `say` process finishes.
- `rate` is words-per-minute; omit or pass `0` for the system default (~200 wpm).
