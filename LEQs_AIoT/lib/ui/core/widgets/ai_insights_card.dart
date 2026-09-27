import 'package:flutter/material.dart';
import '../app_theme.dart';
import '../../../data/models/farm_models.dart';
import '../../view_models/farm_view_model.dart';

class AiInsightsCard extends StatelessWidget {
  final FarmViewModel viewModel;

  const AiInsightsCard({super.key, required this.viewModel});

  @override
  Widget build(BuildContext context) {
    final s = viewModel.sensors;
    final ai = viewModel.aiRecommendation;

    Color vpdColor;
    if (s.vpd < 0.4) {
      vpdColor = AppTheme.skyCyan;
    } else if (s.vpd <= 1.2) {
      vpdColor = AppTheme.accentMint;
    } else if (s.vpd <= 1.6) {
      vpdColor = AppTheme.warmAmber;
    } else {
      vpdColor = AppTheme.alertRed;
    }

    return Container(
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(16),
        border: Border.all(
          color: vpdColor.withValues(alpha: 0.35),
          width: 1.2,
        ),
        boxShadow: [
          BoxShadow(
            color: vpdColor.withValues(alpha: 0.08),
            blurRadius: 16,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header Bar
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
            decoration: BoxDecoration(
              color: vpdColor.withValues(alpha: 0.12),
              borderRadius: const BorderRadius.vertical(top: Radius.circular(15)),
            ),
            child: Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(6),
                  decoration: BoxDecoration(
                    color: vpdColor.withValues(alpha: 0.2),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(Icons.psychology, size: 16, color: vpdColor),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: Text(
                    'สมองกลเกษตร AI (Agriphysics Engine)',
                    style: const TextStyle(
                      fontSize: 13,
                      fontWeight: FontWeight.bold,
                      color: AppTheme.textPrimaryDark,
                    ),
                    maxLines: 1,
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                const SizedBox(width: 6),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 7, vertical: 3),
                  decoration: BoxDecoration(
                    color: Colors.black.withValues(alpha: 0.3),
                    borderRadius: BorderRadius.circular(6),
                    border: Border.all(color: vpdColor.withValues(alpha: 0.5)),
                  ),
                  child: Text(
                    'Edge TinyML',
                    style: TextStyle(
                      fontSize: 10,
                      fontWeight: FontWeight.bold,
                      color: vpdColor,
                    ),
                  ),
                ),
              ],
            ),
          ),

          Padding(
            padding: const EdgeInsets.all(14.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Live VPD Meter & Status (Responsive & Overflow-safe)
                Row(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: [
                    Expanded(
                      flex: 5,
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Text(
                            'แรงดึงระเหยน้ำบรรยากาศ (VPD)',
                            style: TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                          ),
                          const SizedBox(height: 2),
                          Row(
                            crossAxisAlignment: CrossAxisAlignment.baseline,
                            textBaseline: TextBaseline.alphabetic,
                            children: [
                              Text(
                                s.vpd.toStringAsFixed(2),
                                style: TextStyle(
                                  fontSize: 28,
                                  fontWeight: FontWeight.bold,
                                  color: vpdColor,
                                  letterSpacing: -1,
                                ),
                              ),
                              const SizedBox(width: 4),
                              const Text(
                                'kPa',
                                style: TextStyle(fontSize: 12, color: AppTheme.textSecondaryDark),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 8),
                    Flexible(
                      flex: 6,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 6),
                        decoration: BoxDecoration(
                          color: vpdColor.withValues(alpha: 0.15),
                          borderRadius: BorderRadius.circular(10),
                          border: Border.all(color: vpdColor.withValues(alpha: 0.4)),
                        ),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text(
                              'สถานะปากใบพืช',
                              style: TextStyle(fontSize: 10, color: vpdColor.withValues(alpha: 0.8)),
                              maxLines: 1,
                              overflow: TextOverflow.ellipsis,
                            ),
                            const SizedBox(height: 2),
                            Text(
                              s.vpdStatusTh,
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: vpdColor,
                              ),
                              textAlign: TextAlign.end,
                              maxLines: 2,
                              overflow: TextOverflow.ellipsis,
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 10),

                // VPD Segmented Progress Bar
                ClipRRect(
                  borderRadius: BorderRadius.circular(6),
                  child: SizedBox(
                    height: 6,
                    child: LinearProgressIndicator(
                      value: (s.vpd / 2.2).clamp(0.0, 1.0),
                      backgroundColor: Colors.white.withValues(alpha: 0.08),
                      valueColor: AlwaysStoppedAnimation<Color>(vpdColor),
                    ),
                  ),
                ),
                const SizedBox(height: 4),
                const Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('0.0 (ชื้นจัด)', style: TextStyle(fontSize: 9, color: AppTheme.textSecondaryDark)),
                    Text('0.8 - 1.2 (เหมาะสม)', style: TextStyle(fontSize: 9, color: AppTheme.accentMint)),
                    Text('2.2+ kPa (แห้งจัด)', style: TextStyle(fontSize: 9, color: AppTheme.textSecondaryDark)),
                  ],
                ),

                const Divider(height: 20, color: AppTheme.cardDarkBorder),

                // Explainable AI Decision Banner
                Row(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Icon(
                      Icons.tips_and_updates_outlined,
                      size: 20,
                      color: AppTheme.warmAmber,
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            ai.decisionTitle,
                            style: const TextStyle(
                              fontSize: 12,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.textPrimaryDark,
                            ),
                          ),
                          const SizedBox(height: 2),
                          Text(
                            'คำนวณจากความชื้นดิน, VPD, แสงแดด และสวิตช์ลูกลอย',
                            style: TextStyle(fontSize: 10, color: AppTheme.textSecondaryDark.withValues(alpha: 0.9)),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 10),

                // Button: Explain AI Reason (xAI BottomSheet trigger)
                OutlinedButton.icon(
                  onPressed: () => _showExplainableAiSheet(context, ai, viewModel),
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppTheme.accentMint, width: 1.2),
                    foregroundColor: AppTheme.accentMint,
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                    padding: const EdgeInsets.symmetric(vertical: 8, horizontal: 12),
                    minimumSize: const Size.fromHeight(36),
                  ),
                  icon: const Icon(Icons.auto_awesome, size: 16),
                  label: const Text(
                    'อธิบายเหตุผลการตัดสินใจ (Explain xAI)',
                    style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  void _showExplainableAiSheet(
    BuildContext context,
    ExplainableAiRecommendation ai,
    FarmViewModel vm,
  ) {
    showModalBottomSheet(
      context: context,
      backgroundColor: AppTheme.bgDark,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (ctx) {
        return Padding(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 20,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 24,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Handle bar
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: Colors.grey.shade600,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Title
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: AppTheme.accentMint.withValues(alpha: 0.15),
                      shape: BoxShape.circle,
                    ),
                    child: const Icon(Icons.auto_awesome, color: AppTheme.accentMint, size: 22),
                  ),
                  const SizedBox(width: 12),
                  const Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'ระบบอธิบายเหตุผลปัญญาประดิษฐ์ (xAI)',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppTheme.textPrimaryDark),
                        ),
                        Text(
                          'Explainable AI Multi-Criteria Decision Framework',
                          style: TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                        ),
                      ],
                    ),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              // Summary Box
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: AppTheme.cardDark,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppTheme.cardDarkBorder),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Text(
                          'ระดับความเร่งด่วน: ${ai.urgencyLevel}',
                          style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13, color: AppTheme.accentMint),
                        ),
                        const Spacer(),
                        Text(
                          'ความเชื่อมั่นโมเดล: ${(ai.overallConfidence * 100).toStringAsFixed(1)}%',
                          style: const TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                        ),
                      ],
                    ),
                    const SizedBox(height: 6),
                    Text(
                      ai.naturalLanguageExplanation,
                      style: const TextStyle(fontSize: 12, color: AppTheme.textPrimaryDark, height: 1.4),
                    ),
                    if (ai.recommendedWaterSeconds > 0) ...[
                      const SizedBox(height: 8),
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppTheme.primaryLight.withValues(alpha: 0.2),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Text(
                          'ปริมาณแนะนำ: ${ai.recommendedWaterSeconds} วินาที (~${ai.estimatedVolumeMl} ml ต่อหัวจ่าย)',
                          style: const TextStyle(
                            fontSize: 11,
                            fontWeight: FontWeight.bold,
                            color: AppTheme.accentMint,
                          ),
                        ),
                      ),
                    ],
                  ],
                ),
              ),

              const SizedBox(height: 16),
              const Text(
                'น้ำหนักปัจจัยในการตัดสินใจ (Feature Attributions):',
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold, color: AppTheme.textPrimaryDark),
              ),
              const SizedBox(height: 8),

              // Factors List
              ...ai.factors.map((f) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 8.0),
                  child: Container(
                    padding: const EdgeInsets.all(10),
                    decoration: BoxDecoration(
                      color: AppTheme.cardDark,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: f.isDriverForWatering
                            ? AppTheme.warmAmber.withValues(alpha: 0.3)
                            : AppTheme.cardDarkBorder,
                      ),
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(
                              f.isDriverForWatering ? Icons.arrow_upward : Icons.remove,
                              size: 14,
                              color: f.isDriverForWatering ? AppTheme.warmAmber : AppTheme.skyCyan,
                            ),
                            const SizedBox(width: 6),
                            Expanded(
                              child: Text(
                                f.factorName,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: AppTheme.textPrimaryDark,
                                ),
                              ),
                            ),
                            Text(
                              '${f.contributionPercent.toStringAsFixed(0)}% นัยสำคัญ',
                              style: TextStyle(
                                fontSize: 11,
                                fontWeight: FontWeight.bold,
                                color: f.isDriverForWatering ? AppTheme.warmAmber : AppTheme.textSecondaryDark,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 4),
                        Text(
                          f.physicalObservation,
                          style: const TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                        ),
                      ],
                    ),
                  ),
                );
              }),

              const SizedBox(height: 12),

              // Quick Action Button
              if (ai.recommendedWaterSeconds > 0)
                ElevatedButton.icon(
                  onPressed: () {
                    Navigator.of(ctx).pop();
                    vm.togglePump(true);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(
                        content: Text('เปิดปั๊มน้ำตามคำแนะนำ AI (${ai.recommendedWaterSeconds} วินาที)'),
                        backgroundColor: AppTheme.primaryLight,
                      ),
                    );
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: AppTheme.accentMint,
                    foregroundColor: Colors.black,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
                  ),
                  icon: const Icon(Icons.play_arrow, size: 18),
                  label: Text('เปิดปั๊มตามคำแนะนำ (${ai.recommendedWaterSeconds} วินาที)'),
                ),
            ],
          ),
        );
      },
    );
  }
}
