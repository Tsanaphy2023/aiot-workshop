import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../view_models/farm_view_model.dart';
import '../../core/widgets/sparkline_chart.dart';

class HistoryTab extends StatelessWidget {
  const HistoryTab({super.key});

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final history = vm.history;
    final theme = Theme.of(context);

    if (history.isEmpty) {
      return const Center(child: Text('กำลังรวบรวมข้อมูลโทรมาตรย้อนหลัง...'));
    }

    final soilList = history.map((h) => h.soilMoisture).toList();
    final tempList = history.map((h) => h.temperature).toList();
    final humList = history.map((h) => h.humidity).toList();
    final lightList = history.map((h) => h.lightLux).toList();

    final avgSoil = soilList.reduce((a, b) => a + b) / soilList.length;
    final avgTemp = tempList.reduce((a, b) => a + b) / tempList.length;
    final avgHum = humList.reduce((a, b) => a + b) / humList.length;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header with Export Button
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'ข้อมูลย้อนหลังและการวิเคราะห์',
                    style: theme.textTheme.titleMedium?.copyWith(fontWeight: FontWeight.bold),
                  ),
                  Text(
                    'บันทึกจุดตรวจวัดทั้งหมด ${history.length} จุด',
                    style: const TextStyle(fontSize: 12, color: Colors.grey),
                  ),
                ],
              ),
              FilledButton.tonalIcon(
                icon: const Icon(Icons.download, size: 16),
                label: const Text('ส่งออก JSON'),
                onPressed: () {
                  _showExportDialog(context, vm);
                },
              ),
            ],
          ),
          const SizedBox(height: 16),

          // Average Summary Banner
          Card(
            child: Padding(
              padding: const EdgeInsets.all(14.0),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _buildStatItem('ความชื้นดินเฉลี่ย', '${avgSoil.toStringAsFixed(1)}%', const Color(0xFF10B981)),
                  _buildStatItem('อุณหภูมิเฉลี่ย', '${avgTemp.toStringAsFixed(1)}°C', const Color(0xFFF59E0B)),
                  _buildStatItem('ความชื้นสัมพัทธ์', '${avgHum.toStringAsFixed(1)}%', const Color(0xFF06B6D4)),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Charts Stack
          SparklineChart(
            data: soilList,
            lineColor: const Color(0xFF10B981),
            title: 'ความชื้นในดิน (Soil Moisture History)',
            unit: '%',
          ),
          const SizedBox(height: 12),

          SparklineChart(
            data: tempList,
            lineColor: const Color(0xFFF59E0B),
            title: 'อุณหภูมิอากาศ (Air Temperature History)',
            unit: '°C',
          ),
          const SizedBox(height: 12),

          SparklineChart(
            data: humList,
            lineColor: const Color(0xFF06B6D4),
            title: 'ความชื้นสัมพัทธ์ (Relative Humidity History)',
            unit: '%',
          ),
          const SizedBox(height: 12),

          SparklineChart(
            data: lightList,
            lineColor: const Color(0xFFEAB308),
            title: 'ความสว่างแสงแดด (Light Intensity History)',
            unit: 'Lux',
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Text(value, style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16, color: color)),
        const SizedBox(height: 2),
        Text(label, style: const TextStyle(fontSize: 11, color: Colors.grey)),
      ],
    );
  }

  void _showExportDialog(BuildContext context, FarmViewModel vm) {
    final jsonData = jsonEncode({
      'team_no': vm.teamNumber,
      'exported_at': DateTime.now().toIso8601String(),
      'sensors_current': vm.sensors.toJson(),
      'records_count': vm.history.length,
      'espnow': {
        'sender': vm.espNow.senderNode,
        'receiver': vm.espNow.receiverNode,
        'rssi': vm.espNow.rssi,
        'channel': vm.espNow.channel,
      },
    });

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('ดาวน์โหลดข้อมูลกลุ่ม (JSON Export)'),
        content: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text('โครงสร้าง JSON สำหรับส่งผู้สอนตามใบงาน:'),
              const SizedBox(height: 8),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.black12,
                  borderRadius: BorderRadius.circular(6),
                ),
                child: Text(
                  jsonData,
                  style: const TextStyle(fontFamily: 'monospace', fontSize: 11),
                ),
              ),
            ],
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(ctx).pop(),
            child: const Text('ปิด'),
          ),
          FilledButton(
            onPressed: () {
              Navigator.of(ctx).pop();
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('คัดลอก JSON คำตอบของกลุ่มเรียบร้อยแล้ว ✓')),
              );
            },
            child: const Text('คัดลอกไฟล์'),
          ),
        ],
      ),
    );
  }
}
