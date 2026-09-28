import 'dart:async';
import '../models/farm_models.dart';
import '../models/board_discovery_model.dart';
import '../services/farm_simulator_service.dart';
import '../services/home_assistant_service.dart';
import '../services/direct_board_service.dart';
import '../services/board_discovery_service.dart';
import '../services/leaf_disease_service.dart';
import '../services/predictive_moisture_service.dart';
import '../services/explainable_ai_service.dart';
import '../services/web_dashboard_service.dart';

enum ConnectionMode {
  simulator,
  directBoard,
  homeAssistant,
  webDashboard,
}

/// Single source of truth for Farm telemetry, Actuation, and Safety Rules
class FarmRepository {
  final FarmSimulatorService _simulatorService;
  final HomeAssistantService haService;
  final DirectBoardService directBoardService;
  final BoardDiscoveryService discoveryService;
  final LeafDiseaseService leafDiseaseService;
  final PredictiveMoistureService predictiveMoistureService;
  final ExplainableAiService explainableAiService;
  final WebDashboardService webDashboardService;

  ConnectionMode connectionMode = ConnectionMode.simulator;
  String? connectedBoardIp;
  String? connectedBoardName;

  String? connectedWebDashboardUrl;
  String currentWebDashboardArea = 'flower';
  Map<String, DashboardAreaState> lastDashboardAreas = {};

  final List<HistoryRecord> _history = [];
  final _historyStreamController = StreamController<List<HistoryRecord>>.broadcast();
  final _sensorStreamController = StreamController<SensorTelemetry>.broadcast();
  StreamSubscription<SensorTelemetry>? _simulatorSensorSub;
  Timer? _directBoardPollTimer;
  Timer? _webDashboardPollTimer;

  FarmRepository({
    required FarmSimulatorService simulatorService,
    required this.haService,
    DirectBoardService? directBoardService,
    BoardDiscoveryService? discoveryService,
    LeafDiseaseService? leafDiseaseService,
    PredictiveMoistureService? predictiveMoistureService,
    ExplainableAiService? explainableAiService,
    WebDashboardService? webDashboardService,
  })  : _simulatorService = simulatorService,
        directBoardService = directBoardService ?? DirectBoardService(),
        discoveryService = discoveryService ?? BoardDiscoveryService(),
        leafDiseaseService = leafDiseaseService ?? LeafDiseaseService(),
        predictiveMoistureService = predictiveMoistureService ?? PredictiveMoistureService(),
        explainableAiService = explainableAiService ?? ExplainableAiService(),
        webDashboardService = webDashboardService ?? WebDashboardService() {
    _initHistory();
  }

  bool get isUsingSimulator => connectionMode == ConnectionMode.simulator;
  bool get isDirectBoard => connectionMode == ConnectionMode.directBoard;
  bool get isWebDashboard => connectionMode == ConnectionMode.webDashboard;

  Stream<SensorTelemetry> get sensorStream => _sensorStreamController.stream;
  Stream<EspNowTelemetry> get espNowStream => _simulatorService.espNowStream;
  Stream<List<HistoryRecord>> get historyStream => _historyStreamController.stream;

  List<HistoryRecord> get currentHistory => List.unmodifiable(_history);

  void start() {
    _simulatorService.startSimulation();
    _simulatorSensorSub = _simulatorService.sensorStream.listen((data) {
      if (connectionMode == ConnectionMode.simulator) {
        _sensorStreamController.add(data);
      }
    });
  }

  void stop() {
    _simulatorService.stopSimulation();
    _directBoardPollTimer?.cancel();
  }

  /// Connect to physical GoGo-IoT / LEQs-IoT board via Wi-Fi IP
  Future<bool> connectToDirectBoard(String ip, {String? deviceName}) async {
    final cleanIp = ip.trim().replaceAll('http://', '').replaceAll('/', '');
    final info = await directBoardService.pingBoard(cleanIp);
    if (info != null) {
      connectedBoardIp = cleanIp;
      connectedBoardName = deviceName ?? info['device'] as String? ?? 'LEQs-IoT Node';
      connectionMode = ConnectionMode.directBoard;

      _webDashboardPollTimer?.cancel();
      // Start periodic direct board telemetry polling (1.2s interval)
      _directBoardPollTimer?.cancel();
      _directBoardPollTimer = Timer.periodic(const Duration(milliseconds: 1200), (_) async {
        if (connectionMode == ConnectionMode.directBoard && connectedBoardIp != null) {
          final telemetry = await directBoardService.fetchSensors(connectedBoardIp!);
          if (telemetry != null) {
            _sensorStreamController.add(telemetry);
          }
        }
      });
      return true;
    }
    return false;
  }

