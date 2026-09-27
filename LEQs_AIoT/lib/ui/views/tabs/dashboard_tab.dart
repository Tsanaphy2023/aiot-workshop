import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';
import '../../core/widgets/sensor_gauge_card.dart';
import '../../core/widgets/sparkline_chart.dart';
import '../../core/widgets/ai_insights_card.dart';

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
              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 10),
              child: Row(
                children: [
                  _buildStatusChip(
                    context,
                    label: 'กลุ่ม ${vm.teamNumber}',
                    icon: Icons.groups_outlined,
                    color: Colors.blueAccent,
                  ),
                  const SizedBox(width: 6),
                  _buildStatusChip(
                    context,
                    label: esp.isLinkConnected ? 'ESP-NOW' : 'ออฟไลน์',
                    icon: esp.isLinkConnected ? Icons.wifi : Icons.wifi_off,
                    color: esp.isLinkConnected ? const Color(0xFF10B981) : Colors.red,
                  ),
                  const SizedBox(width: 6),
                  _buildStatusChip(
                    context,
                    label: s.isWaterLow ? 'น้ำแห้ง' : 'น้ำปกติ',
                    icon: s.isWaterLow ? Icons.warning_amber_rounded : Icons.water_drop,
                    color: s.isWaterLow ? Colors.red : const Color(0xFF06B6D4),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 14),

          // Agriphysics & Explainable AI (xAI) Insights Card
          AiInsightsCard(viewModel: vm),
          const SizedBox(height: 14),

          // Primary Soil Moisture Card (Large Highlight)
          SensorGaugeCard(
            title: 'ความชื้นในดิน',
            value: s.soilMoisture.toStringAsFixed(1),
            unit: '%',
            icon: Icons.grass,
            accentColor: const Color(0xFF10B981),
            statusText: s.soilMoisture < vm.automation.soilMoistureLowThreshold
                ? 'ดินแห้ง'
                : (s.soilMoisture > vm.automation.soilMoistureHighThreshold
                    ? 'ดินชุ่มชื้นสูง'
                    : 'เหมาะสม'),
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
                  title: 'อุณหภูมิอากาศ',
                  value: s.temperature.toStringAsFixed(1),
                  unit: '°C',
                  icon: Icons.thermostat,
                  accentColor: const Color(0xFFF59E0B),
                  statusText: s.temperature > 35.0 ? 'อากาศร้อน' : 'ปกติ',
                  statusColor: s.temperature > 35.0 ? Colors.red : const Color(0xFF10B981),
                ),
              ),
              const SizedBox(width: 10),
              Expanded(
                child: SensorGaugeCard(
                  title: 'ความชื้นสัมพัทธ์',
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
            title: 'ความเข้มแสงแดด',
            value: s.lightLux.toStringAsFixed(0),
            unit: 'Lux',
            icon: Icons.wb_sunny_outlined,
            accentColor: const Color(0xFFEAB308),
            statusText: s.lightLux > 1000 ? 'แดดจ้า' : (s.lightLux > 200 ? 'แสงปานกลาง' : 'แสงน้อย'),
            progressPercent: (s.lightLux / 2000.0).clamp(0.0, 1.0),
          ),
          const SizedBox(height: 14),

          // Soil Moisture Sparkline Trend
          SparklineChart(
            data: vm.history.map((h) => h.soilMoisture).toList(),
            lineColor: const Color(0xFF10B981),
            title: 'แนวโน้มความชื้นดิน',
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
        padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
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
