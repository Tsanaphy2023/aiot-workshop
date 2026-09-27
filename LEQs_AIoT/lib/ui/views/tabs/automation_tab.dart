import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';
import '../../core/widgets/predictive_moisture_card.dart';

class AutomationTab extends StatelessWidget {
  const AutomationTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final auto = vm.automation;
    final theme = Theme.of(context);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header Card
          Card(
            color: const Color(0xFF0F5132).withValues(alpha: 0.15),
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  const Icon(Icons.psychology, color: Color(0xFF10B981), size: 32),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: const [
                        Text(
                          'ระบบตั้งกฎอัตโนมัติ (Think & Fail-Safe)',
                          style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        SizedBox(height: 2),
                        Text(
                          'ปรับแต่งเกณฑ์ควบคุมความชื้นดินและตัวตัดการทำงานฉุกเฉิน',
                          style: TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),

          // 6-Hour Time-Series Predictive Moisture Card
          PredictiveMoistureCard(
            predictions: vm.soilPredictions,
            currentMoisture: vm.sensors.soilMoisture,
            wiltingThreshold: auto.soilMoistureLowThreshold,
          ),
          const SizedBox(height: 16),

          Text('เกณฑ์การรดน้ำอัตโนมัติ (Soil Moisture Thresholds)',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),

          // Low Threshold Slider
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Expanded(child: Text('เกณฑ์เริ่มรดน้ำ (เมื่อความชื้นต่ำกว่า)')),
                      const SizedBox(width: 8),
                      Text(
                        '${auto.soilMoistureLowThreshold.toStringAsFixed(0)} %',
                        style: const TextStyle(
                          color: Color(0xFF10B981),
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: auto.soilMoistureLowThreshold,
                    min: 15.0,
                    max: 60.0,
                    divisions: 45,
                    activeColor: const Color(0xFF10B981),
                    onChanged: (val) {
                      vm.updateThresholds(lowThreshold: val);
                    },
                  ),
                  const Text(
                    'เมื่อเซนเซอร์อ่านค่าได้ต่ำกว่าเกณฑ์นี้ และระดับน้ำปกติ ระบบจะสั่งเปิดปั๊มทันที',
                    style: TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // High Threshold Slider
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Expanded(child: Text('เกณฑ์หยุดรดน้ำ (เมื่อความชื้นถึง)')),
                      const SizedBox(width: 8),
                      Text(
                        '${auto.soilMoistureHighThreshold.toStringAsFixed(0)} %',
                        style: const TextStyle(
                          color: Color(0xFF06B6D4),
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: auto.soilMoistureHighThreshold,
                    min: 50.0,
                    max: 90.0,
                    divisions: 40,
                    activeColor: const Color(0xFF06B6D4),
                    onChanged: (val) {
                      vm.updateThresholds(highThreshold: val);
                    },
                  ),
                  const Text(
                    'เมื่อดินได้รับน้ำจนความชื้นเพิ่มขึ้นถึงเกณฑ์นี้ ปั๊มจะสั่งปิดอัตโนมัติ',
                    style: TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          Text('การป้องกันความเสียหาย (Fail-Safe Watchdogs)',
              style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold)),
          const SizedBox(height: 8),

          // Max Run Time
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Expanded(child: Text('เวลาทำงานสูงสุดของปั๊ม (Max Runtime)')),
                      const SizedBox(width: 8),
                      Text(
                        '${auto.maxPumpRunSeconds}s',
                        style: const TextStyle(
                          color: Colors.orange,
                          fontWeight: FontWeight.bold,
                          fontSize: 16,
                        ),
                      ),
                    ],
                  ),
                  Slider(
                    value: auto.maxPumpRunSeconds.toDouble(),
                    min: 30.0,
                    max: 300.0,
                    divisions: 27,
                    activeColor: Colors.orange,
                    onChanged: (val) {
                      vm.updateThresholds(maxRunSeconds: val.toInt());
                    },
                  ),
                  const Text(
                    'ป้องกันน้ำล้นแปลงและปั๊มร้อนจัด หากปั๊มทำงานติดต่อกันครบกำหนดจะตัดการทำงานทันที',
                    style: TextStyle(fontSize: 11, color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 12),

          // Dry-Run Protection Switch
          Card(
            child: SwitchListTile.adaptive(
              title: const Text('ระบบป้องกันปั๊มทำงานแห้ง (Dry-Run Protection)'),
              subtitle: const Text('ตัดการทำงานปั๊มทันทีเมื่อสวิตช์ลูกลอยตรวจพบว่าน้ำในถังพักหมด'),
              value: auto.dryRunProtectionEnabled,
              activeThumbColor: const Color(0xFF10B981),
              onChanged: (val) {
                vm.updateThresholds(dryRunEnabled: val);
              },
            ),
          ),
        ],
      ),
    );
  }
}
