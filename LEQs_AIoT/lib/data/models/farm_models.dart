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

  const SensorTelemetry({
    required this.temperature,
    required this.humidity,
    required this.lightLux,
    required this.soilMoisture,
    required this.isWaterLow,
    required this.timestamp,
  });

  factory SensorTelemetry.initial() {
    return SensorTelemetry(
      temperature: 28.4,
      humidity: 61.2,
      lightLux: 350.0,
      soilMoisture: 48.5,
      isWaterLow: false,
      timestamp: DateTime.now(),
    );
  }

  SensorTelemetry copyWith({
    double? temperature,
    double? humidity,
    double? lightLux,
    double? soilMoisture,
    bool? isWaterLow,
    DateTime? timestamp,
  }) {
    return SensorTelemetry(
      temperature: temperature ?? this.temperature,
      humidity: humidity ?? this.humidity,
      lightLux: lightLux ?? this.lightLux,
      soilMoisture: soilMoisture ?? this.soilMoisture,
      isWaterLow: isWaterLow ?? this.isWaterLow,
      timestamp: timestamp ?? this.timestamp,
    );
  }

  Map<String, dynamic> toJson() => {
        'temperature': temperature,
        'humidity': humidity,
        'lightLux': lightLux,
        'soilMoisture': soilMoisture,
        'isWaterLow': isWaterLow,
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
