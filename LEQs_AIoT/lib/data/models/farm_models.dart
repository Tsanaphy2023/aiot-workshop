import 'dart:math' as math;
import 'package:flutter/foundation.dart';

/// Real-time sensor telemetry model from GoGo-IoT field node
@immutable
class SensorTelemetry {
  final double temperature; // SHT30 Air Temperature in °C
  final double humidity; // SHT30 Air Relative Humidity in %
  final double lightLux; // BH1750 Ambient Light in lux
  final double soilMoisture; // Soil Moisture in % (0 - 100)
  final bool isWaterLow; // Float Switch: true = water dry/empty
  final DateTime timestamp;

  // Edge Agriphysics & TinyML Metrics
  final double vpd; // Vapor Pressure Deficit in kPa
  final String plantStress; // OPTIMAL, MILD_STRESS, HIGH_TRANSPIRATION, FUNGAL_RISK
  final bool isSensorAnomaly;
  final String anomalyMessage;

  const SensorTelemetry({
    required this.temperature,
    required this.humidity,
    required this.lightLux,
    required this.soilMoisture,
    required this.isWaterLow,
    required this.timestamp,
    double? vpd,
    this.plantStress = 'OPTIMAL',
    this.isSensorAnomaly = false,
    this.anomalyMessage = '',
  }) : vpd = vpd ?? 1.05;

  static double calculateVpd(double tempC, double rhPercent) {
    // Tetens equation: Saturation Vapor Pressure (kPa)
    final vpSat = 0.61078 * math.exp((17.27 * tempC) / (tempC + 237.3));
    final vpAct = vpSat * (rhPercent / 100.0);
    final v = vpSat - vpAct;
    return v < 0.0 ? 0.0 : double.parse(v.toStringAsFixed(2));
  }

  static String evaluatePlantStress(double vpdVal) {
    if (vpdVal < 0.4) return 'FUNGAL_RISK';
    if (vpdVal <= 1.2) return 'OPTIMAL';
    if (vpdVal <= 1.6) return 'MILD_STRESS';
    return 'HIGH_TRANSPIRATION';
  }

  String get vpdStatusTh {
    if (vpd < 0.4) return 'ต่ำ (เสี่ยงเกิดเชื้อรา/โรคพืช)';
    if (vpd <= 1.2) return 'เหมาะสม (ปากใบเปิดสมบูรณ์)';
    if (vpd <= 1.6) return 'เริ่มเครียด (คายน้ำปานกลาง)';
    return 'วิกฤต (พืชคายน้ำรุนแรง)';
  }

  factory SensorTelemetry.initial() {
    const t = 28.4;
    const h = 61.2;
    final v = SensorTelemetry.calculateVpd(t, h);
    return SensorTelemetry(
      temperature: t,
      humidity: h,
      lightLux: 350.0,
      soilMoisture: 48.5,
      isWaterLow: false,
      timestamp: DateTime.now(),
      vpd: v,
      plantStress: SensorTelemetry.evaluatePlantStress(v),
    );
  }

  SensorTelemetry copyWith({
    double? temperature,
    double? humidity,
    double? lightLux,
    double? soilMoisture,
    bool? isWaterLow,
    DateTime? timestamp,
    double? vpd,
    String? plantStress,
    bool? isSensorAnomaly,
    String? anomalyMessage,
  }) {
    final newTemp = temperature ?? this.temperature;
    final newHum = humidity ?? this.humidity;
    final computedVpd = vpd ?? SensorTelemetry.calculateVpd(newTemp, newHum);

    return SensorTelemetry(
      temperature: newTemp,
      humidity: newHum,
      lightLux: lightLux ?? this.lightLux,
      soilMoisture: soilMoisture ?? this.soilMoisture,
      isWaterLow: isWaterLow ?? this.isWaterLow,
      timestamp: timestamp ?? this.timestamp,
      vpd: computedVpd,
      plantStress: plantStress ?? SensorTelemetry.evaluatePlantStress(computedVpd),
      isSensorAnomaly: isSensorAnomaly ?? this.isSensorAnomaly,
      anomalyMessage: anomalyMessage ?? this.anomalyMessage,
    );
  }

  Map<String, dynamic> toJson() => {
        'temperature': temperature,
        'humidity': humidity,
        'lightLux': lightLux,
        'soilMoisture': soilMoisture,
        'isWaterLow': isWaterLow,
        'vpd': vpd,
        'plantStress': plantStress,
        'isSensorAnomaly': isSensorAnomaly,
        'anomalyMessage': anomalyMessage,
        'timestamp': timestamp.toIso8601String(),
      };
}

/// Actuator & Relay control states
@immutable
class ActuatorState {
  final bool isPumpOn;
  final bool isGrowLightOn;
  final bool isAutoMode;
  final int pumpRemainingSeconds;
  final bool isEmergencyStopped;
  final String? lastAlertMessage;

