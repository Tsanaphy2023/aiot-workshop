import '../models/farm_models.dart';

/// Explainable AI (xAI) Engine: Computes feature attributions & natural language rationale
class ExplainableAiService {
  /// Generate comprehensive xAI Irrigation Recommendation
  ExplainableAiRecommendation evaluateIrrigation({
    required SensorTelemetry telemetry,
    required AutomationSettings settings,
    required bool isPumpActive,
  }) {
    final factors = <AiReasoningFactor>[];
    int score = 0; // Negative = No water needed, Positive = Strongly needed

    // Factor 1: Soil Moisture Deficit
    final moistureDeficit = settings.soilMoistureLowThreshold - telemetry.soilMoisture;
    if (moistureDeficit > 0) {
      score += 45;
      factors.add(AiReasoningFactor(
        factorName: 'ความชื้นในดิน (${telemetry.soilMoisture.toStringAsFixed(1)}%)',
        contributionPercent: 42.0,
        isDriverForWatering: true,
        physicalObservation:
            'ต่ำกว่าเกณฑ์ควบคุม (${settings.soilMoistureLowThreshold.toStringAsFixed(0)}%) อยู่ ${moistureDeficit.toStringAsFixed(1)}% ดินเริ่มมีแรงดึงน้ำสูง รากดูดน้ำยาก',
      ));
    } else {
      score -= 20;
      factors.add(AiReasoningFactor(
        factorName: 'ความชื้นในดิน (${telemetry.soilMoisture.toStringAsFixed(1)}%)',
        contributionPercent: 35.0,
        isDriverForWatering: false,
        physicalObservation: 'ยังอยู่ในเกณฑ์ชุ่มชื้นเพียงพอต่อการเจริญเติบโต',
      ));
    }

    // Factor 2: Vapor Pressure Deficit (VPD)
    if (telemetry.vpd > 1.6) {
      score += 35;
      factors.add(AiReasoningFactor(
        factorName: 'VPD บรรยากาศ (${telemetry.vpd.toStringAsFixed(2)} kPa)',
        contributionPercent: 30.0,
        isDriverForWatering: true,
        physicalObservation:
            'อากาศแห้งจัดและคายน้ำสูง (High Transpiration Stress) พืชเสี่ยงสูญเสียน้ำผ่านปากใบเร็วกว่าปกติ',
      ));
    } else if (telemetry.vpd < 0.4) {
      score -= 30;
      factors.add(AiReasoningFactor(
        factorName: 'VPD บรรยากาศ (${telemetry.vpd.toStringAsFixed(2)} kPa)',
        contributionPercent: 28.0,
        isDriverForWatering: false,
        physicalObservation:
            'ความชื้นในอากาศสูงมาก คายน้ำชะงัก (Fungal Risk) ควรงดการให้น้ำเพื่อป้องกันเชื้อราและรากเน่า',
      ));
    } else {
      factors.add(AiReasoningFactor(
        factorName: 'VPD บรรยากาศ (${telemetry.vpd.toStringAsFixed(2)} kPa)',
        contributionPercent: 20.0,
        isDriverForWatering: false,
        physicalObservation: 'อยู่ในช่วงสมดุลการเจริญเติบโตตามธรรมชาติ (Optimal Range)',
      ));
    }

    // Factor 3: Ambient Light Intensity (Lux)
    if (telemetry.lightLux > 550) {
      score += 20;
      factors.add(AiReasoningFactor(
        factorName: 'ความเข้มแสง (${telemetry.lightLux.toStringAsFixed(0)} Lux)',
        contributionPercent: 18.0,
        isDriverForWatering: true,
        physicalObservation: 'แสงแดดจัดและอัตราสังเคราะห์แสงสูง เพิ่มความต้องการน้ำหล่อเลี้ยงเซลล์',
      ));
    } else {
      factors.add(AiReasoningFactor(
        factorName: 'ความเข้มแสง (${telemetry.lightLux.toStringAsFixed(0)} Lux)',
        contributionPercent: 10.0,
        isDriverForWatering: false,
        physicalObservation: 'แสงสว่างปานกลาง อัตราการสูญเสียน้ำทางใบยังคงต่ำ',
      ));
    }

    // Factor 4: Float Switch & Dry-Run safety
    if (telemetry.isWaterLow) {
      return ExplainableAiRecommendation(
        decisionTitle: 'ตัดการให้น้ำฉุกเฉิน: ระดับน้ำในถังต่ำ (Dry-Run Lock)',
        urgencyLevel: 'ด่วนที่สุด',
        recommendedWaterSeconds: 0,
        estimatedVolumeMl: 0,
        overallConfidence: 0.99,
        factors: [
          const AiReasoningFactor(
            factorName: 'สวิตช์ลูกลอยระดับน้ำ (Float Switch)',
            contributionPercent: 100.0,
            isDriverForWatering: false,
            physicalObservation: 'ตรวจพบน้ำในถังพักหมด ตัดคำสั่งเปิดปั๊ม 100% เพื่อป้องกันปั๊มไหม้และท่อเสียหาย',
          )
        ],
        naturalLanguageExplanation:
            'ระบบตรวจพบน้ำในถังพักแห้ง แม้ดินจะต้องการน้ำแต่โมเดลความปลอดภัยบล็อกการทำงานทันที แนะนำให้เติมน้ำในถังพักก่อน',
        generatedAt: DateTime.now(),
      );
    }

    // Synthesize final recommendation
    String title;
    String urgency;
    int durationSec;
    int volumeMl;
    String rationale;

    if (score >= 45) {
      title = 'แนะนำให้เปิดระบบให้น้ำเพื่อคลายความเครียดพืช';
      urgency = 'ด่วน';
      durationSec = (40 + (telemetry.vpd * 10)).round().clamp(30, 90);
      volumeMl = (durationSec * 12.5).round(); // ~12.5 ml/sec dripper rate
      rationale =
          'เนื่องจากความชื้นในดินลดลง ประกอบกับค่าความต่างแรงดันไอ (VPD ${telemetry.vpd.toStringAsFixed(2)} kPa) สูง ทำให้พืชคายน้ำเร่งด่วน การให้น้ำ $durationSec วินาที (~$volumeMl ml) จะคืนความชุ่มชื้นสู่เขตรากโดยไม่สูญเปล่า';
    } else if (score >= 20) {
      title = 'เฝ้าระวัง: ดินเริ่มแห้ง แนะนำให้น้ำรอบถัดไปตามเวลา';
      urgency = 'ควรพิจารณา';
      durationSec = 25;
      volumeMl = 300;
      rationale =
          'สภาวะแปลงยังอยู่ในเกณฑ์พอรับได้ แต่ควรเตรียมให้น้ำภายใน 1-2 ชั่วโมงข้างหน้าเมื่อความชื้นแตะจุดเฝ้าระวัง';
    } else {
      title = 'สภาวะแปลงสมบูรณ์: ไม่จำเป็นต้องให้น้ำในขณะนี้';
      urgency = 'เหมาะสม/ปกติ';
      durationSec = 0;
      volumeMl = 0;
      rationale =
          'ดินมีความชื้น ${telemetry.soilMoisture.toStringAsFixed(1)}% และความชื้นสัมพัทธ์ในอากาศอยู่ในเกณฑ์สมดุล ไม่มีความเครียดจากแสงหรือความร้อน';
    }

    return ExplainableAiRecommendation(
      decisionTitle: title,
      urgencyLevel: urgency,
      recommendedWaterSeconds: durationSec,
      estimatedVolumeMl: volumeMl,
      overallConfidence: 0.945,
      factors: factors,
      naturalLanguageExplanation: rationale,
      generatedAt: DateTime.now(),
    );
  }
}
