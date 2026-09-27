import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../data/models/farm_models.dart';
import '../../data/models/board_discovery_model.dart';
import '../../data/repositories/farm_repository.dart';

class FarmViewModel extends ChangeNotifier {
  final FarmRepository _repository;

  StreamSubscription<SensorTelemetry>? _sensorSub;
  StreamSubscription<EspNowTelemetry>? _espNowSub;
  StreamSubscription<List<HistoryRecord>>? _historySub;
  Timer? _countdownTimer;
  Timer? _deadmanTimer;

  SensorTelemetry _sensors = SensorTelemetry.initial();
  ActuatorState _actuators = ActuatorState.initial();
  EspNowTelemetry _espNow = EspNowTelemetry.initial();
  AutomationSettings _automation = AutomationSettings.initial();
  List<HistoryRecord> _history = [];

  int _teamNumber = 1;
  String _activeAlert = '';
  int _secondsSinceLastPacket = 0;

  // Board Discovery & Direct Connection State
  List<DiscoveredBoard> _discoveredBoards = [];
  bool _isScanning = false;
  String _scanStatusMessage = '';

  // Deep Learning & Vision AI State
  LeafDiseaseDiagnosis? _currentLeafDiagnosis;
  bool _isDiagnosingLeaf = false;

  FarmViewModel({required FarmRepository repository})
      : _repository = repository {
    _init();
  }

  SensorTelemetry get sensors => _sensors;
  ActuatorState get actuators => _actuators;
  EspNowTelemetry get espNow => _espNow;
  AutomationSettings get automation => _automation;
  List<HistoryRecord> get history => _history;
  int get teamNumber => _teamNumber;
  String get activeAlert => _activeAlert;
  int get secondsSinceLastPacket => _secondsSinceLastPacket;
  bool get isSimulatorActive => _repository.isUsingSimulator;
  bool get isDirectBoard => _repository.isDirectBoard;
  ConnectionMode get connectionMode => _repository.connectionMode;
  String? get connectedBoardIp => _repository.connectedBoardIp;
  String? get connectedBoardName => _repository.connectedBoardName;

  List<DiscoveredBoard> get discoveredBoards => _discoveredBoards;
  bool get isScanning => _isScanning;
  String get scanStatusMessage => _scanStatusMessage;

  // AI & Agriphysics Getters
  bool get isDiagnosingLeaf => _isDiagnosingLeaf;
  LeafDiseaseDiagnosis get currentLeafDiagnosis =>
      _currentLeafDiagnosis ?? _repository.leafDiseaseService.getSampleDiagnosis('powdery_mildew');

  ExplainableAiRecommendation get aiRecommendation =>
      _repository.explainableAiService.evaluateIrrigation(
        telemetry: _sensors,
        settings: _automation,
        isPumpActive: _actuators.isPumpOn,
      );

  List<SoilPredictionPoint> get soilPredictions =>
      _repository.predictiveMoistureService.forecastSoilMoisture(
        currentMoisture: _sensors.soilMoisture,
        currentVpd: _sensors.vpd,
        currentLux: _sensors.lightLux,
        isPumpRunning: _actuators.isPumpOn,
        wiltingThreshold: _automation.soilMoistureLowThreshold,
      );

  /// Trigger Vision Deep Learning diagnosis for plant leaf
  Future<void> diagnoseLeaf({String? sampleId}) async {
    _isDiagnosingLeaf = true;
    notifyListeners();

    try {
      final diag = await _repository.leafDiseaseService.diagnoseFromImage(targetDiseaseId: sampleId);
      _currentLeafDiagnosis = diag;
    } catch (_) {
    } finally {
      _isDiagnosingLeaf = false;
      notifyListeners();
    }
  }

  void setTeamNumber(int no) {
    _teamNumber = no;
    notifyListeners();
  }