  const ActuatorState({
    required this.isPumpOn,
    required this.isGrowLightOn,
    required this.isAutoMode,
    required this.pumpRemainingSeconds,
    required this.isEmergencyStopped,
    this.lastAlertMessage,
  });

  factory ActuatorState.initial() {
    return const ActuatorState(
      isPumpOn: false,
      isGrowLightOn: false,
      isAutoMode: true,
      pumpRemainingSeconds: 0,
      isEmergencyStopped: false,
      lastAlertMessage: null,
    );
  }

  ActuatorState copyWith({
    bool? isPumpOn,
    bool? isGrowLightOn,
    bool? isAutoMode,
    int? pumpRemainingSeconds,
    bool? isEmergencyStopped,
    String? lastAlertMessage,
  }) {
    return ActuatorState(
      isPumpOn: isPumpOn ?? this.isPumpOn,
      isGrowLightOn: isGrowLightOn ?? this.isGrowLightOn,
      isAutoMode: isAutoMode ?? this.isAutoMode,
      pumpRemainingSeconds: pumpRemainingSeconds ?? this.pumpRemainingSeconds,
      isEmergencyStopped: isEmergencyStopped ?? this.isEmergencyStopped,
      lastAlertMessage: lastAlertMessage ?? this.lastAlertMessage,
    );
  }
}

/// ESP-NOW Long Range Telemetry & Bridge Health
@immutable
class EspNowTelemetry {
  final String senderNode;
  final String receiverNode;
  final int channel;
  final int rssi; // e.g. -42 dBm to -68 dBm
  final int packetCount;
  final int packetLost;
  final bool isLinkConnected;
  final DateTime lastPacketTime;
  final double humDirect;
  final double humEspNow;
  final double lightDirect;
  final double lightEspNow;

  const EspNowTelemetry({
    required this.senderNode,
    required this.receiverNode,
    required this.channel,
    required this.rssi,
    required this.packetCount,
    required this.packetLost,
    required this.isLinkConnected,
    required this.lastPacketTime,
    required this.humDirect,
    required this.humEspNow,
    required this.lightDirect,
    required this.lightEspNow,
  });

  factory EspNowTelemetry.initial() {
    return EspNowTelemetry(
      senderNode: 'gogo-iot-red-242dcc',
      receiverNode: 'farm-receiver-red-d4e5f6',
      channel: 6,
      rssi: -42,
      packetCount: 1240,
      packetLost: 2,
      isLinkConnected: true,
      lastPacketTime: DateTime.now(),
      humDirect: 61.2,
      humEspNow: 61.2,
      lightDirect: 350.0,
      lightEspNow: 350.0,
    );
  }

  double get packetDeliveryRate {
    final total = packetCount + packetLost;
    if (total == 0) return 100.0;
    return (packetCount / total) * 100.0;
  }

  EspNowTelemetry copyWith({
    String? senderNode,
    String? receiverNode,
    int? channel,
    int? rssi,
    int? packetCount,
    int? packetLost,
    bool? isLinkConnected,
    DateTime? lastPacketTime,
    double? humDirect,
    double? humEspNow,
    double? lightDirect,
    double? lightEspNow,
  }) {
    return EspNowTelemetry(
      senderNode: senderNode ?? this.senderNode,
      receiverNode: receiverNode ?? this.receiverNode,
      channel: channel ?? this.channel,
      rssi: rssi ?? this.rssi,
      packetCount: packetCount ?? this.packetCount,
      packetLost: packetLost ?? this.packetLost,
      isLinkConnected: isLinkConnected ?? this.isLinkConnected,
      lastPacketTime: lastPacketTime ?? this.lastPacketTime,
      humDirect: humDirect ?? this.humDirect,
      humEspNow: humEspNow ?? this.humEspNow,
      lightDirect: lightDirect ?? this.lightDirect,
      lightEspNow: lightEspNow ?? this.lightEspNow,
    );
  }
}

/// Think & Failure Lab: Farm Automation Rules & Fail-Safe Config
@immutable
class AutomationSettings {
  final double soilMoistureLowThreshold; // Start watering below this %
  final double soilMoistureHighThreshold; // Stop watering above this %
  final int maxPumpRunSeconds; // Watchdog fail-safe run timer (e.g. 180s)
  final bool dryRunProtectionEnabled; // Interlock with float switch
  final int watchdogAlertTimeoutSeconds; // ESP-NOW deadman alert (e.g. 30s)

  const AutomationSettings({
    required this.soilMoistureLowThreshold,
    required this.soilMoistureHighThreshold,
    required this.maxPumpRunSeconds,
    required this.dryRunProtectionEnabled,
    required this.watchdogAlertTimeoutSeconds,
  });

