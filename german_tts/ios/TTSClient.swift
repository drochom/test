import Foundation
import GRPC
import NIO
import NIOHPACK

/// Calls the German TTS gRPC server running on your Mac.
/// The server plays audio on its own speaker — no audio data is returned.
final class TTSClient {

    private let channel: GRPCChannel
    private let stub: Tts_TTSServiceAsyncClient

    /// - Parameters:
    ///   - host: IP or hostname of your Mac (e.g. "192.168.1.42" or "localhost" in the simulator).
    ///   - port: Port the server is listening on (default 50051).
    init(host: String, port: Int = 50051) {
        let group = PlatformSupport.makeEventLoopGroup(loopCount: 1)
        channel = try! GRPCChannelPool.with(
            target: .host(host, port: port),
            transportSecurity: .plaintext,
            eventLoopGroup: group
        )
        stub = Tts_TTSServiceAsyncClient(channel: channel)
    }

    /// Sends German text to the server and asks it to speak.
    /// - Parameters:
    ///   - text:  German text to synthesize.
    ///   - rate:  Words per minute (0 = server default ~200 wpm).
    @discardableResult
    func speak(_ text: String, rate: Int32 = 0) async throws -> Bool {
        var request = Tts_SpeakRequest()
        request.text = text
        request.rate = rate

        let response = try await stub.speak(request)
        return response.success
    }

    deinit {
        try? channel.close().wait()
    }
}

// MARK: - Usage example

// let tts = TTSClient(host: "192.168.1.42")  // your Mac's local IP
// try await tts.speak("Guten Morgen! Wie geht es dir heute?")
// try await tts.speak("Das Wetter ist heute sehr schön.", rate: 160)
