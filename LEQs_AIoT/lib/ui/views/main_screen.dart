import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../view_models/farm_view_model.dart';
import 'tabs/dashboard_tab.dart';
import 'tabs/control_tab.dart';
import 'tabs/automation_tab.dart';
import 'tabs/espnow_tab.dart';
import 'tabs/history_tab.dart';
import 'tabs/leaf_doctor_tab.dart';
import 'dialogs/connection_settings_dialog.dart';

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
    LeafDoctorTab(),
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
        titleSpacing: 8,
        title: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              padding: const EdgeInsets.all(5),
              decoration: BoxDecoration(
                color: const Color(0xFF10B981).withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(7),
              ),
              child: const Icon(Icons.eco, color: Color(0xFF10B981), size: 18),
            ),
            const SizedBox(width: 6),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'LEQs AIoT',
                    style: TextStyle(fontSize: 15, fontWeight: FontWeight.bold),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                  Text(
                    'ESP-NOW • GoGo-IoT',
                    style: TextStyle(fontSize: 9, color: Colors.grey.shade400),
                    overflow: TextOverflow.ellipsis,
                    maxLines: 1,
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          // Hardware Connection Indicator & Settings Button
          InkWell(
            borderRadius: BorderRadius.circular(8),
            onTap: () => ConnectionSettingsDialog.show(context),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 5),
              decoration: BoxDecoration(
                color: vm.isDirectBoard
                    ? const Color(0xFF10B981).withValues(alpha: 0.18)
                    : Colors.white.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: vm.isDirectBoard ? const Color(0xFF10B981) : Colors.white24,
                  width: 1,
                ),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Icon(
                    vm.isDirectBoard ? Icons.wifi : Icons.sensors_outlined,
                    size: 13,
                    color: vm.isDirectBoard ? const Color(0xFF10B981) : Colors.grey,
                  ),
                  const SizedBox(width: 4),
                  Text(
                    vm.isDirectBoard ? (vm.connectedBoardName ?? 'ต่อบอร์ด') : 'Sim',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: vm.isDirectBoard ? FontWeight.bold : FontWeight.normal,
                      color: vm.isDirectBoard ? const Color(0xFF10B981) : Colors.grey.shade300,
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 5),

          // Team Selector Button (Compact for smartphone)
          InkWell(
            borderRadius: BorderRadius.circular(8),
            onTap: () => _showTeamPicker(context, vm),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 5),
              decoration: BoxDecoration(
                color: Colors.white.withValues(alpha: 0.08),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.white24, width: 1),
              ),
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Icon(Icons.badge_outlined, size: 13, color: Colors.grey),
                  const SizedBox(width: 4),
                  Text(
                    'กลุ่ม ${vm.teamNumber}',
                    style: const TextStyle(fontSize: 11, color: Colors.white),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(width: 2),

          // Theme Toggle
          IconButton(
            visualDensity: VisualDensity.compact,
            icon: Icon(widget.isDarkMode ? Icons.light_mode : Icons.dark_mode, size: 18),
            tooltip: 'เปลี่ยนธีมสี',
            onPressed: widget.onToggleTheme,
          ),
          const SizedBox(width: 4),
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
        type: BottomNavigationBarType.fixed,
        selectedFontSize: 11,
        unselectedFontSize: 10,
        selectedItemColor: const Color(0xFF10B981),
        unselectedItemColor: Colors.grey.shade400,
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
            icon: Icon(Icons.document_scanner_outlined),
            activeIcon: Icon(Icons.document_scanner),
            label: 'หมอพืช AI',
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
