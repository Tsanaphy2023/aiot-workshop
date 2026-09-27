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
            title: 'ปั๊มรดน้ำแปลงปลูก (Relay 1)',
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
            title: 'หลอดไฟปลูกพืช (Relay 2)',
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
              padding: const EdgeInsets.all(14.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Icon(
                        s.isWaterLow ? Icons.error : Icons.check_circle,
                        color: s.isWaterLow ? Colors.red : const Color(0xFF10B981),
                        size: 22,
                      ),
                      const SizedBox(width: 10),
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text(
                              'สวิตช์ลูกลอยตรวจจับระดับน้ำ',
                              style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                              overflow: TextOverflow.ellipsis,
                              maxLines: 1,
                            ),
                            Text(
                              s.isWaterLow
                                  ? 'น้ำแห้ง (Triggered) - ล็อคปั๊ม'
                                  : 'มีน้ำเพียงพอ (Normal)',
                              style: TextStyle(
                                fontSize: 12,
                                color: s.isWaterLow ? Colors.red : Colors.grey,
                              ),
                              overflow: TextOverflow.ellipsis,
                              maxLines: 1,
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(width: 8),
                      OutlinedButton(
                        style: OutlinedButton.styleFrom(
                          visualDensity: VisualDensity.compact,
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          foregroundColor: s.isWaterLow ? const Color(0xFF10B981) : Colors.orange,
                        ),
                        onPressed: () => vm.simulateWaterFloatToggle(),
                        child: Text(
                          s.isWaterLow ? 'เติมน้ำ' : 'จำลองแห้ง',
                          style: const TextStyle(fontSize: 12),
                        ),
                      ),
                    ],
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 20),

          // Big Red Emergency Stop Button
          SizedBox(
            width: double.infinity,
            height: 52,
            child: ElevatedButton.icon(
              style: ElevatedButton.styleFrom(
                backgroundColor: act.isEmergencyStopped ? Colors.grey : const Color(0xFFDC2626),
                foregroundColor: Colors.white,
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
              ),
              icon: Icon(act.isEmergencyStopped ? Icons.restart_alt : Icons.emergency, size: 22),
              label: Text(
                act.isEmergencyStopped ? 'ปลดล็อคหยุดฉุกเฉิน (RESET)' : 'หยุดฉุกเฉินทันที (EMERGENCY STOP)',
                style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
                overflow: TextOverflow.ellipsis,
                maxLines: 1,
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
