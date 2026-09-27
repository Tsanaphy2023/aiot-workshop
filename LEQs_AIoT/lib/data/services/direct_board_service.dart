import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/farm_models.dart';

/// Direct HTTP REST Service communicating with ESP32 GoGo-IoT / LEQs IoT hardware
class DirectBoardService {
  final http.Client _client;

  DirectBoardService({http.Client? client}) : _client = client ?? http.Client();

  /// Check connectivity and retrieve board info
  Future<Map<String, dynamic>?> pingBoard(String ip) async {
    try {
      final cleanIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
      final url = Uri.parse('http://$cleanIp/api/info');
      final res = await _client.get(url).timeout(const Duration(milliseconds: 1800));
      if (res.statusCode == 200) {
        return jsonDecode(res.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return null;
  }

  /// Fetch live sensor telemetry directly from hardware
  Future<SensorTelemetry?> fetchSensors(String ip) async {
    try {
      final cleanIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
      final url = Uri.parse('http://$cleanIp/api/sensors');
      final res = await _client.get(url).timeout(const Duration(milliseconds: 2000));
      if (res.statusCode == 200) {
        final data = jsonDecode(res.body) as Map<String, dynamic>;
        return SensorTelemetry(
          temperature: (data['temperature'] as num?)?.toDouble() ?? 28.0,
          humidity: (data['humidity'] as num?)?.toDouble() ?? 60.0,
          soilMoisture: (data['soil_moisture'] as num?)?.toDouble() ?? 50.0,
          lightLux: (data['light_lux'] as num?)?.toDouble() ?? 300.0,
          isWaterLow: data['water_low'] as bool? ?? false,
          timestamp: DateTime.now(),
        );
      }
    } catch (_) {}
    return null;
  }

  /// Toggle hardware relay (ch 1: Pump, ch 2: Light)
  Future<bool> setRelay(String ip, int channel, bool state) async {
    try {
      final cleanIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
      final url = Uri.parse('http://$cleanIp/api/relay?ch=$channel&state=${state ? 1 : 0}');
      final res = await _client.get(url).timeout(const Duration(milliseconds: 2000));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Trigger or release Emergency Stop on the hardware
  Future<bool> setEmergencyStop(String ip, bool isStop) async {
    try {
      final cleanIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
      final url = Uri.parse('http://$cleanIp/api/estop?state=${isStop ? 1 : 0}');
      final res = await _client.get(url).timeout(const Duration(milliseconds: 2000));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
