import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/app_theme.dart';
import '../../view_models/farm_view_model.dart';

class ConnectionSettingsDialog extends StatefulWidget {
  const ConnectionSettingsDialog({super.key});

  static Future<void> show(BuildContext context) {
    return showDialog(
      context: context,
      barrierDismissible: true,
      builder: (ctx) => const ConnectionSettingsDialog(),
    );
  }

  @override
  State<ConnectionSettingsDialog> createState() => _ConnectionSettingsDialogState();
}

class _ConnectionSettingsDialogState extends State<ConnectionSettingsDialog>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final TextEditingController _ipController = TextEditingController();
  bool _isTestingPing = false;
  String? _pingResult;
  bool _pingSuccess = false;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    final vm = context.read<FarmViewModel>();
    if (vm.connectedBoardIp != null) {
      _ipController.text = vm.connectedBoardIp!;
    } else {
      _ipController.text = '192.168.4.1';
    }

    // Auto-scan on open if not already scanned
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (vm.discoveredBoards.isEmpty && !vm.isScanning) {
        vm.scanForBoards();
      }
    });
  }

  @override
  void dispose() {
    _tabController.dispose();
    _ipController.dispose();
    super.dispose();
  }

  Future<void> _handleTestPing(FarmViewModel vm) async {
    final ip = _ipController.text.trim();
    if (ip.isEmpty) return;

    setState(() {
      _isTestingPing = true;
      _pingResult = null;
    });

    try {
      final res = await vm.connectToManualIp(ip);
      setState(() {
        _isTestingPing = false;
        _pingSuccess = res;
        _pingResult = res
            ? 'เชื่อมต่อบอร์ด $ip สำเร็จ!'
            : 'ไม่สามารถติดต่อบอร์ดที่ $ip ได้ (ตรวจสอบการเชื่อมต่อ Wi-Fi)';
      });
    } catch (e) {
      setState(() {
        _isTestingPing = false;
        _pingSuccess = false;
        _pingResult = 'ข้อผิดพลาด: $e';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final isConnected = vm.isDirectBoard && vm.connectedBoardIp != null;

    return Dialog(
      backgroundColor: AppTheme.bgDark,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(20),
        side: const BorderSide(color: AppTheme.cardDarkBorder, width: 1.5),
      ),
      insetPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      child: ConstrainedBox(
        constraints: const BoxConstraints(maxWidth: 500, maxHeight: 680),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.fromLTRB(20, 20, 16, 12),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.accentMint.withValues(alpha: 0.15),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: const Icon(
                      Icons.wifi_tethering,
                      color: AppTheme.accentMint,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 14),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'เชื่อมต่อบอร์ดฮาร์ดแวร์ IoT',
                          style: TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.textPrimaryDark,
                          ),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'GoGo-IoT / LEQs IoT xAI Direct Wi-Fi',
                          style: TextStyle(
                            fontSize: 12,
                            color: AppTheme.textSecondaryDark,
                          ),
                        ),
                      ],
                    ),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close, color: AppTheme.textSecondaryDark),
                    onPressed: () => Navigator.of(context).pop(),
                  ),
                ],
              ),
            ),

            // Active Connection Status Banner
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 20),
              child: Container(
                padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                decoration: BoxDecoration(
                  color: isConnected
                      ? AppTheme.primaryLight.withValues(alpha: 0.2)
                      : Colors.white.withValues(alpha: 0.04),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(
                    color: isConnected ? AppTheme.accentMint : AppTheme.cardDarkBorder,
                  ),
                ),
                child: Row(
                  children: [
                    Icon(
                      isConnected ? Icons.check_circle : Icons.sensors_off,
                      color: isConnected ? AppTheme.accentMint : AppTheme.textSecondaryDark,
                      size: 20,
                    ),
                    const SizedBox(width: 10),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            isConnected
                                ? 'กำลังต่อบอร์ดจริง: ${vm.connectedBoardName ?? 'LEQs Node'}'
                                : 'โหมดจำลอง (Farm Simulator)',
                            style: TextStyle(
                              fontSize: 13,
                              fontWeight: FontWeight.bold,
                              color: isConnected ? AppTheme.accentMint : AppTheme.textPrimaryDark,
                            ),
                          ),
                          if (isConnected)
                            Text(
                              'IP: ${vm.connectedBoardIp}',
                              style: const TextStyle(
                                fontSize: 11,
                                color: AppTheme.textSecondaryDark,
                              ),
                            ),
                        ],
                      ),
                    ),
                    if (isConnected)
                      TextButton(
                        onPressed: () {
                          vm.disconnectToSimulator();
                          setState(() {
                            _pingResult = 'กลับสู่โหมด Simulator แล้ว';
                            _pingSuccess = true;
                          });
                        },
                        style: TextButton.styleFrom(
                          foregroundColor: AppTheme.alertRed,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          minimumSize: Size.zero,
                          tapTargetSize: MaterialTapTargetSize.shrinkWrap,
                        ),
                        child: const Text('ตัดการเชื่อมต่อ', style: TextStyle(fontSize: 12)),
                      ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Tabs
            TabBar(
              controller: _tabController,
              indicatorColor: AppTheme.accentMint,
              labelColor: AppTheme.accentMint,
              unselectedLabelColor: AppTheme.textSecondaryDark,
              tabs: const [
                Tab(
                  icon: Icon(Icons.radar, size: 18),
                  text: 'สแกนอัตโนมัติ (Auto-Scan)',
                ),
                Tab(
                  icon: Icon(Icons.edit_note, size: 18),
                  text: 'กำหนดเอง (Manual IP)',
                ),
              ],
            ),

            // Tab Views
            Expanded(
              child: TabBarView(
                controller: _tabController,
                children: [
                  _buildAutoScanTab(context, vm),
                  _buildManualIpTab(context, vm),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildAutoScanTab(BuildContext context, FarmViewModel vm) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Action Bar: Scan button + Status
          Row(
            children: [
              Expanded(
                child: Text(
                  vm.scanStatusMessage.isEmpty
                      ? 'กดปุ่มเพื่อเริ่มค้นหาบอร์ดในเครือข่าย Wi-Fi'
                      : vm.scanStatusMessage,
                  style: const TextStyle(
                    fontSize: 12,
                    color: AppTheme.textSecondaryDark,
                  ),
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
              ),
              const SizedBox(width: 8),
              ElevatedButton.icon(
                onPressed: vm.isScanning ? null : () => vm.scanForBoards(),
                style: ElevatedButton.styleFrom(
                  backgroundColor: AppTheme.primaryLight,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                ),
                icon: vm.isScanning
                    ? const SizedBox(
                        width: 14,
                        height: 14,
                        child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                      )
                    : const Icon(Icons.refresh, size: 16),
                label: Text(vm.isScanning ? 'กำลังสแกน...' : 'สแกนใหม่'),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Discovered Boards List
          Expanded(
            child: vm.discoveredBoards.isEmpty
                ? Center(
                    child: SingleChildScrollView(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            vm.isScanning ? Icons.radar : Icons.wifi_find,
                            size: 48,
                            color: AppTheme.textSecondaryDark.withValues(alpha: 0.5),
                          ),
                          const SizedBox(height: 12),
                          Text(
                            vm.isScanning
                                ? 'กำลังฟัง UDP Broadcast บนพอร์ต 8266...'
                                : 'ยังไม่พบบอร์ด GoGo-IoT / LEQs IoT',
                            style: const TextStyle(
                              color: AppTheme.textSecondaryDark,
                              fontSize: 13,
                            ),
                          ),
                          const SizedBox(height: 8),
                          const Text(
                            'ตรวจสอบว่าบอร์ดเปิดสวิตช์แล้ว และมือถือเชื่อมต่อ Wi-Fi หรือ Hotspot เดียวกัน',
                            textAlign: TextAlign.center,
                            style: TextStyle(
                              color: AppTheme.textSecondaryDark,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ),
                  )
                : ListView.separated(
                    itemCount: vm.discoveredBoards.length,
                    separatorBuilder: (c, i) => const SizedBox(height: 8),
                    itemBuilder: (ctx, index) {
                      final board = vm.discoveredBoards[index];
                      final isCurrent = vm.connectedBoardIp == board.ip;

                      return Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: isCurrent
                              ? AppTheme.accentMint.withValues(alpha: 0.12)
                              : AppTheme.cardDark,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(
                            color: isCurrent ? AppTheme.accentMint : AppTheme.cardDarkBorder,
                            width: isCurrent ? 1.5 : 1,
                          ),
                        ),
                        child: Row(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(8),
                              decoration: BoxDecoration(
                                color: AppTheme.accentMint.withValues(alpha: 0.15),
                                shape: BoxShape.circle,
                              ),
                              child: const Icon(
                                Icons.developer_board,
                                color: AppTheme.accentMint,
                                size: 22,
                              ),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Row(
                                    children: [
                                      Flexible(
                                        child: Text(
                                          board.deviceName,
                                          style: const TextStyle(
                                            fontWeight: FontWeight.bold,
                                            fontSize: 14,
                                            color: AppTheme.textPrimaryDark,
                                          ),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      if (board.teamNumber > 0) ...[
                                        const SizedBox(width: 6),
                                        Container(
                                          padding: const EdgeInsets.symmetric(
                                              horizontal: 6, vertical: 2),
                                          decoration: BoxDecoration(
                                            color: AppTheme.warmAmber.withValues(alpha: 0.2),
                                            borderRadius: BorderRadius.circular(6),
                                          ),
                                          child: Text(
                                            'ทีม ${board.teamNumber}',
                                            style: const TextStyle(
                                              fontSize: 10,
                                              fontWeight: FontWeight.bold,
                                              color: AppTheme.warmAmber,
                                            ),
                                          ),
                                        ),
                                      ],
                                    ],
                                  ),
                                  const SizedBox(height: 3),
                                  Text(
                                    'IP: ${board.ip}  •  RSSI: ${board.rssi} dBm (${board.signalQuality})',
                                    style: const TextStyle(
                                      fontSize: 12,
                                      color: AppTheme.textSecondaryDark,
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(width: 8),
                            ElevatedButton(
                              onPressed: isCurrent
                                  ? null
                                  : () async {
                                      final ok = await vm.connectToBoard(board);
                                      if (ok && context.mounted) {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          SnackBar(
                                            content: Text('เชื่อมต่อบอร์ด ${board.deviceName} สำเร็จ!'),
                                            backgroundColor: AppTheme.primaryLight,
                                          ),
                                        );
                                        Navigator.of(context).pop();
                                      }
                                    },
                              style: ElevatedButton.styleFrom(
                                backgroundColor: isCurrent
                                    ? Colors.grey.shade700
                                    : AppTheme.accentMint,
                                foregroundColor: Colors.black,
                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                              ),
                              child: Text(
                                isCurrent ? 'กำลังต่อ' : 'เชื่อมต่อ',
                                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 12),
                              ),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
          ),
        ],
      ),
    );
  }

  Widget _buildManualIpTab(BuildContext context, FarmViewModel vm) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const Text(
            'กรอก IP Address ของบอร์ด',
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.bold,
              color: AppTheme.textPrimaryDark,
            ),
          ),
          const SizedBox(height: 6),
          const Text(
            'ใช้ในกรณีที่เครือข่าย Wi-Fi มีการบล็อก UDP Broadcast หรือเชื่อมต่อตรงผ่าน AP Hotspot ของบอร์ด',
            style: TextStyle(fontSize: 12, color: AppTheme.textSecondaryDark),
          ),
          const SizedBox(height: 12),

          // IP input
          TextField(
            controller: _ipController,
            keyboardType: TextInputType.text,
            style: const TextStyle(color: AppTheme.textPrimaryDark, fontFamily: 'monospace'),
            decoration: InputDecoration(
              labelText: 'IP Address บอร์ด GoGo / LEQs',
              hintText: '192.168.4.1 หรือ 192.168.1.xxx',
              prefixIcon: const Icon(Icons.computer, color: AppTheme.accentMint),
              filled: true,
              fillColor: AppTheme.cardDark,
              border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.cardDarkBorder),
              ),
              enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.cardDarkBorder),
              ),
              focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(12),
                borderSide: const BorderSide(color: AppTheme.accentMint, width: 2),
              ),
            ),
          ),

          const SizedBox(height: 10),

          // Quick Presets
          Wrap(
            spacing: 8,
            children: [
              ActionChip(
                label: const Text('192.168.4.1 (ESP32 AP Hotspot)'),
                backgroundColor: AppTheme.cardDark,
                side: const BorderSide(color: AppTheme.cardDarkBorder),
                labelStyle: const TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                onPressed: () {
                  _ipController.text = '192.168.4.1';
                },
              ),
              ActionChip(
                label: const Text('192.168.1.100'),
                backgroundColor: AppTheme.cardDark,
                side: const BorderSide(color: AppTheme.cardDarkBorder),
                labelStyle: const TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                onPressed: () {
                  _ipController.text = '192.168.1.100';
                },
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Test Ping result banner
          if (_pingResult != null)
            Container(
              padding: const EdgeInsets.all(12),
              margin: const EdgeInsets.only(bottom: 16),
              decoration: BoxDecoration(
                color: _pingSuccess
                    ? AppTheme.primaryLight.withValues(alpha: 0.2)
                    : AppTheme.alertRed.withValues(alpha: 0.2),
                borderRadius: BorderRadius.circular(10),
                border: Border.all(
                  color: _pingSuccess ? AppTheme.accentMint : AppTheme.alertRed,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    _pingSuccess ? Icons.check_circle : Icons.error_outline,
                    color: _pingSuccess ? AppTheme.accentMint : AppTheme.alertRed,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  Expanded(
                    child: Text(
                      _pingResult!,
                      style: TextStyle(
                        fontSize: 12,
                        color: _pingSuccess ? AppTheme.accentMint : AppTheme.alertRed,
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                  ),
                ],
              ),
            ),

          // Actions: Ping and Connect
          Row(
            children: [
              Expanded(
                child: OutlinedButton.icon(
                  onPressed: _isTestingPing ? null : () => _handleTestPing(vm),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppTheme.accentMint),
                    foregroundColor: AppTheme.accentMint,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  icon: _isTestingPing
                      ? const SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2, color: AppTheme.accentMint),
                        )
                      : const Icon(Icons.network_ping, size: 18),
                  label: const Text('ทดสอบ (Ping)'),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: ElevatedButton.icon(
                  onPressed: () async {
                    final ip = _ipController.text.trim();
                    if (ip.isEmpty) return;

                    final ok = await vm.connectToManualIp(ip);
                    if (ok && context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text('เชื่อมต่อบอร์ดที่ $ip สำเร็จ!'),
                          backgroundColor: AppTheme.primaryLight,
                        ),
                      );
                      Navigator.of(context).pop();
                    } else {
                      setState(() {
                        _pingSuccess = false;
                        _pingResult = 'ไม่สามารถเชื่อมต่อ $ip ได้ กรุณาตรวจสอบ IP';
                      });
                    }
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentMint,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  icon: const Icon(Icons.link, size: 18),
                  label: const Text('บันทึกและเชื่อมต่อ', style: TextStyle(fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
