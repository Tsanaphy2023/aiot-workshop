import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';

class EspNowTab extends StatelessWidget {
  const EspNowTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final esp = vm.espNow;
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Bridge Status Banner
          Card(
            color: esp.isLinkConnected
                ? const Color(0xFF10B981).withValues(alpha: 0.15)
                : Colors.red.withValues(alpha: 0.15),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Icon(
                    esp.isLinkConnected ? Icons.cell_tower : Icons.signal_wifi_off,
                    color: esp.isLinkConnected ? const Color(0xFF10B981) : Colors.red,
                    size: 32,
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          esp.isLinkConnected
                              ? 'ESP-NOW Bridge ทำงานปกติ (Connected)'
                              : 'ขาดการติดต่อจากแปลง (Disconnected)',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: esp.isLinkConnected ? const Color(0xFF10B981) : Colors.red,
                          ),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          esp.isLinkConnected
                              ? 'ส่งต่อข้อมูลจากแปลง 150m เข้าสู่ระบบ Home Assistant'
                              : 'ไม่ได้รับข้อมูลเกินกำหนด เซนเซอร์เข้าสู่สถานะ Fail-Safe',
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Radio Network Hardware Config
          Text('ข้อมูลโครงข่ายวิทยุ (Wireless Config)',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  _buildDataRow('บอร์ดแปลงต้นทาง (Sender):', esp.senderNode),
                  const Divider(height: 16),
                  _buildDataRow('บอร์ดตัวรับที่บ้าน (Receiver):', esp.receiverNode),
                  const Divider(height: 16),
                  _buildDataRow('ช่องสัญญาณวิทยุ (Wi-Fi Channel):', 'CH ${esp.channel} (2.437 GHz)'),
                  const Divider(height: 16),
                  _buildDataRow(
                    'ความแรงสัญญาณ (RSSI):',
                    '${esp.rssi} dBm (${_getSignalQuality(esp.rssi)})',
                    valueColor: _getSignalColor(esp.rssi),
                  ),
                  const SizedBox(height: 8),
                  ClipRRect(
                    borderRadius: BorderRadius.circular(4),
                    child: LinearProgressIndicator(
                      value: ((esp.rssi + 100) / 70.0).clamp(0.0, 1.0),
                      minHeight: 6,
                      backgroundColor: Colors.grey.withValues(alpha: 0.2),
                      valueColor: AlwaysStoppedAnimation<Color>(_getSignalColor(esp.rssi)),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Activity 11.2: Dual-Path Comparison Table
          Text('เปรียบเทียบข้อมูลสองทาง (Direct Wi-Fi vs ESP-NOW)',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Table(
                columnWidths: const {
                  0: FlexColumnWidth(2),
                  1: FlexColumnWidth(2),
                  2: FlexColumnWidth(2),
                },
                children: [
                  TableRow(
                    decoration: BoxDecoration(
                      border: Border(bottom: BorderSide(color: Colors.grey.withValues(alpha: 0.2))),
                    ),
                    children: const [
                      Padding(
                        padding: EdgeInsets.only(bottom: 8),
                        child: Text('ค่าเซนเซอร์', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      Padding(
                        padding: EdgeInsets.only(bottom: 8),
                        child: Text('โดยตรง (Wi-Fi)', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                      Padding(
                        padding: EdgeInsets.only(bottom: 8),
                        child: Text('ผ่าน ESP-NOW', style: TextStyle(fontWeight: FontWeight.bold)),
                      ),
                    ],
                  ),
                  TableRow(
                    children: [
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        child: Text('ความชื้นอากาศ'),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Text('${esp.humDirect.toStringAsFixed(1)} %'),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Text(
                          '${esp.humEspNow.toStringAsFixed(1)} %',
                          style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                  TableRow(
                    children: [
                      const Padding(
                        padding: EdgeInsets.symmetric(vertical: 8),
                        child: Text('ความสว่าง'),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Text('${esp.lightDirect.toStringAsFixed(0)} Lux'),
                      ),
                      Padding(
                        padding: const EdgeInsets.symmetric(vertical: 8),
                        child: Text(
                          '${esp.lightEspNow.toStringAsFixed(0)} Lux',
                          style: const TextStyle(color: Color(0xFF10B981), fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Packet Statistics & Quality of Service (QoS)
          Text('สถิติแพ็กเก็ต (Packet Quality of Service)',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: _buildMetricTile(
                  'แพ็กเก็ตที่ได้รับ',
                  '${esp.packetCount}',
                  Icons.mark_email_read,
                  const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildMetricTile(
                  'แพ็กเก็ตที่หาย',
                  '${esp.packetLost}',
                  Icons.mark_email_unread,
                  Colors.orange,
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: _buildMetricTile(
                  'อัตราสำเร็จ',
                  '${esp.packetDeliveryRate.toStringAsFixed(1)}%',
                  Icons.verified,
                  const Color(0xFF06B6D4),
                ),
              ),
            ],
          ),
          const SizedBox(height: 20),

          // Activity 11.4 Watchdog Test Button
          Card(
            color: Colors.red.withValues(alpha: 0.08),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'ทดสอบระบบเตือนเมื่อแปลงเงียบ (Watchdog Failure Test)',
                    style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                  ),
                  const SizedBox(height: 4),
                  const Text(
                    'จำลองการปิดสวิตช์บอร์ดที่แปลง เพื่อทดสอบว่าตัวรับและแอปตรวจจับการขาดหายได้ภายใน 15-30 วินาทีหรือไม่',
                    style: TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                  const SizedBox(height: 12),
                  SizedBox(
                    width: double.infinity,
                    child: OutlinedButton.icon(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: esp.isLinkConnected ? Colors.red : const Color(0xFF10B981),
                        side: BorderSide(
                          color: esp.isLinkConnected ? Colors.red : const Color(0xFF10B981),
                        ),
                      ),
                      icon: Icon(esp.isLinkConnected ? Icons.power_settings_new : Icons.refresh),
                      label: Text(
                        esp.isLinkConnected
                            ? 'จำลองปิดบอร์ดแปลง (Simulate Power Off)'
                            : 'กู้คืนสัญญาณ (Restore Link)',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      onPressed: () => vm.simulateEspNowLinkToggle(),
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildDataRow(String label, String value, {Color? valueColor}) {
    return Row(
      children: [
        Expanded(
          child: Text(label, style: const TextStyle(color: Colors.grey, fontSize: 13)),
        ),
        const SizedBox(width: 8),
        Text(
          value,
          textAlign: TextAlign.end,
          style: TextStyle(
            fontWeight: FontWeight.bold,
            fontSize: 13,
            color: valueColor,
          ),
        ),
      ],
    );
  }

  Widget _buildMetricTile(String label, String value, IconData icon, Color color) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 12, horizontal: 8),
        child: Column(
          children: [
            Icon(icon, color: color, size: 20),
            const SizedBox(height: 6),
            Text(
              value,
              style: TextStyle(
                fontWeight: FontWeight.bold,
                fontSize: 16,
                color: color,
              ),
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: const TextStyle(fontSize: 10, color: Colors.grey),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  String _getSignalQuality(int rssi) {
    if (rssi >= -50) return 'แรงมาก';
    if (rssi >= -65) return 'ดี';
    if (rssi >= -75) return 'ปานกลาง';
    return 'อ่อน';
  }

  Color _getSignalColor(int rssi) {
    if (rssi >= -50) return const Color(0xFF10B981);
    if (rssi >= -65) return const Color(0xFF06B6D4);
    if (rssi >= -75) return Colors.orange;
    return Colors.red;
  }
}
