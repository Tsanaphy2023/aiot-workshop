import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'data/repositories/farm_repository.dart';
import 'data/services/farm_simulator_service.dart';
import 'data/services/home_assistant_service.dart';
import 'ui/core/app_theme.dart';
import 'ui/view_models/farm_view_model.dart';
import 'ui/views/main_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();

  // Instantiate Data Layer services and repository
  final simulatorService = FarmSimulatorService();
  final haService = HomeAssistantService();
  final repository = FarmRepository(
    simulatorService: simulatorService,
    haService: haService,
  );

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(
          create: (_) => FarmViewModel(repository: repository),
        ),
      ],
      child: const SmartFarmApp(),
    ),
  );
}

class SmartFarmApp extends StatefulWidget {
  const SmartFarmApp({super.key});

  @override
  State<SmartFarmApp> createState() => _SmartFarmAppState();
}

class _SmartFarmAppState extends State<SmartFarmApp> {
  ThemeMode _themeMode = ThemeMode.dark;

  void _toggleTheme() {
    setState(() {
      _themeMode =
          _themeMode == ThemeMode.dark ? ThemeMode.light : ThemeMode.dark;
    });
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'CMU AIoT Smart Farm',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme(),
      darkTheme: AppTheme.darkTheme(),
      themeMode: _themeMode,
      home: MainScreen(
        onToggleTheme: _toggleTheme,
        isDarkMode: _themeMode == ThemeMode.dark,
      ),
    );
  }
}
