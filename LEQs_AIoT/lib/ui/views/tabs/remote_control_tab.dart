import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import '../../../data/services/remote_farm_service.dart';

/// ============================================================
/// Remote Control Tab — ควบคุมบอร์ด ESPHome ข้ามเครือข่าย WiFi
/// ============================================================
/// ใช้ PHP api.php เป็น Cloud Relay ผ่าน Cloudflare Tunnel
/// ไม่จำเป็นต้องอยู่ WiFi ฟาร์ม
/// ============================================================

class RemoteControlTab extends StatefulWidget {
  const RemoteControlTab({super.key});

  @override
  State<RemoteControlTab> createState() => _RemoteControlTabState();
}

class _RemoteControlTabState extends State<RemoteControlTab>
    with SingleTickerProviderStateMixin {
  late final RemoteFarmService _svc;
  final _urlController = TextEditingController();
  bool _isRelayOn = false;
  bool _commandLoading = false;
  String _lastStatus = '';
  Timer? _autoRefreshTimer;
  bool _autoPoll = false;
  late AnimationController _pulseAnim;
  late Animation<double> _pulse;

  // สีธีม
  static const _green = Color(0xFF10B981);
  static const _blue = Color(0xFF38BDF8);
  static const _orange = Color(0xFFF59E0B);
  static const _red = Color(0xFFEF4444);

  @override
  void initState() {
    super.initState();
    _svc = RemoteFarmService(
      remoteUrl: 'http://192.168.1.100/cmu_aiot/smart_farm_dashboard/api/api.php',
    );
    _urlController.text = _svc.remoteUrl;
    _svc.addListener(_onServiceChanged);

    _pulseAnim = AnimationController(
      vsync: this,
      duration: const Duration(seconds: 2),
    )..repeat(reverse: true);
    _pulse = Tween<double>(begin: 0.6, end: 1.0).animate(
      CurvedAnimation(parent: _pulseAnim, curve: Curves.easeInOut),
    );
  }

  void _onServiceChanged() {
    if (!mounted) return;
    setState(() {
      _isRelayOn = _svc.relayState;
      _lastStatus = _svc.statusMessage;
    });
  }

  @override
  void dispose() {
    _autoRefreshTimer?.cancel();
    _svc.dispose();
    _urlController.dispose();
    _pulseAnim.dispose();
    super.dispose();
  }

  // ─────────────── Actions ───────────────
  Future<void> _ping() async {
    setState(() => _lastStatus = '⏳ กำลังทดสอบการเชื่อมต่อ...');
    final ok = await _svc.updateUrl(_urlController.text.trim());
    setState(() {
      _lastStatus = ok ? '✅ เชื่อมต่อ API สำเร็จ' : '❌ ไม่สามารถเชื่อมต่อได้ — ตรวจสอบ URL';
    });
  }

  Future<void> _fetchSensors() async {
    await _svc.fetchSensors();
  }

  Future<void> _toggleRelay() async {
    setState(() => _commandLoading = true);
    final newState = !_isRelayOn;
    final result = await _svc.setRelay(newState);
    setState(() {
      _commandLoading = false;
      _isRelayOn = result.success ? newState : _isRelayOn;
    });

    if (!result.success) {
      _showSnack('❌ สั่งรีเลย์ล้มเหลว — ตรวจสอบ URL และการเชื่อมต่อ', isError: true);
    } else if (!result.reachedBoard) {
      _showSnack('⚠️ PHP รับคำสั่งแล้ว แต่บอร์ด ESPHome ไม่ตอบสนอง (อาจ offline)', isError: false);
    }
  }

  void _toggleAutoPoll(bool val) {
    setState(() => _autoPoll = val);
    if (val) {
      _svc.startPolling(intervalSeconds: 8);
    } else {
      _svc.stopPolling();
    }
  }

  void _showSnack(String msg, {bool isError = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(msg),
        backgroundColor: isError ? _red : _orange,
        behavior: SnackBarBehavior.floating,
        duration: const Duration(seconds: 4),
      ),
    );
  }

  // ─────────────── UI ───────────────
  @override
  Widget build(BuildContext context) {
    final reading = _svc.lastReading;
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final cardBg = isDark ? const Color(0xFF1E293B) : Colors.white;
    final textSub = isDark ? Colors.grey.shade400 : Colors.grey.shade600;

    return Scaffold(
      backgroundColor: isDark ? const Color(0xFF0F172A) : const Color(0xFFF1F5F9),
      body: ListView(
        padding: const EdgeInsets.all(12),
        children: [
          // ── URL ตั้งค่า ──────────────────────
          _card(
            cardBg,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Icon(Icons.cloud_outlined, color: _blue, size: 18),
                    const SizedBox(width: 6),
                    Text('URL เชื่อมต่อ', style: TextStyle(
                        fontWeight: FontWeight.bold, color: isDark ? Colors.white : Colors.black87)),
                    const Spacer(),
                    _badge(
                      _svc.apiReachable ? '● Online' : '○ Offline',
                      _svc.apiReachable ? _green : Colors.grey,
                    ),
                  ],
                ),
                const SizedBox(height: 8),
                TextField(
                  controller: _urlController,
                  style: const TextStyle(fontSize: 12, fontFamily: 'monospace'),
                  decoration: InputDecoration(
                    hintText: 'https://xxxx.trycloudflare.com/cmu_aiot/...api.php',
                    hintStyle: TextStyle(fontSize: 11, color: Colors.grey.shade500),
                    isDense: true,
                    contentPadding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
                    border: OutlineInputBorder(borderRadius: BorderRadius.circular(8)),
                    suffixIcon: IconButton(
                      icon: const Icon(Icons.copy, size: 16),
                      onPressed: () => Clipboard.setData(ClipboardData(text: _urlController.text)),
                    ),
                  ),
                ),
                const SizedBox(height: 6),
                // ป้ายตัวอย่าง URL
                _infoBox(isDark,
                    '💡 เปิด Cloudflare Tunnel แล้วใส่ URL ที่ได้ เพื่อควบคุมบอร์ดข้ามเครือข่าย WiFi\n'
                    '   ตัวอย่าง: https://abc-def-123.trycloudflare.com/cmu_aiot/smart_farm_dashboard/api/api.php'),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _ping,
                        icon: const Icon(Icons.wifi_find, size: 16),
                        label: const Text('ทดสอบเชื่อมต่อ', style: TextStyle(fontSize: 12)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _blue,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: ElevatedButton.icon(
                        onPressed: _fetchSensors,
                        icon: const Icon(Icons.sensors, size: 16),
                        label: const Text('ดึงค่าเซนเซอร์', style: TextStyle(fontSize: 12)),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: _green,
                          foregroundColor: Colors.white,
                          padding: const EdgeInsets.symmetric(vertical: 8),
                        ),
                      ),
                    ),
                  ],
                ),
                // Auto-poll toggle
                SwitchListTile(
                  dense: true,
                  title: Text('ดึงข้อมูลอัตโนมัติ (ทุก 8 วินาที)',
                      style: TextStyle(fontSize: 12, color: textSub)),
                  value: _autoPoll,
                  onChanged: _toggleAutoPoll,
                  activeThumbColor: _green,
                  contentPadding: EdgeInsets.zero,
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),

          // ── สถานะ ──────────────────────
          if (_lastStatus.isNotEmpty)
            Container(
              margin: const EdgeInsets.only(bottom: 10),
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              decoration: BoxDecoration(
                color: _svc.apiReachable
                    ? _green.withValues(alpha: 0.12)
                    : _red.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(8),
                border: Border.all(
                  color: _svc.apiReachable ? _green.withValues(alpha: 0.4) : _red.withValues(alpha: 0.3),
                ),
              ),
              child: Text(_lastStatus, style: TextStyle(
                  fontSize: 12, color: _svc.apiReachable ? _green : _red)),
            ),

          // ── Relay Control ──────────────────────
          _card(
            cardBg,
            child: Column(
              children: [
                Row(
                  children: [
                    const Icon(Icons.power_settings_new, color: _orange, size: 18),
                    const SizedBox(width: 6),
                    const Text('ควบคุมรีเลย์ (Pump/Valve)',
                        style: TextStyle(fontWeight: FontWeight.bold)),
                    const Spacer(),
                    _badge(
                      _isRelayOn ? '💧 ON' : '⚫ OFF',
                      _isRelayOn ? _green : Colors.grey,
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                // Big Toggle Button
                GestureDetector(
                  onTap: _commandLoading ? null : _toggleRelay,
                  child: AnimatedBuilder(
                    animation: _pulse,
                    builder: (_, child) => Transform.scale(
                      scale: _isRelayOn ? _pulse.value : 1.0,
                      child: child,
                    ),
                    child: Container(
                      width: 120,
                      height: 120,
                      decoration: BoxDecoration(
                        shape: BoxShape.circle,
                        color: _isRelayOn
                            ? _green.withValues(alpha: 0.15)
                            : Colors.grey.withValues(alpha: 0.1),
                        border: Border.all(
                          color: _isRelayOn ? _green : Colors.grey,
                          width: 3,
                        ),
                        boxShadow: _isRelayOn
                            ? [BoxShadow(color: _green.withValues(alpha: 0.35), blurRadius: 20, spreadRadius: 2)]
                            : [],
                      ),
                      child: _commandLoading
                          ? const Center(child: CircularProgressIndicator())
                          : Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.power_settings_new,
                                  size: 40,
                                  color: _isRelayOn ? _green : Colors.grey,
                                ),
                                const SizedBox(height: 4),
                                Text(
                                  _isRelayOn ? 'กำลังทำงาน' : 'หยุดทำงาน',
                                  style: TextStyle(
                                    fontSize: 11,
                                    fontWeight: FontWeight.bold,
                                    color: _isRelayOn ? _green : Colors.grey,
                                  ),
                                ),
                              ],
                            ),
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                  children: [
                    _quickBtn('เปิดปั๊ม', Icons.water_drop, _green, () async {
                      setState(() => _commandLoading = true);
                      await _svc.setRelay(true);
                      setState(() => _commandLoading = false);
                    }),
                    _quickBtn('ปิดปั๊ม', Icons.water_drop_outlined, _red, () async {
                      setState(() => _commandLoading = true);
                      await _svc.setRelay(false);
                      setState(() => _commandLoading = false);
                    }),
                  ],
                ),
              ],
            ),
          ),
          const SizedBox(height: 10),

          // ── Sensor Readings ──────────────────────
          if (reading != null) ...[
            _card(
              cardBg,
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      const Icon(Icons.sensors, color: _green, size: 18),
                      const SizedBox(width: 6),
                      const Text('ข้อมูลเซนเซอร์', style: TextStyle(fontWeight: FontWeight.bold)),
                      const Spacer(),
                      if (reading.cached)
                        _badge('📦 Cache', Colors.orange)
                      else if (reading.sensorOnline)
                        _badge('● Live', _green)
                      else
                        _badge('○ Offline', Colors.grey),
                    ],
                  ),
                  const SizedBox(height: 12),
                  // Grid ข้อมูล
                  GridView.count(
                    crossAxisCount: 2,
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    mainAxisSpacing: 8,
                    crossAxisSpacing: 8,
                    childAspectRatio: 2.2,
                    children: [
                      _sensorTile('🌡 อุณหภูมิ',
                          reading.temperature != null ? '${reading.temperature!.toStringAsFixed(1)} °C' : '-',
                          _orange, textSub),
                      _sensorTile('💧 ความชื้น',
                          reading.humidity != null ? '${reading.humidity!.toStringAsFixed(1)} %RH' : '-',
                          _blue, textSub),
                      _sensorTile('🌬 VPD',
                          reading.vpd != null ? '${reading.vpd!.toStringAsFixed(2)} kPa' : '-',
                          _green, textSub),
                      _sensorTile('🌅 แสง',
                          reading.light != null ? '${reading.light!.toInt()} lux' : '-',
                          _orange, textSub),
                      _sensorTile('⬆ ความกดอากาศ',
                          reading.pressure != null ? '${reading.pressure!.toStringAsFixed(1)} hPa' : '-',
                          Colors.purple, textSub),
                      _sensorTile('📡 สัญญาณ WiFi',
                          reading.rssiLabel, _blue, textSub),
                    ],
                  ),
                  if (reading.vpd != null) ...[
                    const SizedBox(height: 8),
                    Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: _green.withValues(alpha: 0.1),
                        borderRadius: BorderRadius.circular(6),
                      ),
                      child: Row(
                        children: [
                          const Icon(Icons.eco, color: _green, size: 14),
                          const SizedBox(width: 6),
                          Text('สภาพพืช: ${reading.vpdStatus}',
                              style: const TextStyle(fontSize: 12, color: _green, fontWeight: FontWeight.bold)),
                        ],
                      ),
                    ),
                  ],
                  if (reading.floatState != null) ...[
                    const SizedBox(height: 6),
                    _infoBox(isDark, '🪣 ลูกลอย: ${reading.floatState}'),
                  ],
                  const SizedBox(height: 6),
                  Text(
                    'อัปเดตล่าสุด: ${_formatTime(reading.timestamp)}',
                    style: TextStyle(fontSize: 10, color: textSub),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 10),
          ],

          // ── คู่มือ Cloudflare Tunnel ──────────────────────
          _card(
            cardBg,
            child: ExpansionTile(
              tilePadding: EdgeInsets.zero,
              title: const Row(
                children: [
                  Icon(Icons.help_outline, size: 16, color: Colors.orange),
                  SizedBox(width: 6),
                  Text('วิธีตั้งค่า Cloudflare Tunnel',
                      style: TextStyle(fontSize: 13, fontWeight: FontWeight.bold)),
                ],
              ),
              children: [
                _stepBox(isDark, '1', 'ดาวน์โหลด cloudflared บน Mac:\n'
                    'brew install cloudflared'),
                _stepBox(isDark, '2', 'รัน tunnel ชั่วคราว (ฟรี ไม่ต้อง login):\n'
                    'cloudflared tunnel --url http://localhost:80'),
                _stepBox(isDark, '3', 'รับ URL สาธารณะ เช่น:\n'
                    'https://abc-def.trycloudflare.com'),
                _stepBox(isDark, '4', 'ใส่ URL นั้นในช่องด้านบน ต่อท้ายด้วย:\n'
                    '/cmu_aiot/smart_farm_dashboard/api/api.php'),
                _stepBox(isDark, '5', 'กด "ทดสอบเชื่อมต่อ" แล้วกด "ดึงค่าเซนเซอร์"\n'
                    'จากนั้นสามารถสั่ง ON/OFF รีเลย์ข้ามเครือข่ายได้'),
                const SizedBox(height: 6),
                _infoBox(isDark,
                    '🔐 URL Cloudflare จะเปลี่ยนทุกครั้งที่รัน tunnel ใหม่\n'
                    '   สำหรับ URL คงที่ใช้ Cloudflare Zero Trust (free tier)'),
              ],
            ),
          ),
          const SizedBox(height: 20),
        ],
      ),
    );
  }

  // ─────────────── Widgets ───────────────
  Widget _card(Color bg, {required Widget child}) {
    return Container(
      padding: const EdgeInsets.all(14),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(12),
        boxShadow: [BoxShadow(color: Colors.black.withValues(alpha: 0.06), blurRadius: 6, offset: const Offset(0, 2))],
      ),
      child: child,
    );
  }

  Widget _badge(String label, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.15),
        borderRadius: BorderRadius.circular(10),
        border: Border.all(color: color.withValues(alpha: 0.5)),
      ),
      child: Text(label, style: TextStyle(fontSize: 10, color: color, fontWeight: FontWeight.bold)),
    );
  }

  Widget _sensorTile(String label, String value, Color color, Color textSub) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.08),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withValues(alpha: 0.2)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Text(label, style: TextStyle(fontSize: 10, color: textSub)),
          Text(value, style: TextStyle(fontSize: 13, color: color, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  Widget _quickBtn(String label, IconData icon, Color color, VoidCallback onTap) {
    return ElevatedButton.icon(
      onPressed: onTap,
      icon: Icon(icon, size: 16),
      label: Text(label, style: const TextStyle(fontSize: 12)),
      style: ElevatedButton.styleFrom(
        backgroundColor: color,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      ),
    );
  }

  Widget _infoBox(bool isDark, String text) {
    return Container(
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.blue.withValues(alpha: isDark ? 0.1 : 0.06),
        borderRadius: BorderRadius.circular(6),
        border: Border.all(color: Colors.blue.withValues(alpha: 0.2)),
      ),
      child: Text(text, style: TextStyle(
          fontSize: 10.5, color: isDark ? Colors.blue.shade200 : Colors.blue.shade700)),
    );
  }

  Widget _stepBox(bool isDark, String step, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 6),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Container(
            width: 22,
            height: 22,
            alignment: Alignment.center,
            decoration: BoxDecoration(
              color: _green.withValues(alpha: 0.2),
              shape: BoxShape.circle,
            ),
            child: Text(step, style: const TextStyle(fontSize: 11, color: _green, fontWeight: FontWeight.bold)),
          ),
          const SizedBox(width: 8),
          Expanded(
            child: Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: isDark ? Colors.white.withValues(alpha: 0.04) : Colors.grey.shade50,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.grey.withValues(alpha: 0.2)),
              ),
              child: Text(text,
                  style: TextStyle(fontSize: 11, fontFamily: 'monospace',
                      color: isDark ? Colors.white70 : Colors.black87)),
            ),
          ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final h = dt.hour.toString().padLeft(2, '0');
    final m = dt.minute.toString().padLeft(2, '0');
    final s = dt.second.toString().padLeft(2, '0');
    return '$h:$m:$s';
  }
}
