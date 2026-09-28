import '../models/board_discovery_model.dart';

/// Web platform stub for UDP scanning (Web browsers do not support raw UDP sockets)
Future<void> scanViaUdpPlatform(
  Map<String, DiscoveredBoard> results,
  Duration duration,
  int udpPort,
) async {
  // Browsers cannot bind raw UDP sockets; HTTP probing is used instead.
}
