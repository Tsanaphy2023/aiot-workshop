class DiscoveredBoard {
  final String ip;
  final String deviceName;
  final int teamNumber;
  final int rssi;
  final String mac;
  final String firmware;
  final DateTime discoveredAt;

  DiscoveredBoard({
    required this.ip,
    required this.deviceName,
    required this.teamNumber,
    required this.rssi,
    required this.mac,
    required this.firmware,
    required this.discoveredAt,
  });

  factory DiscoveredBoard.fromJson(Map<String, dynamic> json, String fallbackIp) {
    return DiscoveredBoard(
      ip: json['ip'] as String? ?? fallbackIp,
      deviceName: json['device'] as String? ?? 'LEQs-IoT Node',
      teamNumber: (json['team'] as num?)?.toInt() ?? 1,
      rssi: (json['rssi'] as num?)?.toInt() ?? -60,
      mac: json['mac'] as String? ?? 'Unknown MAC',
      firmware: json['firmware'] as String? ?? 'v1.0',
      discoveredAt: DateTime.now(),
    );
  }

  String get signalQuality {
    if (rssi >= -55) return 'แรงมาก';
    if (rssi >= -70) return 'ดี';
    if (rssi >= -80) return 'ปานกลาง';
    return 'อ่อน';
  }
}
