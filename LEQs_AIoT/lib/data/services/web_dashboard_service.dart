import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/farm_models.dart';

/// Model representing telemetry and actuator states of an area from Web Dashboard
class DashboardAreaState {
  final String key;
  final String name;
  final double soilMoisture;
  final double temperature;
  final double humidity;
  final double lightLux;
  final bool isValveOn;
  final bool isPumpOn;
  final bool isMistOn;
  final bool isFanOn;
  final DateTime lastUpdated;

  DashboardAreaState({
    required this.key,
    required this.name,
    required this.soilMoisture,
    required this.temperature,
    required this.humidity,
    required this.lightLux,
    required this.isValveOn,
    required this.isPumpOn,
    required this.isMistOn,
    required this.isFanOn,
    required this.lastUpdated,
  });

  factory DashboardAreaState.fromJson(String key, Map<String, dynamic> json, DateTime updated) {
    return DashboardAreaState(
      key: key,
      name: json['name'] as String? ?? key,
      soilMoisture: (json['soil'] as num?)?.toDouble() ?? 50.0,
      temperature: (json['temp'] as num?)?.toDouble() ?? 28.0,
      humidity: (json['humidity'] as num?)?.toDouble() ?? 65.0,
      lightLux: (json['light'] as num?)?.toDouble() ?? 40000.0,
      isValveOn: json['valve'] == true,
      isPumpOn: json['pump'] == true,
      isMistOn: json['mist'] == true,
      isFanOn: json['fan'] == true,
      lastUpdated: updated,
    );
  }

  SensorTelemetry toTelemetry() {
    return SensorTelemetry(
      temperature: temperature,
      humidity: humidity,
      lightLux: lightLux,
      soilMoisture: soilMoisture,
      isWaterLow: false,
      timestamp: lastUpdated,
    );
  }
}

/// Service interfacing bidirectional synchronization between Mobile App & Web Dashboard
class WebDashboardService {
  String baseUrl;

  WebDashboardService({
    this.baseUrl = 'http://localhost/cmu_aiot/smart_farm_dashboard/api/api.php',
  });

  String _cleanUrl(String? custom) {
    String url = (custom ?? baseUrl).trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://$url';
    }
    if (!url.contains('api.php')) {
      if (url.endsWith('/')) {
        url = '${url}api/api.php';
      } else {
        url = '$url/api/api.php';
      }
    }
    return url;
  }

  /// Ping/Check connection to Web Dashboard REST API
  Future<bool> checkConnection([String? customUrl]) async {
    try {
      final endpoint = '${_cleanUrl(customUrl)}?action=status';
      final res = await http.get(Uri.parse(endpoint)).timeout(const Duration(seconds: 4));
      if (res.statusCode == 200) {
        final decoded = jsonDecode(res.body);
        return decoded['status'] == 'success';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// Fetch entire dashboard state (all farm areas & actuator statuses)
  Future<Map<String, DashboardAreaState>?> fetchAllAreas([String? customUrl]) async {
    try {
      final endpoint = '${_cleanUrl(customUrl)}?action=status';
      final res = await http.get(Uri.parse(endpoint)).timeout(const Duration(seconds: 4));
      if (res.statusCode != 200) return null;

      final decoded = jsonDecode(res.body);
      if (decoded['status'] != 'success' || decoded['data'] == null) return null;

      final data = decoded['data'] as Map<String, dynamic>;
      final updatedStr = data['last_updated'] as String? ?? '';
      final updated = DateTime.tryParse(updatedStr) ?? DateTime.now();

      final areasJson = data['areas'] as Map<String, dynamic>? ?? {};
      final Map<String, DashboardAreaState> result = {};

      areasJson.forEach((key, val) {
        if (val is Map<String, dynamic>) {
          result[key] = DashboardAreaState.fromJson(key, val, updated);
        }
      });

      return result;
    } catch (_) {
      return null;
    }
  }

  /// Send control command to toggle actuator on Web Dashboard (valve, pump, mist, fan)
  Future<bool> controlActuator({
    required String area,
    required String device,
    required bool state,
    String? customUrl,
  }) async {
    try {
      final endpoint = '${_cleanUrl(customUrl)}?action=control';
      final body = jsonEncode({
        'area': area,
        'device': device,
        'state': state,
      });

      final res = await http.post(
        Uri.parse(endpoint),
        headers: {'Content-Type': 'application/json'},
        body: body,
      ).timeout(const Duration(seconds: 3));

      if (res.statusCode == 200) {
        final decoded = jsonDecode(res.body);
        return decoded['status'] == 'success';
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  /// Send mobile sensor telemetry up to Web Dashboard
  Future<bool> sendTelemetry({
    required String area,
    required SensorTelemetry telemetry,
    String? customUrl,
  }) async {
    try {
      final endpoint = '${_cleanUrl(customUrl)}?action=telemetry';
      final body = jsonEncode({
        'area': area,
        'soil': telemetry.soilMoisture,
        'temp': telemetry.temperature,
        'humidity': telemetry.humidity,
        'light': telemetry.lightLux.toInt(),
      });

      final res = await http.post(
        Uri.parse(endpoint),
        headers: {'Content-Type': 'application/json'},
        body: body,
      ).timeout(const Duration(seconds: 3));

      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