  factory AutomationSettings.initial() {
    return const AutomationSettings(
      soilMoistureLowThreshold: 40.0,
      soilMoistureHighThreshold: 75.0,
      maxPumpRunSeconds: 180,
      dryRunProtectionEnabled: true,
      watchdogAlertTimeoutSeconds: 30,
    );
  }

  AutomationSettings copyWith({
    double? soilMoistureLowThreshold,
    double? soilMoistureHighThreshold,
    int? maxPumpRunSeconds,
    bool? dryRunProtectionEnabled,
    int? watchdogAlertTimeoutSeconds,
  }) {
    return AutomationSettings(
      soilMoistureLowThreshold:
          soilMoistureLowThreshold ?? this.soilMoistureLowThreshold,
      soilMoistureHighThreshold:
          soilMoistureHighThreshold ?? this.soilMoistureHighThreshold,
      maxPumpRunSeconds: maxPumpRunSeconds ?? this.maxPumpRunSeconds,
      dryRunProtectionEnabled:
          dryRunProtectionEnabled ?? this.dryRunProtectionEnabled,
      watchdogAlertTimeoutSeconds:
          watchdogAlertTimeoutSeconds ?? this.watchdogAlertTimeoutSeconds,
    );
  }
}

/// Historical trend point for charts
@immutable
class HistoryRecord {
  final DateTime timestamp;
  final double temperature;
  final double humidity;
  final double soilMoisture;
  final double lightLux;
  final bool isPumpActive;

  const HistoryRecord({
    required this.timestamp,
    required this.temperature,
    required this.humidity,
    required this.soilMoisture,
    required this.lightLux,
    required this.isPumpActive,
  });
}

/// Vision Deep Learning: Leaf Disease Diagnosis Model
@immutable
class LeafDiseaseDiagnosis {
  final String diseaseId;
  final String diseaseNameTh;
  final String diseaseNameEn;
  final String scientificName;
  final double confidence; // 0.0 - 1.0 (e.g. 0.94)
  final String severity; // "ปกติ/สมบูรณ์", "ระยะเริ่มต้น (Mild)", "ระยะปานกลาง (Moderate)", "ระยะวิกฤต (Severe)"
  final String symptomsTh;
  final List<String> organicRemedies;
  final List<String> chemicalRemedies;
  final List<String> preventionTips;
  final DateTime diagnosedAt;

  const LeafDiseaseDiagnosis({
    required this.diseaseId,
    required this.diseaseNameTh,
    required this.diseaseNameEn,
    required this.scientificName,
    required this.confidence,
    required this.severity,
    required this.symptomsTh,
    required this.organicRemedies,
    required this.chemicalRemedies,
    required this.preventionTips,
    required this.diagnosedAt,
  });

  bool get isHealthy => diseaseId == 'healthy';
}

/// Time-Series Deep Learning / Regression: 6-Hour Soil Moisture Forecast Point
@immutable
class SoilPredictionPoint {
  final DateTime targetTime;
  final double predictedMoisture; // Projected %
  final double lowerConfidence; // 95% Confidence interval lower
  final double upperConfidence; // 95% Confidence interval upper
  final bool isWiltingRisk; // True if falling below wilting threshold

  const SoilPredictionPoint({
    required this.targetTime,
    required this.predictedMoisture,
    required this.lowerConfidence,
    required this.upperConfidence,
    required this.isWiltingRisk,
  });
}

/// Explainable AI (xAI): Reasoning factor with feature weight
@immutable
class AiReasoningFactor {
  final String factorName;
  final double contributionPercent; // e.g. 42.0%
  final bool isDriverForWatering; // True if push towards watering
  final String physicalObservation; // e.g. "VPD 1.75 kPa อยู่ในเกณฑ์คายน้ำรุนแรง"

  const AiReasoningFactor({
    required this.factorName,
    required this.contributionPercent,
    required this.isDriverForWatering,
    required this.physicalObservation,
  });
}

/// Explainable AI (xAI): Full Decision & Recommendation Report
@immutable
class ExplainableAiRecommendation {
  final String decisionTitle; // e.g. "แนะนำรดน้ำทันทีเพื่อคลายความเครียดพืช"
  final String urgencyLevel; // "เหมาะสม/ปกติ", "ควรพิจารณา", "ด่วนที่สุด"
  final int recommendedWaterSeconds; // e.g. 45 วินาที
  final int estimatedVolumeMl; // e.g. 350 ml
  final double overallConfidence; // e.g. 0.96
  final List<AiReasoningFactor> factors;
  final String naturalLanguageExplanation;
  final DateTime generatedAt;

  const ExplainableAiRecommendation({
    required this.decisionTitle,
    required this.urgencyLevel,
    required this.recommendedWaterSeconds,
    required this.estimatedVolumeMl,
    required this.overallConfidence,
    required this.factors,
    required this.naturalLanguageExplanation,
    required this.generatedAt,
  });
}

