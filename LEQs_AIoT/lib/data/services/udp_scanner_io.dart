import 'dart:async';
import 'dart:convert';
import 'dart:io';
import 'package:flutter/foundation.dart';
import '../models/board_discovery_model.dart';

/// Native (Android, iOS, Desktop) implementation of UDP Broadcast scanning
Future<void> scanViaUdpPlatform(
  Map<String, DiscoveredBoard> results,
  Duration duration,
  int udpPort,
) async {
  RawDatagramSocket? socket;
  try {
    socket = await RawDatagramSocket.bind(InternetAddress.anyIPv4, 0);
    socket.broadcastEnabled = true;

    final data = utf8.encode('DISCOVER_LEQS_DEVICE');
    final broadcastAddr = InternetAddress('255.255.255.255');
    socket.send(data, broadcastAddr, udpPort);

    final completer = Completer<void>();
    Timer(duration, () {
      if (!completer.isCompleted) completer.complete();
    });

    socket.listen((event) {
      if (event == RawSocketEvent.read) {
        final datagram = socket?.receive();
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
  } catch (e) {
    debugPrint('[Discovery] UDP scan error: $e');
  } finally {
    socket?.close();
  }
}
