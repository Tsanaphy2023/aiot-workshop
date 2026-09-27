import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';
import '../../core/widgets/sensor_gauge_card.dart';
import '../../core/widgets/sparkline_chart.dart';

class DashboardTab extends StatelessWidget {
  const DashboardTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final s = vm.sensors;
    final esp = vm.espNow;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // System Health & Badges Strip
          Card(
            color: Theme.of(context).cardTheme.color,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              child: Row(
                children: [
                  _buildStatusChip(
                    context,
                    label: 'กลุ่มที่ ${vm.teamNumber}',
                    icon: Icons.groups_outlined,
                    color: Colors.blueAccent,
                  ),
                  const SizedBox(width: 8),
                  _buildStatusChip(
                    context,
                    label: esp.isLinkConnected ? 'ESP-NOW เชื่อมต่อ' : 'ขาดการติดต่อ',
                    icon: esp.isLinkConnected ? Icons.wifi : Icons.wifi_off,
                    color: esp.isLinkConnected ? const Color(0xFF10B981) : Colors.red,
                  ),
                  const SizedBox(width: 8),
                  _buildStatusChip(
                    context,
                    label: s.isWaterLow ? 'น้ำแห้ง!' : 'ระดับน้ำปกติ',
                    icon: s.isWaterLow ? Icons.warning_amber_rounded : Icons.water_drop,
                    color: s.isWaterLow ? Colors.red : const Color(0xFF06B6D4),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Primary Soil Moisture Card (Large Highlight)
          SensorGaugeCard(
            title: 'ความชื้นในดิน (Soil Moisture)',
            value: s.soilMoisture.toStringAsFixed(1),
            unit: '%',
            icon: Icons.grass,
            accentColor: const Color(0xFF10B981),
            statusText: s.soilMoisture < vm.automation.soilMoistureLowThreshold
                ? 'ดินแห้ง (ต้องการน้ำ)'
                : (s.soilMoisture > vm.automation.soilMoistureHighThreshold
                    ? 'ดินชุ่มชื้นสูง'
                    : 'ระดับเหมาะสม'),
            statusColor: s.soilMoisture < vm.automation.soilMoistureLowThreshold
                ? Colors.orange
                : const Color(0xFF10B981),
            progressPercent: s.soilMoisture / 100.0,
          ),
          const SizedBox(height: 12),

          // SHT30 & BH1750 Environmental Sensors Grid
          Row(
            children: [
              Expanded(
                child: SensorGaugeCard(
                  title: 'อุณหภูมิอากาศ (SHT30)',
                  value: s.temperature.toStringAsFixed(1),
                  unit: '°C',
                  icon: Icons.thermostat,
                  accentColor: const Color(0xFFF59E0B),
                  statusText: s.temperature > 35.0 ? 'อากาศร้อน' : 'ปกติ',
                  statusColor: s.temperature > 35.0 ? Colors.red : const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: SensorGaugeCard(
                  title: 'ความชื้นอากาศ (SHT30)',
                  value: s.humidity.toStringAsFixed(1),
                  unit: '%',
                  icon: Icons.cloud,
                  accentColor: const Color(0xFF06B6D4),
                  statusText: s.humidity < 50 ? 'แห้ง' : 'ชุ่มชื้น',
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),

          SensorGaugeCard(
            title: 'ความเข้มแสงแดด (BH1750)',
            value: s.lightLux.toStringAsFixed(0),
            unit: 'Lux',
            icon: Icons.wb_sunny_outlined,
            accentColor: const Color(0xFFEAB308),
            statusText: s.lightLux > 1000 ? 'แดดจ้า' : (s.lightLux > 200 ? 'แสงปานกลาง' : 'แสงน้อย'),
            progressPercent: (s.lightLux / 2000.0).clamp(0.0, 1.0),
          ),
          const SizedBox(height: 16),

          // Soil Moisture Sparkline Trend
          SparklineChart(
            data: vm.history.map((h) => h.soilMoisture).toList(),
            lineColor: const Color(0xFF10B981),
            title: 'แนวโน้มความชื้นดิน (Soil Moisture Trend)',
            unit: '%',
            height: 120,
          ),
        ],
      ),
    );
  }

  Widget _buildStatusChip(
    BuildContext context, {
    required String label,
    required IconData icon,
    required Color color,
  }) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 8),
        decoration: BoxDecoration(
          color: color.withValues(alpha: 0.12),
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: color.withValues(alpha: 0.25)),
        ),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(icon, size: 14, color: color),
            const SizedBox(width: 4),
            Flexible(
              child: Text(
                label,
                style: TextStyle(
                  color: color,
                  fontSize: 11,
                  fontWeight: FontWeight.bold,
                ),
                overflow: TextOverflow.ellipsis,
              ),
            ),
          ],
        ),
      ),
    );
  }
}
