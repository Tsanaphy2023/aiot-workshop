import 'dart:async';
import 'dart:convert';
import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

/// ============================================================
/// RemoteFarmService — ควบคุมบอร์ด ESPHome ผ่านอินเทอร์เน็ต
/// ============================================================
/// สถาปัตยกรรม:
///   📱 Flutter App (4G/5G)
///     └─► POST https://leqs.trycloudflare.com/cmu_aiot/smart_farm_dashboard/api/api.php?action=relay_esphome
///              └─► XAMPP PHP (LAN)
///                    └─► POST http://10.10.29.103/switch/รีเลย์%20(relay)/turn_on
///
/// ไม่จำเป็นต้องอยู่ WiFi เดียวกันกับบอร์ด
/// ============================================================

class RemoteFarmReading {
  final bool sensorOnline;
  final bool relayOnline;
  final bool relayState;
  final double? temperature;
  final double? humidity;
  final double? vpd;
  final double? dewPoint;
  final double? light;
  final double? pressure;
  final double? elevation;
  final double? vibration;
  final bool? floatSwitch;
  final String? floatState;
  final bool? pumpRunning;
  final String? pumpSensitivity;
  final String? ipAddress;
  final int? rssi;
  final double? uptime;
  final bool cached;
  final DateTime timestamp;

  RemoteFarmReading({
    required this.sensorOnline,
    required this.relayOnline,
    required this.relayState,
    this.temperature,
    this.humidity,
    this.vpd,
    this.dewPoint,
    this.light,
    this.pressure,
    this.elevation,
    this.vibration,
    this.floatSwitch,
    this.floatState,
    this.pumpRunning,
    this.pumpSensitivity,
    this.ipAddress,
    this.rssi,
    this.uptime,
    this.cached = false,
    required this.timestamp,
  });

  factory RemoteFarmReading.fromJson(Map<String, dynamic> json) {
    return RemoteFarmReading(
      sensorOnline: json['sensor_online'] as bool? ?? false,
      relayOnline: json['relay_online'] as bool? ?? false,
      relayState: json['relay_state'] as bool? ?? false,
      temperature: (json['temperature'] as num?)?.toDouble(),
      humidity: (json['humidity'] as num?)?.toDouble(),
      vpd: (json['vpd'] as num?)?.toDouble(),
      dewPoint: (json['dew_point'] as num?)?.toDouble(),
      light: (json['light'] as num?)?.toDouble(),
      pressure: (json['pressure'] as num?)?.toDouble(),
      elevation: (json['elevation'] as num?)?.toDouble(),
      vibration: (json['vibration'] as num?)?.toDouble(),
      floatSwitch: json['float_switch'] as bool?,
      floatState: json['float_state'] as String?,
      pumpRunning: json['pump_running'] as bool?,
      pumpSensitivity: json['pump_sensitivity']?.toString(),
      ipAddress: json['ip_address'] as String?,
      rssi: (json['rssi'] as num?)?.toInt(),
      uptime: (json['uptime'] as num?)?.toDouble(),
      cached: json['cached'] as bool? ?? false,
      timestamp: DateTime.tryParse(json['timestamp'] as String? ?? '') ?? DateTime.now(),
    );
  }

  /// แสดงระดับ VPD เป็นข้อความภาษาไทย
  String get vpdStatus {
    final v = vpd;
    if (v == null) return 'ไม่มีข้อมูล';
    if (v < 0.4) return 'ชื้นเกินไป 🌧';
    if (v < 0.8) return 'เหมาะสม ✅';
    if (v < 1.6) return 'ปกติ 🌤';
    return 'แห้งมาก ⚠️';
  }

  /// แสดงความแรงสัญญาณ WiFi ของบอร์ด
  String get rssiLabel {
    final r = rssi;
    if (r == null) return 'ไม่ทราบ';
    if (r >= -50) return 'ดีมาก 📶📶📶';
    if (r >= -65) return 'ดี 📶📶';
    if (r >= -75) return 'พอใช้ 📶';
    return 'อ่อน ⚠️';
  }
}

/// ผลลัพธ์การสั่งงานรีเลย์
class RelayCommandResult {
  final bool success;
  final bool state;
  final String hwResult;    // 'forwarded_ok' | 'hw_timeout'
  final String? error;
  final DateTime timestamp;

  RelayCommandResult({
    required this.success,
    required this.state,
    this.hwResult = '',
    this.error,
    required this.timestamp,
  });

  bool get reachedBoard => hwResult == 'forwarded_ok';
}

