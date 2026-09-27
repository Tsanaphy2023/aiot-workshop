import 'dart:async';
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/farm_models.dart';

/// Service interfacing with Home Assistant REST API
class HomeAssistantService {
  String baseUrl;
  String bearerToken;

  HomeAssistantService({
    this.baseUrl = 'http://homeassistant.local:8123',
    this.bearerToken = '',
  });

  Map<String, String> get _headers => {
        'Authorization': 'Bearer $bearerToken',
        'Content-Type': 'application/json',
      };

  /// Check connection to Home Assistant
  Future<bool> checkConnection() async {
    if (bearerToken.isEmpty) return false;
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/api/'), headers: _headers)
          .timeout(const Duration(seconds: 4));
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  /// Fetch all relevant entity states
  Future<SensorTelemetry?> fetchSensorStates() async {
    if (bearerToken.isEmpty) return null;
    try {
      final res = await http
          .get(Uri.parse('$baseUrl/api/states'), headers: _headers)
          .timeout(const Duration(seconds: 5));
      if (res.statusCode != 200) return null;

      final List<dynamic> data = jsonDecode(res.body);
      double temp = 28.0;
      double hum = 60.0;
      double light = 300.0;
      double soil = 50.0;
      bool waterLow = false;

      for (final item in data) {
        final entityId = item['entity_id'] as String? ?? '';
        final stateStr = item['state'] as String? ?? '';

        if (entityId.contains('temperature') && !entityId.contains('cpu')) {
          temp = double.tryParse(stateStr) ?? temp;
        } else if (entityId.contains('humidity')) {
          hum = double.tryParse(stateStr) ?? hum;
        } else if (entityId.contains('illuminance') ||
            entityId.contains('light_sensor')) {
          light = double.tryParse(stateStr) ?? light;
        } else if (entityId.contains('soil_moisture')) {
          soil = double.tryParse(stateStr) ?? soil;
        } else if (entityId.contains('float') ||
            entityId.contains('water_level')) {
          waterLow = stateStr == 'off' || stateStr == 'dry';
        }
      }

      return SensorTelemetry(
        temperature: temp,
        humidity: hum,
        lightLux: light,
        soilMoisture: soil,
        isWaterLow: waterLow,
        timestamp: DateTime.now(),
      );
    } catch (_) {
      return null;
    }
  }

  /// Call Home Assistant Service (e.g. switch.turn_on, switch.turn_off)
  Future<bool> setSwitch(String entityId, bool turnOn) async {
    if (bearerToken.isEmpty) return false;
    try {
      final service = turnOn ? 'turn_on' : 'turn_off';
      final res = await http.post(
        Uri.parse('$baseUrl/api/services/switch/$service'),
        headers: _headers,
        body: jsonEncode({'entity_id': entityId}),
      );
      return res.statusCode == 200;
    } catch (_) {
      return false;
    }
  }
}
