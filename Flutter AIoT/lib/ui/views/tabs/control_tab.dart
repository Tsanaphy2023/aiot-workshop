import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';
import '../../core/widgets/actuator_card.dart';

class ControlTab extends StatelessWidget {
  const ControlTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final act = vm.actuators;
    final s = vm.sensors;

    final isPumpLocked = act.isEmergencyStopped || (s.isWaterLow && vm.automation.dryRunProtectionEnabled);
    final String? pumpLockReason = act.isEmergencyStopped
        ? 'ปั๊มถูกระงับ: สถานะหยุดฉุกเฉิน (E-Stop Active)'
        : (s.isWaterLow && vm.automation.dryRunProtectionEnabled
            ? 'ปั๊มถูกระงับ: ตรวจพบระดับน้ำต่ำ ป้องกันปั๊มทำงานแห้ง (Dry-Run Lock)'
            : null);

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Auto / Manual Mode Selector Card
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: act.isAutoMode
                          ? const Color(0xFF10B981).withValues(alpha: 0.2)
                          : Colors.orange.withValues(alpha: 0.2),
                      shape: BoxShape.circle,
                    ),
                    child: Icon(
                      act.isAutoMode ? Icons.auto_mode : Icons.touch_app,
                      color: act.isAutoMode ? const Color(0xFF10B981) : Colors.orange,
                      size: 24,
                    ),
                  ),
                  const SizedBox(width: 14),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          act.isAutoMode ? 'โหมดอัตโนมัติ (Autonomous)' : 'โหมดควบคุมด้วยตนเอง (Manual)',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
                        ),
                        Text(
                          act.isAutoMode
                              ? 'ควบคุมตามความชื้นดินและตัวจับเวลา Fail-safe'
                              : 'ผู้ใช้สั่งการเปิด/ปิดผ่านแอปพลิเคชันโดยตรง',
                          style: const TextStyle(fontSize: 12, color: Colors.grey),
                        ),
                      ],
                    ),
                  ),
                  Switch.adaptive(
                    value: act.isAutoMode,
                    activeThumbColor: const Color(0xFF10B981),
                    onChanged: (val) => vm.toggleAutoMode(val),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          Text(
            'ควบคุมรีเลย์ (Actuators)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),

          // Relay 1: Irrigation Pump
          ActuatorCard(
            title: 'ปั๊มรดน้ำแปลงปลูก (Relay 1 - Irrigation Pump)',
            subtitle: act.isPumpOn ? 'กำลังรดน้ำแปลงปลูก' : 'ปั๊มน้ำปิดอยู่',
            icon: Icons.water,
            isOn: act.isPumpOn,
            isLocked: isPumpLocked,
            lockReason: pumpLockReason,
            remainingSeconds: act.isPumpOn ? act.pumpRemainingSeconds : null,
            activeColor: const Color(0xFF06B6D4),
            onToggle: (val) => vm.togglePump(val),
          ),
          const SizedBox(height: 12),

          // Relay 2: Grow Light
          ActuatorCard(
            title: 'หลอดไฟปลูกพืช (Relay 2 - Grow Lights)',
            subtitle: act.isGrowLightOn ? 'เปิดไฟเพิ่มแสงสังเคราะห์' : 'หลอดไฟปิดอยู่',
            icon: Icons.lightbulb,
            isOn: act.isGrowLightOn,
            isLocked: act.isEmergencyStopped,
            lockReason: act.isEmergencyStopped ? 'หยุดฉุกเฉิน (E-Stop Active)' : null,
            activeColor: const Color(0xFFEAB308),
            onToggle: (val) => vm.toggleGrowLight(val),
          ),
          const SizedBox(height: 20),

          // Failure Lab Simulation Controls
          Text(
            'ห้องทดลองจำลองปัญหา (Failure Lab Diagnostics)',
            style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 8),
          Card(
            child: Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                children: [
                  ListTile(
                    contentPadding: EdgeInsets.zero,
                    leading: Icon(
                      s.isWaterLow ? Icons.error : Icons.check_circle,
                      color: s.isWaterLow ? Colors.red : const Color(0xFF10B981),
                    ),
                    title: const Text('สวิตช์ลูกลอยตรวจจับระดับน้ำ (Float Switch)'),
                    subtitle: Text(
                      s.isWaterLow
                          ? 'สถานะ: น้ำแห้ง (Triggered) - ปั๊มถูกล็อคห้ามทำงาน'
                          : 'สถานะ: มีน้ำเพียงพอ (Normal)',
                      style: TextStyle(color: s.isWaterLow ? Colors.red : null),
                    ),
                    trailing: OutlinedButton(
                      style: OutlinedButton.styleFrom(
                        foregroundColor: s.isWaterLow ? const Color(0xFF10B981) : Colors.orange,
                      ),
                      onPressed: () => vm.simulateWaterFloatToggle(),
                      child: Text(s.isWaterLow ? 'เติมน้ำ (Reset)' : 'จำลองน้ำแห้ง'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 24),

          // Big Red Emergency Stop Button
          SizedBox(
            width: double.infinity,
            height: 54,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: act.isEmergencyStopped ? Colors.grey : const Color(0xFFDC2626),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: Icon(act.isEmergencyStopped ? Icons.restart_alt : Icons.emergency, size: 24),
              label: Text(
                act.isEmergencyStopped ? 'ปลดล็อคระบบหยุดฉุกเฉิน (RESET E-STOP)' : 'หยุดฉุกเฉินทันที (EMERGENCY STOP)',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
              ),
              onPressed: () {
                if (act.isEmergencyStopped) {
                  vm.resetEmergencyStop();
                } else {
                  vm.triggerEmergencyStop();
                }
              },
            ),
          ),
        ],
      ),
    );
  }
}
