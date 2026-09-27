import 'dart:async';
import 'package:flutter/foundation.dart';
import '../../data/models/farm_models.dart';
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

  void setTeamNumber(int no) {
    _teamNumber = no;
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
    notifyListeners();
  }

  void resetEmergencyStop() {
    _actuators = _actuators.copyWith(isEmergencyStopped: false);
    _activeAlert = '';
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