  /// Connect to Web Dashboard REST API (http://IP/cmu_aiot/smart_farm_dashboard/api/api.php)
  Future<bool> connectToWebDashboard(String url, {String area = 'flower'}) async {
    final ok = await webDashboardService.checkConnection(url);
    if (ok) {
      connectedWebDashboardUrl = url;
      currentWebDashboardArea = area;
      connectionMode = ConnectionMode.webDashboard;

      _directBoardPollTimer?.cancel();
      _webDashboardPollTimer?.cancel();

      // Poll Web Dashboard status every 1.2 seconds
      _webDashboardPollTimer = Timer.periodic(const Duration(milliseconds: 1200), (_) async {
        if (connectionMode == ConnectionMode.webDashboard && connectedWebDashboardUrl != null) {
          final areas = await webDashboardService.fetchAllAreas(connectedWebDashboardUrl);
          if (areas != null && areas.containsKey(currentWebDashboardArea)) {
            lastDashboardAreas = areas;
            final activeArea = areas[currentWebDashboardArea]!;
            _sensorStreamController.add(activeArea.toTelemetry());
          }
        }
      });
      return true;
    }
    return false;
  }

  /// Change active monitored area on Web Dashboard (flower, corn, grass)
  void setWebDashboardArea(String area) {
    currentWebDashboardArea = area;
    if (lastDashboardAreas.containsKey(area)) {
      _sensorStreamController.add(lastDashboardAreas[area]!.toTelemetry());
    }
  }

  /// Disconnect physical board or web dashboard and return to Simulator
  void returnToSimulator() {
    _directBoardPollTimer?.cancel();
    _webDashboardPollTimer?.cancel();
    connectedBoardIp = null;
    connectedBoardName = null;
    connectedWebDashboardUrl = null;
    connectionMode = ConnectionMode.simulator;
  }

  /// Scan for GoGo-IoT / LEQs IoT boards on the current Wi-Fi LAN
  Future<List<DiscoveredBoard>> scanForBoards() async {
    return await discoveryService.scanForBoards();
  }

  /// Update actuators (syncs with physical board or web dashboard)
  void updateActuatorSimulation({
    required bool isPumpOn,
    required bool isGrowLightOn,
  }) {
    _simulatorService.setActuatorState(
      isPumpOn: isPumpOn,
      isGrowLightOn: isGrowLightOn,
    );

    // If connected to physical hardware, send command over Wi-Fi
    if (connectionMode == ConnectionMode.directBoard && connectedBoardIp != null) {
      directBoardService.setRelay(connectedBoardIp!, 1, isPumpOn);
      directBoardService.setRelay(connectedBoardIp!, 2, isGrowLightOn);
    }

    // If connected to Web Dashboard, sync command via REST API
    if (connectionMode == ConnectionMode.webDashboard && connectedWebDashboardUrl != null) {
      webDashboardService.controlActuator(
        area: currentWebDashboardArea,
        device: 'pump',
        state: isPumpOn,
        customUrl: connectedWebDashboardUrl,
      );
      webDashboardService.controlActuator(
        area: currentWebDashboardArea,
        device: 'valve',
        state: isPumpOn,
        customUrl: connectedWebDashboardUrl,
      );
      webDashboardService.controlActuator(
        area: currentWebDashboardArea,
        device: 'fan',
        state: isGrowLightOn,
        customUrl: connectedWebDashboardUrl,
      );
    }
  }

  /// Send Emergency Stop directly to hardware or Web Dashboard
  void triggerEmergencyStop(bool isStopped) {
    if (connectionMode == ConnectionMode.directBoard && connectedBoardIp != null) {
      directBoardService.setEmergencyStop(connectedBoardIp!, isStopped);
    }
    if (connectionMode == ConnectionMode.webDashboard && connectedWebDashboardUrl != null && isStopped) {
      webDashboardService.controlActuator(
        area: currentWebDashboardArea,
        device: 'pump',
        state: false,
        customUrl: connectedWebDashboardUrl,
      );
      webDashboardService.controlActuator(
        area: currentWebDashboardArea,
        device: 'valve',
        state: false,
        customUrl: connectedWebDashboardUrl,
      );
    }
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
    _simulatorSensorSub?.cancel();
    _directBoardPollTimer?.cancel();
    _webDashboardPollTimer?.cancel();
    _simulatorService.dispose();
    _sensorStreamController.close();
    _historyStreamController.close();
  }
}
