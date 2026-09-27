import 'dart:async';
import '../models/farm_models.dart';
import '../services/farm_simulator_service.dart';
import '../services/home_assistant_service.dart';

/// Single source of truth for Farm telemetry, Actuation, and Safety Rules
class FarmRepository {
  final FarmSimulatorService _simulatorService;
  final HomeAssistantService haService;
  bool isUsingSimulator = true;
  final List<HistoryRecord> _history = [];
  final _historyStreamController =
      StreamController<List<HistoryRecord>>.broadcast();

  FarmRepository({
    required FarmSimulatorService simulatorService,
    required this.haService,
  })  : _simulatorService = simulatorService {
    _initHistory();
  }

  Stream<SensorTelemetry> get sensorStream => _simulatorService.sensorStream;
  Stream<EspNowTelemetry> get espNowStream => _simulatorService.espNowStream;
  Stream<List<HistoryRecord>> get historyStream =>
      _historyStreamController.stream;

  List<HistoryRecord> get currentHistory => List.unmodifiable(_history);

  void start() {
    _simulatorService.startSimulation();
  }

  void stop() {
    _simulatorService.stopSimulation();
  }

  void updateActuatorSimulation({
    required bool isPumpOn,
    required bool isGrowLightOn,
  }) {
    _simulatorService.setActuatorState(
      isPumpOn: isPumpOn,
      isGrowLightOn: isGrowLightOn,
    );
  }

  void simulateWaterLow(bool isWaterLow) {
    _simulatorService.toggleFloatSwitch(isWaterLow);
  }

  void simulateEspNowLoss(bool forceLoss) {
    _simulatorService.toggleEspNowLinkFailure(forceLoss);
  }

  void recordHistory(SensorTelemetry sensor, bool isPumpActive) {
    _history.add(HistoryRecord(
      timestamp: sensor.timestamp,
      temperature: sensor.temperature,
      humidity: sensor.humidity,
      soilMoisture: sensor.soilMoisture,
      lightLux: sensor.lightLux,
      isPumpActive: isPumpActive,
    ));

    // Keep up to 60 historical data points for smooth graphs
    if (_history.length > 60) {
      _history.removeAt(0);
    }
    _historyStreamController.add(_history);
  }

  void _initHistory() {
    final now = DateTime.now();
    for (int i = 30; i >= 0; i--) {
      final t = now.subtract(Duration(minutes: i * 2));
      _history.add(HistoryRecord(
        timestamp: t,
        temperature: 28.0 + (i % 5) * 0.3,
        humidity: 60.0 + (i % 4) * 0.5,
        soilMoisture: 55.0 - (i * 0.4),
        lightLux: 300.0 + (i * 5),
        isPumpActive: i == 5 || i == 6,
      ));
    }
  }

  void dispose() {
    _simulatorService.dispose();
    _historyStreamController.close();
  }
}
