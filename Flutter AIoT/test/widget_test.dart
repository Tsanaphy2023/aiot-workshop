import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:flutter_aiot/data/repositories/farm_repository.dart';
import 'package:flutter_aiot/data/services/farm_simulator_service.dart';
import 'package:flutter_aiot/data/services/home_assistant_service.dart';
import 'package:flutter_aiot/ui/view_models/farm_view_model.dart';
import 'package:flutter_aiot/main.dart';

void main() {
  testWidgets('SmartFarmApp initializes and renders Dashboard smoke test',
      (WidgetTester tester) async {
    final simulator = FarmSimulatorService();
    final ha = HomeAssistantService();
    final repo = FarmRepository(simulatorService: simulator, haService: ha);
    final vm = FarmViewModel(repository: repo);

    await tester.pumpWidget(
      MultiProvider(
        providers: [
          ChangeNotifierProvider.value(value: vm),
        ],
        child: const SmartFarmApp(),
      ),
    );

    await tester.pump();

    // Verify main screen and sensor titles are rendered
    expect(find.text('CMU AIoT Smart Farm'), findsOneWidget);
    expect(find.text('ความชื้นในดิน (Soil Moisture)'), findsOneWidget);

    vm.dispose();
  });
}