  /// Scan for physical GoGo-IoT / LEQs IoT hardware on Wi-Fi
  Future<void> scanForBoards() async {
    _isScanning = true;
    _scanStatusMessage = 'กำลังสแกนหาบอร์ด GoGo-IoT / LEQs IoT บนเครือข่าย Wi-Fi...';
    notifyListeners();

    try {
      final results = await _repository.scanForBoards();
      _discoveredBoards = results;
      if (results.isEmpty) {
        _scanStatusMessage = 'ไม่พบบอร์ดอัตโนมัติ (กรุณาตรวจสอบว่าบอร์ดและมือถือต่อ Wi-Fi เดียวกัน หรือใช้การกำหนด IP ด้วยตนเอง)';
      } else {
        _scanStatusMessage = 'ตรวจพบบอร์ด ${results.length} อุปกรณ์พร้อมเชื่อมต่อ';
      }
    } catch (e) {
      _scanStatusMessage = 'เกิดข้อผิดพลาดในการสแกน: $e';
    } finally {
      _isScanning = false;
      notifyListeners();
    }
  }

  /// Connect to a discovered board
  Future<bool> connectToBoard(DiscoveredBoard board) async {
    final success = await _repository.connectToDirectBoard(board.ip, deviceName: board.deviceName);
    if (success) {
      if (board.teamNumber > 0) {
        _teamNumber = board.teamNumber;
      }
      _activeAlert = '';
      notifyListeners();
    }
    return success;
  }

  /// Connect to board via manual IP address
  Future<bool> connectToManualIp(String ip) async {
    final success = await _repository.connectToDirectBoard(ip);
    if (success) {
      _activeAlert = '';
      notifyListeners();
    }
    return success;
  }

  /// Disconnect physical board and switch back to Simulator
  void disconnectToSimulator() {
    _repository.returnToSimulator();
    notifyListeners();
  }

