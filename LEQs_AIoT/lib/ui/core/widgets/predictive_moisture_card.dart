import 'package:flutter/material.dart';
import '../app_theme.dart';
import '../../../data/models/farm_models.dart';

class PredictiveMoistureCard extends StatelessWidget {
  final List<SoilPredictionPoint> predictions;
  final double currentMoisture;
  final double wiltingThreshold;

  const PredictiveMoistureCard({
    super.key,
    required this.predictions,
    required this.currentMoisture,
    required this.wiltingThreshold,
  });

  @override
  Widget build(BuildContext context) {
    final wiltingPoint = predictions.where((p) => p.isWiltingRisk).firstOrNull;

    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(color: AppTheme.skyCyan.withValues(alpha: 0.35), width: 1.2),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(6),
                decoration: BoxDecoration(
                  color: AppTheme.skyCyan.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.timeline, color: AppTheme.skyCyan, size: 18),
              ),
              const SizedBox(width: 10),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'AI พยากรณ์ความชื้นดินล่วงหน้า 6 ชม.',
                      style: TextStyle(
                        fontSize: 13,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimaryDark,
                      ),
                    ),
                    Text(
                      'Time-Series Regression & Evapotranspiration Curve',
                      style: TextStyle(fontSize: 10, color: AppTheme.textSecondaryDark),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 12),

          // Wilting Point Alert or Safe Status
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
            decoration: BoxDecoration(
              color: wiltingPoint != null
                  ? AppTheme.warmAmber.withValues(alpha: 0.15)
                  : AppTheme.primaryLight.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(
                color: wiltingPoint != null ? AppTheme.warmAmber : AppTheme.accentMint,
              ),
            ),
            child: Row(
              children: [
                Icon(
                  wiltingPoint != null ? Icons.warning_amber_rounded : Icons.verified,
                  color: wiltingPoint != null ? AppTheme.warmAmber : AppTheme.accentMint,
                  size: 18,
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    wiltingPoint != null
                        ? 'เตือน: ดินจะแตะจุดเริ่มขาดน้ำ (<${wiltingThreshold.toStringAsFixed(0)}%) เวลา ${wiltingPoint.targetTime.hour.toString().padLeft(2, '0')}:${wiltingPoint.targetTime.minute.toString().padLeft(2, '0')} น.'
                        : 'ความชื้นในดินมีแนวโน้มคงที่เพียงพอตลอด 6 ชั่วโมงข้างหน้า',
                    style: TextStyle(
                      fontSize: 11,
                      fontWeight: FontWeight.bold,
                      color: wiltingPoint != null ? AppTheme.warmAmber : AppTheme.accentMint,
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // 6-Hour Timeline Prediction Cards
          SizedBox(
            height: 90,
            child: ListView.separated(
              scrollDirection: Axis.horizontal,
              itemCount: predictions.length,
              separatorBuilder: (c, i) => const SizedBox(width: 8),
              itemBuilder: (ctx, index) {
                final point = predictions[index];
                final hourStr = '+${index + 1} ชม.';
                final timeStr = '${point.targetTime.hour.toString().padLeft(2, '0')}:00';

                return Container(
                  width: 82,
                  padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 6),
                  decoration: BoxDecoration(
                    color: point.isWiltingRisk
                        ? AppTheme.alertRed.withValues(alpha: 0.15)
                        : Colors.white.withValues(alpha: 0.04),
                    borderRadius: BorderRadius.circular(10),
                    border: Border.all(
                      color: point.isWiltingRisk
                          ? AppTheme.alertRed.withValues(alpha: 0.5)
                          : AppTheme.cardDarkBorder,
                    ),
                  ),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(
                        hourStr,
                        style: const TextStyle(fontSize: 10, color: AppTheme.textSecondaryDark),
                      ),
                      Text(
                        timeStr,
                        style: const TextStyle(fontSize: 10, color: AppTheme.textSecondaryDark),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        '${point.predictedMoisture}%',
                        style: TextStyle(
                          fontSize: 14,
                          fontWeight: FontWeight.bold,
                          color: point.isWiltingRisk ? AppTheme.alertRed : AppTheme.skyCyan,
                        ),
                      ),
                      Text(
                        '±${(point.upperConfidence - point.predictedMoisture).toStringAsFixed(1)}%',
                        style: const TextStyle(fontSize: 9, color: AppTheme.textSecondaryDark),
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
}
