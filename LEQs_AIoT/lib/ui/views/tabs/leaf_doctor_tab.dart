import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../core/app_theme.dart';
import '../../view_models/farm_view_model.dart';

class LeafDoctorTab extends StatefulWidget {
  const LeafDoctorTab({super.key});

  @override
  State<LeafDoctorTab> createState() => _LeafDoctorTabState();
}

class _LeafDoctorTabState extends State<LeafDoctorTab> with SingleTickerProviderStateMixin {
  late AnimationController _animController;
  late Animation<double> _scanLineAnimation;
  String _selectedSampleId = 'powdery_mildew';

  @override
  void initState() {
    super.initState();
    _animController = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);

    _scanLineAnimation = Tween<double>(begin: 0.1, end: 0.9).animate(
      CurvedAnimation(parent: _animController, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _animController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final vm = context.watch<FarmViewModel>();
    final diag = vm.currentLeafDiagnosis;

    Color severityColor;
    if (diag.isHealthy) {
      severityColor = AppTheme.accentMint;
    } else if (diag.severity.contains('รุนแรง') || diag.severity.contains('Severe')) {
      severityColor = AppTheme.alertRed;
    } else if (diag.severity.contains('ปานกลาง') || diag.severity.contains('Moderate')) {
      severityColor = AppTheme.warmAmber;
    } else {
      severityColor = AppTheme.skyCyan;
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Header
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppTheme.accentMint.withValues(alpha: 0.15),
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.document_scanner, color: AppTheme.accentMint, size: 22),
              ),
              const SizedBox(width: 12),
              const Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'หมอพืช AI (Leaf Doctor)',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.bold,
                        color: AppTheme.textPrimaryDark,
                      ),
                    ),
                    Text(
                      'On-Device Deep Learning • MobileNetV3 Vision',
                      style: TextStyle(fontSize: 11, color: AppTheme.textSecondaryDark),
                    ),
                  ],
                ),
              ),
            ],
          ),

          const SizedBox(height: 14),

          // Sample Selector Chips (For Live Demonstration & Field Testing)
          const Text(
            'เลือกตัวอย่างใบพืชเพื่อจำลองการสแกน หรือถ่ายภาพจริง:',
            style: TextStyle(fontSize: 12, color: AppTheme.textSecondaryDark),
          ),
          const SizedBox(height: 8),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            child: Row(
              children: [
                _buildSampleChip('powdery_mildew', '⚪️ ราแป้ง', vm),
                const SizedBox(width: 8),
                _buildSampleChip('early_blight', '🟤 ใบไหม้', vm),
                const SizedBox(width: 8),
                _buildSampleChip('rust', '🟠 ราสนิม', vm),
                const SizedBox(width: 8),
                _buildSampleChip('thrips_pest', '🦗 เพลี้ยไฟ', vm),
                const SizedBox(width: 8),
                _buildSampleChip('healthy', '🌿 ใบสมบูรณ์', vm),
              ],
            ),
          ),

          const SizedBox(height: 14),

          // Camera Viewfinder HUD (Cyber Agri-Tech Scan Box)
          Container(
            height: 220,
            decoration: BoxDecoration(
              color: Colors.black,
              borderRadius: BorderRadius.circular(18),
              border: Border.all(color: AppTheme.accentMint.withValues(alpha: 0.4), width: 1.5),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.accentMint.withValues(alpha: 0.15),
                  blurRadius: 18,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Stack(
              children: [
                // Background Simulated Leaf Pattern
                Center(
                  child: Icon(
                    Icons.spa,
                    size: 110,
                    color: AppTheme.accentMint.withValues(alpha: 0.15),
                  ),
                ),

                // Corner Reticles
                _buildCornerReticle(top: 12, left: 12),
                _buildCornerReticle(top: 12, right: 12),
                _buildCornerReticle(bottom: 12, left: 12),
                _buildCornerReticle(bottom: 12, right: 12),

                // Scanning Line Animation
                AnimatedBuilder(
                  animation: _scanLineAnimation,
                  builder: (context, child) {
                    return Positioned(
                      top: 220 * _scanLineAnimation.value,
                      left: 20,
                      right: 20,
                      child: Container(
                        height: 2,
                        decoration: BoxDecoration(
                          color: AppTheme.accentMint,
                          boxShadow: [
                            BoxShadow(
                              color: AppTheme.accentMint.withValues(alpha: 0.8),
                              blurRadius: 8,
                              spreadRadius: 2,
                            ),
                          ],
                        ),
                      ),
                    );
                  },
                ),

                // Center Crosshair & Live Detection Label
                Center(
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.65),
                      borderRadius: BorderRadius.circular(8),
                      border: Border.all(color: AppTheme.accentMint.withValues(alpha: 0.5)),
                    ),
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        const Icon(Icons.center_focus_strong, color: AppTheme.accentMint, size: 16),
                        const SizedBox(width: 6),
                        Text(
                          vm.isDiagnosingLeaf
                              ? 'กำลังประมวลผล Deep Learning...'
                              : 'AI พร้อมวิเคราะห์ใบพืช',
                          style: const TextStyle(
                            color: AppTheme.textPrimaryDark,
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),

                // Inference Engine Status Badge (Top-Right)
                Positioned(
                  top: 10,
                  right: 14,
                  child: Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
                    decoration: BoxDecoration(
                      color: Colors.black.withValues(alpha: 0.7),
                      borderRadius: BorderRadius.circular(6),
                      border: Border.all(color: AppTheme.accentMint.withValues(alpha: 0.4)),
                    ),
                    child: const Text(
                      'TFLite Edge • 3.8 MB',
                      style: TextStyle(color: AppTheme.accentMint, fontSize: 9, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 12),

          // Scan Trigger Button
          ElevatedButton.icon(
            onPressed: vm.isDiagnosingLeaf
                ? null
                : () => vm.diagnoseLeaf(sampleId: _selectedSampleId),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppTheme.accentMint,
              foregroundColor: Colors.black,
              padding: const EdgeInsets.symmetric(vertical: 14),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
            ),
            icon: vm.isDiagnosingLeaf
                ? const SizedBox(
                    width: 18,
                    height: 18,
                    child: CircularProgressIndicator(strokeWidth: 2, color: Colors.black),
                  )
                : const Icon(Icons.camera_alt, size: 20),
            label: Text(
              vm.isDiagnosingLeaf ? 'กำลังวิเคราะห์ภาพ...' : 'สแกนและวินิจฉัยโรคพืช (Run Vision AI)',
              style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14),
            ),
          ),

          const SizedBox(height: 18),

          // Diagnosis Result Card
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppTheme.cardDark,
              borderRadius: BorderRadius.circular(16),
              border: Border.all(color: severityColor.withValues(alpha: 0.4), width: 1.2),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // Diagnosis Header
                Row(
                  children: [
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: severityColor.withValues(alpha: 0.15),
                        shape: BoxShape.circle,
                      ),
                      child: Icon(
                        diag.isHealthy ? Icons.check_circle : Icons.warning_amber,
                        color: severityColor,
                        size: 22,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            diag.diseaseNameTh,
                            style: const TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: AppTheme.textPrimaryDark,
                            ),
                          ),
                          Text(
                            diag.scientificName,
                            style: const TextStyle(
                              fontSize: 11,
                              fontStyle: FontStyle.italic,
                              color: AppTheme.textSecondaryDark,
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(
                        color: severityColor.withValues(alpha: 0.2),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: severityColor),
                      ),
                      child: Text(
                        '${(diag.confidence * 100).toStringAsFixed(1)}%',
                        style: TextStyle(
                          fontSize: 12,
                          fontWeight: FontWeight.bold,
                          color: severityColor,
                        ),
                      ),
                    ),
                  ],
                ),

                const SizedBox(height: 10),

                // Severity Badge & Time
                Row(
                  children: [
                    Text(
                      'ระดับความรุนแรง: ',
                      style: const TextStyle(fontSize: 12, color: AppTheme.textSecondaryDark),
                    ),
                    Text(
                      diag.severity,
                      style: TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.bold,
                        color: severityColor,
                      ),
                    ),
                  ],
                ),

                const Divider(height: 22, color: AppTheme.cardDarkBorder),

                // Symptoms Description
                const Text(
                  'ลักษณะอาการที่ตรวจพบ (Observed Symptoms):',
                  style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: AppTheme.textPrimaryDark),
                ),
                const SizedBox(height: 4),
                Text(
                  diag.symptomsTh,
                  style: const TextStyle(fontSize: 12, color: AppTheme.textSecondaryDark, height: 1.4),
                ),

                const SizedBox(height: 14),

                // Organic & Biocontrol Remedies
                _buildActionSection(
                  title: '🌿 การรักษาทางชีวภาพและอินทรีย์ (Organic & Biocontrol):',
                  items: diag.organicRemedies,
                  accentColor: AppTheme.accentMint,
                ),

                const SizedBox(height: 12),

                // Chemical Remedies (Safe standard)
                if (diag.chemicalRemedies.isNotEmpty && !diag.isHealthy)
                  _buildActionSection(
                    title: '🧪 ทางเลือกสารเคมีป้องกันกำจัด (Chemical Options):',
                    items: diag.chemicalRemedies,
                    accentColor: AppTheme.warmAmber,
                  ),

                const SizedBox(height: 12),

                // Prevention Tips
                _buildActionSection(
                  title: '🛡 คำแนะนำการจัดการสภาพแวดล้อมและป้องกัน (Prevention):',
                  items: diag.preventionTips,
                  accentColor: AppTheme.skyCyan,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildSampleChip(String id, String label, FarmViewModel vm) {
    final isSelected = _selectedSampleId == id;
    return ChoiceChip(
      label: Text(label, style: TextStyle(fontSize: 12, color: isSelected ? Colors.black : AppTheme.textPrimaryDark)),
      selected: isSelected,
      selectedColor: AppTheme.accentMint,
      backgroundColor: AppTheme.cardDark,
      side: BorderSide(color: isSelected ? AppTheme.accentMint : AppTheme.cardDarkBorder),
      onSelected: (val) {
        if (val) {
          setState(() {
            _selectedSampleId = id;
          });
          vm.diagnoseLeaf(sampleId: id);
        }
      },
    );
  }

  Widget _buildCornerReticle({double? top, double? bottom, double? left, double? right}) {
    return Positioned(
      top: top,
      bottom: bottom,
      left: left,
      right: right,
      child: Container(
        width: 18,
        height: 18,
        decoration: BoxDecoration(
          border: Border(
            top: top != null ? const BorderSide(color: AppTheme.accentMint, width: 2.5) : BorderSide.none,
            bottom: bottom != null ? const BorderSide(color: AppTheme.accentMint, width: 2.5) : BorderSide.none,
            left: left != null ? const BorderSide(color: AppTheme.accentMint, width: 2.5) : BorderSide.none,
            right: right != null ? const BorderSide(color: AppTheme.accentMint, width: 2.5) : BorderSide.none,
          ),
        ),
      ),
    );
  }

  Widget _buildActionSection({
    required String title,
    required List<String> items,
    required Color accentColor,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          title,
          style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold, color: accentColor),
        ),
        const SizedBox(height: 6),
        ...items.map((it) {
          return Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 4),
            child: Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('• ', style: TextStyle(color: accentColor, fontWeight: FontWeight.bold)),
                Expanded(
                  child: Text(
                    it,
                    style: const TextStyle(fontSize: 11, color: AppTheme.textPrimaryDark, height: 1.3),
                  ),
                ),
              ],
            ),
          );
        }),
      ],
    );
  }
}
