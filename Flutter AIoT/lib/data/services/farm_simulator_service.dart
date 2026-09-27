import 'dart:async';
import 'dart:math';
import '../models/farm_models.dart';

/// Interactive Smart Farm Simulator Service
/// Accurately simulates GoGo-IoT SHT30, BH1750, soil moisture, float switch,
/// and ESP-NOW bridge telemetries from the workshop.
class FarmSimulatorService {
  final _random = Random();
  Timer? _timer;
  final _sensorStreamController = StreamController<SensorTelemetry>.broadcast();
  final _espNowStreamController = StreamController<EspNowTelemetry>.broadcast();

  SensorTelemetry _currentSensors = SensorTelemetry.initial();
  EspNowTelemetry _currentEspNow = EspNowTelemetry.initial();
  bool _isPumpActive = false;
  bool _isGrowLightActive = false;
  bool _simulateLinkLoss = false;

  Stream<SensorTelemetry> get sensorStream => _sensorStreamController.stream;
  Stream<EspNowTelemetry> get espNowStream => _espNowStreamController.stream;

  SensorTelemetry get currentSensors => _currentSensors;
  EspNowTelemetry get currentEspNow => _currentEspNow;

  void startSimulation() {
    _timer?.cancel();
    _timer = Timer.periodic(const Duration(seconds: 1), _tick);
  }

  void stopSimulation() {
    _timer?.cancel();
  }

  void setActuatorState({required bool isPumpOn, required bool isGrowLightOn}) {
    _isPumpActive = isPumpOn;
    _isGrowLightActive = isGrowLightOn;
  }

  void toggleFloatSwitch(bool isWaterLow) {
    _currentSensors = _currentSensors.copyWith(isWaterLow: isWaterLow);
    _sensorStreamController.add(_currentSensors);
  }

  void toggleEspNowLinkFailure(bool forceDisconnect) {
    _simulateLinkLoss = forceDisconnect;
    _currentEspNow = _currentEspNow.copyWith(
      isLinkConnected: !forceDisconnect,
      rssi: forceDisconnect ? -99 : -42,
    );
    _espNowStreamController.add(_currentEspNow);
  }

  void _tick(Timer timer) {
    final now = DateTime.now();

    // 1. Temperature natural fluctuation (27.5 - 31.0 °C)
    final tempDelta = (_random.nextDouble() - 0.5) * 0.15;
    double newTemp = (_currentSensors.temperature + tempDelta).clamp(24.0, 38.0);

    // 2. Humidity fluctuation (55 - 75%)
    final humDelta = (_random.nextDouble() - 0.5) * 0.2;
    double newHum = (_currentSensors.humidity + humDelta).clamp(40.0, 95.0);

    // 3. Light Lux: Boosted if grow light is on
    double baseLight = 320.0 + sin(now.second * 0.1) * 30.0;
    if (_isGrowLightActive) {
      baseLight += 450.0;
    }
    double newLight = max(50.0, baseLight + (_random.nextDouble() * 20.0));

    // 4. Soil moisture dynamics:
    // If pump is ON, moisture climbs +0.6% / sec up to 88%
    // If pump is OFF, moisture slowly dries -0.05% / sec
    double newSoil = _currentSensors.soilMoisture;
    if (_isPumpActive) {
      newSoil = min(88.0, newSoil + 0.65);
    } else {
      newSoil = max(20.0, newSoil - 0.05);
    }

    _currentSensors = _currentSensors.copyWith(
      temperature: double.parse(newTemp.toStringAsFixed(1)),
      humidity: double.parse(newHum.toStringAsFixed(1)),
      lightLux: double.parse(newLight.toStringAsFixed(0)),
      soilMoisture: double.parse(newSoil.toStringAsFixed(1)),
      timestamp: now,
    );
    _sensorStreamController.add(_currentSensors);

    // 5. ESP-NOW Bridge packets every 3 seconds (as in Activity 9-11)
    if (timer.tick % 3 == 0) {
      if (!_simulateLinkLoss) {
        final rssiVariance = _random.nextInt(5) - 2;
        final newRssi = (-42 + rssiVariance).clamp(-85, -35);
        _currentEspNow = _currentEspNow.copyWith(
          packetCount: _currentEspNow.packetCount + 1,
          rssi: newRssi,
          isLinkConnected: true,
          lastPacketTime: now,
          humDirect: _currentSensors.humidity,
          humEspNow: _currentSensors.humidity,
          lightDirect: _currentSensors.lightLux,
          lightEspNow: _currentSensors.lightLux,
        );
      } else {
        // Link lost
        _currentEspNow = _currentEspNow.copyWith(
          packetLost: _currentEspNow.packetLost + 1,
          isLinkConnected: false,
        );
      }
      _espNowStreamController.add(_currentEspNow);
    }
  }

  void dispose() {
    _timer?.cancel();
    _sensorStreamController.close();
    _espNowStreamController.close();
  }
}