/// ============================================================
/// Service Class
/// ============================================================
class RemoteFarmService extends ChangeNotifier {
  // ─────────────── การตั้งค่า URL ───────────────
  /// URL ภายใน LAN (ใช้เมื่ออยู่ WiFi ฟาร์ม)
  static const String _defaultLocalUrl =
      'http://192.168.1.100/cmu_aiot/smart_farm_dashboard/api/api.php';

  /// URL สาธารณะ (Cloudflare Tunnel / ngrok) ใช้เมื่ออยู่ 4G/5G
  String remoteUrl;

  /// โหมดการเชื่อมต่อ
  ConnectionMode connectionMode;

  // ─────────────── State ───────────────
  RemoteFarmReading? _lastReading;
  bool _isLoading = false;
  String _statusMessage = 'ยังไม่ได้เชื่อมต่อ';
  bool _apiReachable = false;
  Timer? _pollTimer;

  RemoteFarmService({
    String? remoteUrl,
    this.connectionMode = ConnectionMode.auto,
  }) : remoteUrl = remoteUrl ?? _defaultLocalUrl;

  // ─────────────── Getters ───────────────
  RemoteFarmReading? get lastReading => _lastReading;
  bool get isLoading => _isLoading;
  String get statusMessage => _statusMessage;
  bool get apiReachable => _apiReachable;
  bool get relayState => _lastReading?.relayState ?? false;

  /// URL ที่ใช้จริงตาม connectionMode
  String get _activeUrl {
    switch (connectionMode) {
      case ConnectionMode.remote:
        return remoteUrl;
      case ConnectionMode.local:
        return _defaultLocalUrl;
      case ConnectionMode.auto:
        // ใช้ remoteUrl ที่ผู้ใช้กำหนด (อาจเป็น local หรือ cloud)
        return remoteUrl.isEmpty ? _defaultLocalUrl : remoteUrl;
    }
  }

