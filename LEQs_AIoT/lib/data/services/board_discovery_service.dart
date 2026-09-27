import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/board_discovery_model.dart';

// Conditionally import dart:io for native platforms
import 'dart:io' if (dart.library.html) 'dart:html' as platform;

/// Auto-discovery service to locate GoGo-IoT / LEQs IoT hardware boards on Wi-Fi
class BoardDiscoveryService {
  static const int udpPort = 8266;

  /// Perform a full scan using UDP Broadcast and Subnet sweep
  Future<List<DiscoveredBoard>> scanForBoards({
    Duration scanDuration = const Duration(seconds: 3),
  }) async {
    final Map<String, DiscoveredBoard> results = {};

    // 1. Try UDP Broadcast on native platforms (Android, iOS, Desktop)
    if (!kIsWeb) {
      try {
        await _scanViaUdp(results, scanDuration);
      } catch (e) {
        debugPrint('[Discovery] UDP scan error: $e');
      }
    }

    // 2. Common fallback IPs (Hotspot / Default Subnet / XAMPP bridge)
    final fallbackIps = [
      '192.168.1.105',
      '192.168.1.108',
      '192.168.4.1',   // ESP32 Default SoftAP IP
      '10.0.0.41',     // XAMPP Workshop Bridge IP
    ];

    await Future.wait(fallbackIps.map((ip) async {
      if (!results.containsKey(ip)) {
        final board = await _probeHttp(ip);
        if (board != null) {
          results[board.ip] = board;
        }
      }
    }));

    return results.values.toList()
      ..sort((a, b) => b.rssi.compareTo(a.rssi));
  }

  /// UDP Broadcast Probe
  Future<void> _scanViaUdp(
    Map<String, DiscoveredBoard> results,
    Duration duration,
  ) async {
    // ignore: undefined_prefixed_name
    dynamic socket = await platform.RawDatagramSocket.bind(
      // ignore: undefined_prefixed_name
      platform.InternetAddress.anyIPv4,
      0,
    );

    try {
      socket.broadcastEnabled = true;

      // Broadcast discover packet
      final data = utf8.encode('DISCOVER_LEQS_DEVICE');
      // ignore: undefined_prefixed_name
      final broadcastAddr = platform.InternetAddress('255.255.255.255');
      socket.send(data, broadcastAddr, udpPort);

      final completer = Completer<void>();
      Timer(duration, () {
        if (!completer.isCompleted) completer.complete();
      });

      socket.listen((event) {
        // ignore: undefined_prefixed_name
        if (event == platform.RawSocketEvent.read) {
          final datagram = socket.receive();
          if (datagram != null) {
            try {
              final text = utf8.decode(datagram.data);
              final json = jsonDecode(text) as Map<String, dynamic>;
              final ip = datagram.address.address;
              final board = DiscoveredBoard.fromJson(json, ip);
              results[board.ip] = board;
              debugPrint('[Discovery] Found board via UDP: ${board.deviceName} @ $ip');
            } catch (_) {}
          }
        }
      });

      await completer.future;
    } finally {
      socket.close();
    }
  }

  /// Probe a single IP via HTTP /api/info
  Future<DiscoveredBoard?> _probeHttp(String ip) async {
    try {
      final client = http.Client();
      final res = await client
          .get(Uri.parse('http://$ip/api/info'))
          .timeout(const Duration(milliseconds: 600));
      client.close();
      if (res.statusCode == 200) {
        final json = jsonDecode(res.body) as Map<String, dynamic>;
        return DiscoveredBoard.fromJson(json, ip);
      }
    } catch (_) {}
    return null;
  }
}
