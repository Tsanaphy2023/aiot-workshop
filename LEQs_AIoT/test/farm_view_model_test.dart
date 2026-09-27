import 'package:flutter_test/flutter_test.dart';
import 'package:leqs_aiot/data/repositories/farm_repository.dart';
import 'package:leqs_aiot/data/services/farm_simulator_service.dart';
import 'package:leqs_aiot/data/services/home_assistant_service.dart';
import 'package:leqs_aiot/ui/view_models/farm_view_model.dart';

void main() {
  group('FarmViewModel & Fail-Safe Logic Tests', () {
    late FarmSimulatorService simulator;
    late HomeAssistantService ha;
    late FarmRepository repository;
    late FarmViewModel viewModel;

    setUp(() {
      simulator = FarmSimulatorService();
      ha = HomeAssistantService();
      repository = FarmRepository(simulatorService: simulator, haService: ha);
      viewModel = FarmViewModel(repository: repository);
    });

    tearDown(() {
      viewModel.dispose();
    });

    test('Initial states adhere to smart farm defaults', () {
      expect(viewModel.sensors.temperature, greaterThan(20.0));
      expect(viewModel.sensors.humidity, greaterThan(40.0));
      expect(viewModel.actuators.isEmergencyStopped, isFalse);
      expect(viewModel.actuators.isAutoMode, isTrue);
      expect(viewModel.automation.dryRunProtectionEnabled, isTrue);
    });

    test('Dry-run protection prevents pump activation when water is low', () {
      // Simulate low water
      viewModel.simulateWaterFloatToggle();
      expect(viewModel.sensors.isWaterLow, isTrue);

      // Attempt to turn on pump
      viewModel.togglePump(true);
      expect(viewModel.actuators.isPumpOn, isFalse);
      expect(viewModel.activeAlert, contains('ระดับน้ำในถังต่ำ'));
    });

    test('Emergency stop immediately cuts all relays', () {
      viewModel.toggleGrowLight(true);
      expect(viewModel.actuators.isGrowLightOn, isTrue);

      viewModel.triggerEmergencyStop();
      expect(viewModel.actuators.isEmergencyStopped, isTrue);
      expect(viewModel.actuators.isGrowLightOn, isFalse);
      expect(viewModel.actuators.isPumpOn, isFalse);
      expect(viewModel.activeAlert, contains('หยุดฉุกเฉิน'));
    });

    test('ESP-NOW link failure simulation raises link disconnected status', () {
      expect(viewModel.espNow.isLinkConnected, isTrue);
      viewModel.simulateEspNowLinkToggle();
      expect(viewModel.espNow.isLinkConnected, isFalse);
      expect(viewModel.activeAlert, contains('ESP-NOW'));
    });
  });
}