  String _cleanUrl(String raw) {
    String url = raw.trim();
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'http://$url';
    }
    if (!url.contains('api.php')) {
      url = url.endsWith('/') ? '${url}api/api.php' : '$url/api/api.php';
    }
    return url;
  }

  // ─────────────── Ping / Health Check ───────────────
  /// ตรวจสอบว่า API server เข้าถึงได้จากเครือข่ายปัจจุบันหรือไม่
  Future<bool> pingApi({String? customUrl}) async {
    try {
      final base = _cleanUrl(customUrl ?? _activeUrl);
      final url = Uri.parse('$base?action=ping');
      final res = await http.get(url).timeout(const Duration(seconds: 5));
      if (res.statusCode == 200) {
        final json = jsonDecode(res.body);
        _apiReachable = json['status'] == 'ok';
        if (_apiReachable) {
          _statusMessage = '✅ เชื่อมต่อ API สำเร็จ';
        } else {
          _statusMessage = '⚠️ API ตอบรับผิดปกติ';
        }
        notifyListeners();
        return _apiReachable;
      }
    } catch (e) {
      _apiReachable = false;
      _statusMessage = '❌ ไม่สามารถเชื่อมต่อ API: ${e.runtimeType}';
      notifyListeners();
    }
    return false;
  }

  // ─────────────── Read Sensors ───────────────
  /// ดึงค่าเซนเซอร์จากบอร์ดผ่าน PHP relay
  /// ใช้ cache อัตโนมัติหากบอร์ด ESPHome ออฟไลน์ชั่วคราว
  Future<RemoteFarmReading?> fetchSensors({String? customUrl}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final base = _cleanUrl(customUrl ?? _activeUrl);
      final url = Uri.parse('$base?action=sensor_read');
      final res = await http.get(url).timeout(const Duration(seconds: 8));

      if (res.statusCode == 200) {
        final json = jsonDecode(res.body) as Map<String, dynamic>;
        if (json['status'] == 'success') {
          _lastReading = RemoteFarmReading.fromJson(json);
          _apiReachable = true;
          _statusMessage = _lastReading!.sensorOnline
              ? '📡 รับข้อมูลบอร์ดสำเร็จ'
              : (_lastReading!.cached ? '📦 ใช้ข้อมูล Cache (บอร์ดออฟไลน์)' : '⚠️ บอร์ดเซนเซอร์ไม่ตอบสนอง');
        }
      }
    } catch (e) {
      _apiReachable = false;
      _statusMessage = '❌ ดึงข้อมูลล้มเหลว: ${e.runtimeType}';
      debugPrint('[RemoteFarmService] fetchSensors error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return _lastReading;
  }

  // ─────────────── Relay Control ───────────────
  /// สั่ง ON/OFF รีเลย์ (ปั๊มน้ำ/วาล์ว) ผ่าน PHP relay → ESPHome
  Future<RelayCommandResult> setRelay(bool state, {String? customUrl}) async {
    _isLoading = true;
    notifyListeners();

    try {
      final base = _cleanUrl(customUrl ?? _activeUrl);
      final url = Uri.parse('$base?action=relay_esphome');
      final body = jsonEncode({'state': state});

      final res = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: body,
      ).timeout(const Duration(seconds: 10));

      if (res.statusCode == 200) {
        final json = jsonDecode(res.body) as Map<String, dynamic>;
        final result = RelayCommandResult(
          success: json['status'] == 'success',
          state: json['state'] as bool? ?? state,
          hwResult: json['hw_result'] as String? ?? '',
          timestamp: DateTime.tryParse(json['timestamp'] as String? ?? '') ?? DateTime.now(),
        );

        if (result.success) {
          // อัปเดต local reading ทันทีโดยไม่รอ fetch รอบใหม่
          if (_lastReading != null) {
            _lastReading = RemoteFarmReading(
              sensorOnline: _lastReading!.sensorOnline,
              relayOnline: _lastReading!.relayOnline,
              relayState: state,
              temperature: _lastReading!.temperature,
              humidity: _lastReading!.humidity,
              vpd: _lastReading!.vpd,
              dewPoint: _lastReading!.dewPoint,
              light: _lastReading!.light,
              pressure: _lastReading!.pressure,
              elevation: _lastReading!.elevation,
              vibration: _lastReading!.vibration,
              floatSwitch: _lastReading!.floatSwitch,
              floatState: _lastReading!.floatState,
              pumpRunning: state ? true : _lastReading!.pumpRunning,
              pumpSensitivity: _lastReading!.pumpSensitivity,
              ipAddress: _lastReading!.ipAddress,
              rssi: _lastReading!.rssi,
              uptime: _lastReading!.uptime,
              cached: false,
              timestamp: DateTime.now(),
            );
          }

          _statusMessage = state
              ? '💧 สั่ง ON รีเลย์สำเร็จ ${result.reachedBoard ? "(บอร์ดตอบรับ)" : "(PHP ส่งคำสั่งแล้ว)"}'
              : '🔴 สั่ง OFF รีเลย์สำเร็จ ${result.reachedBoard ? "(บอร์ดตอบรับ)" : "(PHP ส่งคำสั่งแล้ว)"}';
          _apiReachable = true;
        }

        _isLoading = false;
        notifyListeners();
        return result;
      }
    } catch (e) {
      _statusMessage = '❌ สั่งรีเลย์ล้มเหลว: ${e.runtimeType}';
      debugPrint('[RemoteFarmService] setRelay error: $e');
    }

    _isLoading = false;
    notifyListeners();
    return RelayCommandResult(
      success: false,
      state: !state, // ไม่เปลี่ยน
      error: _statusMessage,
      timestamp: DateTime.now(),
    );
  }

  // ─────────────── Auto-Polling ───────────────
  /// เริ่มดึงข้อมูลเซนเซอร์อัตโนมัติทุก [intervalSeconds] วินาที
  void startPolling({int intervalSeconds = 10}) {
    stopPolling();
    fetchSensors(); // ดึงทันทีเมื่อเริ่ม
    _pollTimer = Timer.periodic(
      Duration(seconds: intervalSeconds),
      (_) => fetchSensors(),
    );
    debugPrint('[RemoteFarmService] Polling started every ${intervalSeconds}s via $_activeUrl');
  }

  void stopPolling() {
    _pollTimer?.cancel();
    _pollTimer = null;
  }

  /// อัปเดต URL แล้วทดสอบการเชื่อมต่อใหม่
  Future<bool> updateUrl(String newUrl, {ConnectionMode? mode}) async {
    remoteUrl = newUrl.trim();
    if (mode != null) connectionMode = mode;
    notifyListeners();
    return pingApi();
  }

  @override
  void dispose() {
    stopPolling();
    super.dispose();
  }
}

/// โหมดการเชื่อมต่อ
enum ConnectionMode {
  /// เลือกอัตโนมัติ (ใช้ remoteUrl ที่กำหนด)
  auto,
  /// บังคับใช้ WiFi LAN เท่านั้น
  local,
  /// บังคับใช้ URL สาธารณะ (Cloudflare / ngrok)
  remote,
}
