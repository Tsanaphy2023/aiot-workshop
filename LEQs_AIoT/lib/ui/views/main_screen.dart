import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../view_models/farm_view_model.dart';
import 'tabs/dashboard_tab.dart';
import 'tabs/control_tab.dart';
import 'tabs/automation_tab.dart';
import 'tabs/espnow_tab.dart';
import 'tabs/history_tab.dart';

class MainScreen extends StatefulWidget {
  final VoidCallback onToggleTheme;
  final bool isDarkMode;

  const MainScreen({
    super.key,
    required this.onToggleTheme,
    required this.isDarkMode,
  });

  @override
  State<MainScreen> createState() => _MainScreenState();
}

class _MainScreenState extends State<MainScreen> {
  int _currentIndex = 0;

  final List<Widget> _tabs = const [
    DashboardTab(),
    ControlTab(),
    AutomationTab(),
    EspNowTab(),
    HistoryTab(),
  ];

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();

    return Scaffold(
      appBar: AppBar(
        titleSpacing: 12,
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(8),
              ),
              child: const Icon(Icons.eco, color: Color(0xFF10B981), size: 20),
            ),
            const SizedBox(width: 8),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'LEQs AIoT',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  Text(
                    'ESP-NOW • GoGo-IoT • HA',
                    style: TextStyle(fontSize: 10, color: Colors.grey.shade400),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          // Team Selector Button (Compact for smartphone)
          ActionChip(
            visualDensity: VisualDensity.compact,
            padding: const EdgeInsets.symmetric(horizontal: 2),
            avatar: const Icon(Icons.badge_outlined, size: 14),
            label: Text(
              'กลุ่ม ${vm.teamNumber}',
              style: const TextStyle(fontSize: 12),
            ),
            onPressed: () => _showTeamPicker(context, vm),
          ),
          const SizedBox(width: 4),

          // Theme Toggle
          IconButton(
            visualDensity: VisualDensity.compact,
            icon: Icon(widget.isDarkMode ? Icons.light_mode : Icons.dark_mode, size: 20),
            tooltip: 'เปลี่ยนธีมสี',
            onPressed: widget.onToggleTheme,
          ),
          const SizedBox(width: 6),
        ],
      ),
      body: Column(
        children: [
          // Global Alert Notification Banner
          if (vm.activeAlert.isNotEmpty) ...[
            Container(
              width: double.infinity,
              color: const Color(0xFFDC2626),
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
              child: Row(
                children: [
                  const Icon(Icons.warning, color: Colors.white, size: 20),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      vm.activeAlert,
                      style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 12,
                      ),
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: Colors.white, size: 18),
                    padding: EdgeInsets.zero,
                    constraints: const BoxConstraints(),
                    onPressed: () => vm.dismissAlert(),
                  ),
                ],
              ),
            ),
          ],

          // Active Tab Body
          Expanded(child: _tabs[_currentIndex]),
        ],
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _currentIndex,
        onTap: (index) {
          setState(() {
            _currentIndex = index;
          });
        },
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.dashboard_outlined),
            activeIcon: Icon(Icons.dashboard),
            label: 'แดชบอร์ด',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.power_settings_new),
            activeIcon: Icon(Icons.power),
            label: 'ควบคุม',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.tune),
            activeIcon: Icon(Icons.tune),
            label: 'กฎอัตโนมัติ',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.cell_tower),
            activeIcon: Icon(Icons.cell_tower),
            label: 'ESP-NOW',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.insights),
            activeIcon: Icon(Icons.insights),
            label: 'วิเคราะห์',
          ),
        ],
      ),
    );
  }

  void _showTeamPicker(BuildContext context, FarmViewModel vm) {
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('เลือกหมายเลขกลุ่ม'),
        content: SizedBox(
          width: double.maxFinite,
          child: Wrap(
            spacing: 8,
            runSpacing: 8,
            children: List.generate(12, (index) {
              final team = index + 1;
              final isSelected = team == vm.teamNumber;
              return ChoiceChip(
                label: Text('กลุ่ม $team'),
                selected: isSelected,
                selectedColor: const Color(0xFF10B981),
                onSelected: (selected) {
                  if (selected) {
                    vm.setTeamNumber(team);
                    Navigator.of(ctx).pop();
                  }
                },
              );
            }),
          ),
        ),
      ),
    );
  }
}