  void _init() {
    _repository.start();

    _sensorSub = _repository.sensorStream.listen((data) {
      _sensors = data;
      _repository.recordHistory(data, _actuators.isPumpOn);
      _evaluateAutomationRules();
      notifyListeners();
    });

    _espNowSub = _repository.espNowStream.listen((data) {
      _espNow = data;
      if (data.isLinkConnected) {
        _secondsSinceLastPacket = 0;
        if (_activeAlert.contains('แปลงเงียบ')) {
          _activeAlert = '';
        }
      }
      notifyListeners();
    });

    _history = _repository.currentHistory;
    _historySub = _repository.historyStream.listen((data) {
      _history = List.from(data);
      notifyListeners();
    });

    // Deadman watchdog timer tick every 1 sec
    _deadmanTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      _secondsSinceLastPacket++;
      if (!_espNow.isLinkConnected || _secondsSinceLastPacket > _automation.watchdogAlertTimeoutSeconds) {
        if (!_activeAlert.contains('แปลงเงียบ')) {
          _activeAlert = 'แปลงเงียบ: ขาดการติดต่อจากแปลงเกิน ${_automation.watchdogAlertTimeoutSeconds} วินาที (Watchdog Alert)';
          notifyListeners();
        }
      }
    });
  }

  // Actuator Control
  void togglePump(bool targetState) {
    if (_actuators.isEmergencyStopped) {
      _activeAlert = 'ไม่สามารถเปิดปั๊มได้: อยู่ในสถานะหยุดฉุกเฉิน (E-Stop)';
      notifyListeners();
      return;
    }

    if (targetState && _sensors.isWaterLow && _automation.dryRunProtectionEnabled) {
      _activeAlert = 'ตัดการทำงาน: ระดับน้ำในถังต่ำ ป้องกันปั๊มไหม้ (Dry-Run Protection)';
      notifyListeners();
      return;
    }

    if (targetState) {
      _startPumpWithTimer(_automation.maxPumpRunSeconds);
    } else {
      _stopPump();
    }
  }

  void toggleGrowLight(bool targetState) {
    _actuators = _actuators.copyWith(isGrowLightOn: targetState);
    _repository.updateActuatorSimulation(
      isPumpOn: _actuators.isPumpOn,
      isGrowLightOn: targetState,
    );
    notifyListeners();
  }

  void toggleAutoMode(bool targetState) {
    _actuators = _actuators.copyWith(isAutoMode: targetState);
    notifyListeners();
  }

  void triggerEmergencyStop() {
    _stopPump();
    _actuators = _actuators.copyWith(
      isEmergencyStopped: true,
      isGrowLightOn: false,
    );
    _activeAlert = 'ระบบหยุดฉุกเฉินทำงาน (Emergency Stop Active)! รีเลย์ทั้งหมดถูกตัด';
    _repository.updateActuatorSimulation(isPumpOn: false, isGrowLightOn: false);
    _repository.triggerEmergencyStop(true);
    notifyListeners();
  }

  void resetEmergencyStop() {
    _actuators = _actuators.copyWith(isEmergencyStopped: false);
    _activeAlert = '';
    _repository.triggerEmergencyStop(false);
    notifyListeners();
  }

  void dismissAlert() {
    _activeAlert = '';
    notifyListeners();
  }

  // Automation Thresholds
  void updateThresholds({
    double? lowThreshold,
    double? highThreshold,
    int? maxRunSeconds,
    bool? dryRunEnabled,
  }) {
    _automation = _automation.copyWith(
      soilMoistureLowThreshold: lowThreshold,
      soilMoistureHighThreshold: highThreshold,
      maxPumpRunSeconds: maxRunSeconds,
      dryRunProtectionEnabled: dryRunEnabled,
    );
    notifyListeners();
  }

  // Failure lab simulations
  void simulateWaterFloatToggle() {
    final nextState = !_sensors.isWaterLow;
    _sensors = _sensors.copyWith(isWaterLow: nextState);
    _repository.simulateWaterLow(nextState);
    if (nextState && _actuators.isPumpOn && _automation.dryRunProtectionEnabled) {
      _stopPump();
      _activeAlert = 'ตรวจพบน้ำแห้ง: สวิตช์ลูกลอยทำงาน ตัดปั๊มทันที (Dry-Run Failure Lab)';
    }
    notifyListeners();
  }

  void simulateEspNowLinkToggle() {
    final willDisconnect = _espNow.isLinkConnected;
    _espNow = _espNow.copyWith(isLinkConnected: !willDisconnect);
    _repository.simulateEspNowLoss(willDisconnect);
    if (willDisconnect) {
      _activeAlert = 'จำลองปัญหา ESP-NOW: บอร์ดแปลงหยุดส่งสัญญาณ (Link Disconnected)';
    } else {
      _activeAlert = '';
    }
    notifyListeners();
  }

  void _startPumpWithTimer(int seconds) {
    _countdownTimer?.cancel();
    _actuators = _actuators.copyWith(
      isPumpOn: true,
      pumpRemainingSeconds: seconds,
    );
    _repository.updateActuatorSimulation(
      isPumpOn: true,
      isGrowLightOn: _actuators.isGrowLightOn,
    );

    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (timer) {
      if (_actuators.pumpRemainingSeconds <= 1) {
        _stopPump();
      } else {
        _actuators = _actuators.copyWith(
          pumpRemainingSeconds: _actuators.pumpRemainingSeconds - 1,
        );
        notifyListeners();
      }
    });
    notifyListeners();
  }

  void _stopPump() {
    _countdownTimer?.cancel();
    _actuators = _actuators.copyWith(
      isPumpOn: false,
      pumpRemainingSeconds: 0,
    );
    _repository.updateActuatorSimulation(
      isPumpOn: false,
      isGrowLightOn: _actuators.isGrowLightOn,
    );
    notifyListeners();
  }

  void _evaluateAutomationRules() {
    if (!_actuators.isAutoMode || _actuators.isEmergencyStopped) return;

    // Safety Interlock
    if (_sensors.isWaterLow && _automation.dryRunProtectionEnabled) {
      if (_actuators.isPumpOn) {
        _stopPump();
        _activeAlert = 'กฎความปลอดภัย: ระดับน้ำต่ำ ตัดการทำงานปั๊ม';
      }
      return;
    }

    // Auto watering rule
    if (_sensors.soilMoisture < _automation.soilMoistureLowThreshold) {
      if (!_actuators.isPumpOn) {
        _startPumpWithTimer(_automation.maxPumpRunSeconds);
      }
    } else if (_sensors.soilMoisture >= _automation.soilMoistureHighThreshold) {
      if (_actuators.isPumpOn) {
        _stopPump();
      }
    }
  }

  @override
  void dispose() {
    _sensorSub?.cancel();
    _espNowSub?.cancel();
    _historySub?.cancel();
    _countdownTimer?.cancel();
    _deadmanTimer?.cancel();
    _repository.dispose();
    super.dispose();
  }
}
