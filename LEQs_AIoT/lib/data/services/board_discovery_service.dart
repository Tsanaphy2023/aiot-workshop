import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;
import '../models/board_discovery_model.dart';
import 'udp_scanner.dart';

/// Auto-discovery service to locate GoGo-IoT / LEQs IoT hardware boards on Wi-Fi
class BoardDiscoveryService {
  static const int udpPort = 8266;

  /// Perform a full scan using UDP Broadcast and Subnet sweep
  Future<List<DiscoveredBoard>> scanForBoards({
    Duration scanDuration = const Duration(seconds: 3),
  }) async {
    final Map<String, DiscoveredBoard> results = {};

    // 1. Try UDP Broadcast (Delegated to native platform implementation, bypassed on web)
    try {
      await scanViaUdpPlatform(results, scanDuration, udpPort);
    } catch (e) {
      debugPrint('[Discovery] UDP scan error: $e');
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
