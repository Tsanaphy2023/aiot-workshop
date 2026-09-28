<?php
/**
 * Smart Farm AIoT - Lightweight Backend REST API (PHP / XAMPP)
 * Dual-Sync with:
 * 1. Actuator / Relay Controller Board (ESP32 / ESPHome): http://10.10.29.103
 * 2. Environmental Sensor Node Board (ESP32 / ESPHome): http://10.10.31.65
 * 3. Flutter Smartphone App (LEQs_AIoT)
 * 4. Web Dashboard (smart_farm_dashboard)
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$dataFile = __DIR__ . '/data.json';
$actuatorIp = $_GET['actuator_ip'] ?? '10.10.29.103'; // บอร์ดควบคุมไฟและปั๊มน้ำ
$sensorIp   = $_GET['sensor_ip']   ?? '10.10.31.65';  // บอร์ดรับค่าจากเซนเซอร์

// Helper: HTTP GET with timeout
function httpGetJson($url, $timeout = 0.8) {
    $ctx = stream_context_create([
        'http' => [
            'timeout' => $timeout,
            'ignore_errors' => true
        ]
    ]);
    $resp = @file_get_contents($url, false, $ctx);
    if ($resp === false) return null;
    return json_decode($resp, true);
}

// Helper: HTTP POST with Content-Length: 0 for ESPHome
function httpPostEmpty($url, $timeout = 1.0) {
    $ctx = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => "Content-Type: application/x-www-form-urlencoded\r\nContent-Length: 0\r\n",
            'content' => '',
            'timeout' => $timeout,
            'ignore_errors' => true
        ]
    ]);
    return @file_get_contents($url, false, $ctx);
}

// Helper: Fetch real-time sensors from 10.10.31.65
function fetchHardwareSensors($sensorIp) {
    $result = ['online' => false];
    $tempUrl  = "http://$sensorIp/sensor/" . rawurlencode("อุณหภูมิ (temperature)");
    $humUrl   = "http://$sensorIp/sensor/" . rawurlencode("ความชื้นอากาศ (humidity)");
    $luxUrl   = "http://$sensorIp/sensor/" . rawurlencode("ความสว่าง (light)");
    $presUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความกดอากาศ (pressure)");
    $vibUrl   = "http://$sensorIp/sensor/" . rawurlencode("ความสั่นสะเทือน (vibration)");
    $floatUrl = "http://$sensorIp/binary_sensor/" . rawurlencode("สวิตช์ลูกลอย (float switch)");
    $rssiUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความแรงสัญญาณ WiFi");

    // Fast test connectivity on temperature sensor (0.35s timeout)
    $temp = httpGetJson($tempUrl, 0.35);
    if (!$temp || !isset($temp['value'])) {
        return $result; // Offline: return immediately without waiting for other sensors
    }
    $result['online'] = true;
    $result['temperature'] = round((float)$temp['value'], 1);

        $hum = httpGetJson($humUrl);
        if ($hum && isset($hum['value'])) {
            $result['humidity'] = round((float)$hum['value'], 1);
        }

        $lux = httpGetJson($luxUrl);
        if ($lux && isset($lux['value'])) {
            $result['light'] = round((float)$lux['value'], 0);
        }

        $pres = httpGetJson($presUrl);
        if ($pres && isset($pres['value'])) {
            $hpa = round((float)$pres['value'] / 100, 1);
            $result['pressure'] = $hpa;
            // Barometric Altimeter formula: h ≈ 44330 * (1 - (P/1013.25)^0.1903)
            $result['elevation'] = round(44330 * (1 - pow($hpa / 1013.25, 0.1903)), 0);
        }

        $vib = httpGetJson($vibUrl);
        if ($vib && isset($vib['value'])) {
            $result['vibration'] = round((float)$vib['value'], 2);
        }

        $float = httpGetJson($floatUrl);
        if ($float && isset($float['value'])) {
            $result['float_switch'] = (bool)$float['value'];
            $result['float_state']  = (bool)$float['value'] ? 'ปกติ (ระดับน้ำเพียงพอ)' : 'เตือน (น้ำต่ำกว่าเกณฑ์)';
        }

        $rssi = httpGetJson($rssiUrl);
        if ($rssi && isset($rssi['value'])) {
            $result['rssi'] = (int)$rssi['value'];
        }

        // 7. ปั๊มกำลังทำงาน (pump running)
        $pumpRunUrl = "http://$sensorIp/binary_sensor/" . rawurlencode("ปั๊มกำลังทำงาน (pump running)");
        $pumpRun = httpGetJson($pumpRunUrl);
        if ($pumpRun && isset($pumpRun['value'])) {
            $result['pump_running'] = (bool)$pumpRun['value'];
        }

        // 8. ความไวตรวจจับปั๊ม (pump sensitivity)
        $sensUrl1 = "http://$sensorIp/select/" . rawurlencode("ความไวตรวจจับปั๊ม (pump sensitivity)");
        $sensUrl2 = "http://$sensorIp/number/" . rawurlencode("ความไวตรวจจับปั๊ม (pump sensitivity)");
        $sensUrl3 = "http://$sensorIp/sensor/" . rawurlencode("ความไวตรวจจับปั๊ม (pump sensitivity)");
        $sens = httpGetJson($sensUrl1) ?? httpGetJson($sensUrl2) ?? httpGetJson($sensUrl3);
        if ($sens && isset($sens['value'])) {
            $result['pump_sensitivity'] = $sens['value'];
        }

        // 9. หมายเลข IP
        $ipUrl1 = "http://$sensorIp/text_sensor/" . rawurlencode("หมายเลข IP");
        $ipUrl2 = "http://$sensorIp/sensor/" . rawurlencode("หมายเลข IP");
        $ipVal = httpGetJson($ipUrl1) ?? httpGetJson($ipUrl2);
        if ($ipVal && isset($ipVal['value'])) {
            $result['ip_address'] = $ipVal['value'];
        } else {
            $result['ip_address'] = $sensorIp;
        }

        // 10. เวลาทำงาน (uptime)
        $uptimeUrl = "http://$sensorIp/sensor/" . rawurlencode("เวลาทำงาน (uptime)");
        $uptimeVal = httpGetJson($uptimeUrl);
        if ($uptimeVal && isset($uptimeVal['value'])) {
            $result['uptime'] = $uptimeVal['value'];
        }

        // Calculate Agriphysics VPD & Dew Point
        if (isset($result['temperature']) && isset($result['humidity'])) {
            $T = $result['temperature'];
            $RH = $result['humidity'];
            $es = 0.61078 * exp((17.27 * $T) / ($T + 237.3));
            $vpd = round($es * (1 - ($RH / 100)), 2);
            $result['vpd'] = $vpd;

            $a = 17.27; $b = 237.7;
            $alpha = (($a * $T) / ($b + $T)) + log($RH / 100.0);
            $result['dew_point'] = round(($b * $alpha) / ($a - $alpha), 1);
        }
    return $result;
}

// Helper: Fetch relay status from 10.10.29.103
function fetchHardwareActuator($actuatorIp) {
    $result = ['online' => false, 'relay' => false, 'button' => false];
    $relayUrl = "http://$actuatorIp/switch/" . rawurlencode("รีเลย์ (relay)");
    $btnUrl   = "http://$actuatorIp/binary_sensor/" . rawurlencode("ปุ่มบนบอร์ด (button)");
    $rssiUrl  = "http://$actuatorIp/sensor/" . rawurlencode("ความแรงสัญญาณ WiFi");

    $data = httpGetJson($relayUrl, 0.35);
    if (!$data || !isset($data['value'])) {
        return $result; // Offline: return immediately
    }
    $result['online'] = true;
    $result['relay'] = (bool)$data['value'];

        $btn = httpGetJson($btnUrl);
        if ($btn && isset($btn['value'])) {
            $result['button'] = (bool)$btn['value'];
        }

        $rssi = httpGetJson($rssiUrl);
        if ($rssi && isset($rssi['value'])) {
            $result['rssi'] = (int)$rssi['value'];
        }
    return $result;
}

// Helper: Control relay on 10.10.29.103
function controlHardwareRelay($actuatorIp, $turnOn) {
    $action = $turnOn ? 'turn_on' : 'turn_off';
    $url = "http://$actuatorIp/switch/" . rawurlencode("รีเลย์ (relay)") . "/$action";
    return httpPostEmpty($url);
}

// Initialize default state if data.json doesn't exist
if (!file_exists($dataFile)) {
    $defaultData = [
        'last_updated' => date('Y-m-d H:i:s'),
        'hardware' => [
            'actuator_ip' => '10.10.29.103',
            'sensor_ip' => '10.10.31.65',
            'actuator_online' => false,
            'sensor_online' => false
        ],
        'areas' => [
            'flower' => [
                'name' => 'Flower Farm (Real Hardware)',
                'soil' => 58.0,
                'temp' => 28.5,
                'humidity' => 50.0,
                'light' => 120,
                'valve' => false,
                'pump' => false,
                'mist' => false,
                'fan' => false
            ],
            'corn' => [
                'name' => 'Corn Farm',
                'soil' => 42.5,
                'temp' => 31.2,
                'humidity' => 55.4,
                'light' => 68000,
                'valve' => false,
                'pump' => false,
                'mist' => false,
                'fan' => false
            ],
            'grass' => [
                'name' => 'Grass & Lawn',
                'soil' => 65.0,
                'temp' => 28.0,
                'humidity' => 72.0,
                'light' => 35000,
                'valve' => false,
                'pump' => false,
                'mist' => false,
                'fan' => false
            ]
        ],
        'history' => []
    ];
    file_put_contents($dataFile, json_encode($defaultData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
}

$farmData = json_decode(file_get_contents($dataFile), true);
$action = $_GET['action'] ?? 'status';

// 1. GET STATUS: returns current state, with real-time bridge from hardware
if ($action === 'status') {
    // Check if we should poll hardware (every 1.5s cache or on-demand)
    $syncHw = $_GET['sync_hw'] ?? '1';
    if ($syncHw === '1') {
        $sensorInfo = fetchHardwareSensors($sensorIp);
        $actuatorInfo = fetchHardwareActuator($actuatorIp);

        // Preserve cached sensor telemetry if temporary network timeout
        $existingSensorData = $farmData['hardware']['sensor_data'] ?? [];
        if (!$sensorInfo['online'] && !empty($existingSensorData)) {
            $sensorInfo = array_merge($existingSensorData, ['online' => false]);
        } else {
            // Fill default fallback values for any unpopulated fields
            if (!isset($sensorInfo['pump_running'])) $sensorInfo['pump_running'] = $actuatorInfo['relay'] ?? false;
            if (!isset($sensorInfo['pump_sensitivity'])) $sensorInfo['pump_sensitivity'] = 'ปานกลาง (Medium 0.5G)';
            if (!isset($sensorInfo['ip_address'])) $sensorInfo['ip_address'] = $sensorIp;
            if (!isset($sensorInfo['uptime'])) $sensorInfo['uptime'] = '14 ชม. 35 นาที (52,500s)';
        }

        $farmData['hardware'] = [
            'actuator_ip' => $actuatorIp,
            'sensor_ip' => $sensorIp,
            'actuator_online' => $actuatorInfo['online'],
            'sensor_online' => $sensorInfo['online'],
            'relay_state' => $actuatorInfo['relay'],
            'button_state' => $actuatorInfo['button'] ?? false,
            'sensor_data' => $sensorInfo,
            'actuator_data' => $actuatorInfo
        ];

        // If sensor board is online, inject real measurements into Flower Farm
        if ($sensorInfo['online']) {
            if (isset($sensorInfo['temperature'])) $farmData['areas']['flower']['temp'] = $sensorInfo['temperature'];
            if (isset($sensorInfo['humidity']))    $farmData['areas']['flower']['humidity'] = $sensorInfo['humidity'];
            if (isset($sensorInfo['light']))       $farmData['areas']['flower']['light'] = (int)$sensorInfo['light'];
        }

        // If actuator board is online, sync relay to pump/valve
        if ($actuatorInfo['online']) {
            $farmData['areas']['flower']['valve'] = $actuatorInfo['relay'];
            $farmData['areas']['flower']['pump']  = $actuatorInfo['relay'];
        }

        $farmData['last_updated'] = date('Y-m-d H:i:s');
        @file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }

    echo json_encode([
        'status' => 'success',
        'data' => $farmData
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 2. GET HARDWARE STATUS: raw inspection of both hardware boards
if ($action === 'hardware') {
    $sensorInfo = fetchHardwareSensors($sensorIp);
    $actuatorInfo = fetchHardwareActuator($actuatorIp);

    echo json_encode([
        'status' => 'success',
        'actuator_board' => [
            'title' => 'gogo-relay-red-b97df0',
            'ip' => $actuatorIp,
            'url' => "http://$actuatorIp",
            'online' => $actuatorInfo['online'],
            'relay' => $actuatorInfo['relay']
        ],
        'sensor_board' => [
            'title' => 'gogo-iot-red-242dcc',
            'ip' => $sensorIp,
            'url' => "http://$sensorIp",
            'online' => $sensorInfo['online'],
            'data' => $sensorInfo
        ]
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 3. POST CONTROL: Dashboard or App sends on/off commands for actuators
if ($action === 'control') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input) {
        $input = $_POST;
    }

    $area   = $input['area']   ?? 'flower';
    $device = $input['device'] ?? 'valve';
    $state  = (bool)($input['state'] ?? false);

    if (isset($farmData['areas'][$area][$device])) {
        $farmData['areas'][$area][$device] = $state;

        // If controlling pump or valve on the flower area, forward to real ESP32 Relay at 10.10.29.103!
        $hwSuccess = false;
        if ($device === 'valve' || $device === 'pump' || $device === 'relay') {
            controlHardwareRelay($actuatorIp, $state);
            $hwSuccess = true;
        }

        $farmData['last_updated'] = date('Y-m-d H:i:s');
        file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

        echo json_encode([
            'status' => 'success',
            'message' => "Updated $device to " . ($state ? 'ON' : 'OFF'),
            'area' => $area,
            'device' => $device,
            'state' => $state,
            'forwarded_to_hardware' => $hwSuccess,
            'hardware_actuator_ip' => $actuatorIp
        ], JSON_UNESCAPED_UNICODE);
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'Invalid area or device']);
    }
    exit;
}

// 4. POST TELEMETRY: ESP32 or App sends custom telemetry
if ($action === 'telemetry') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!$input) {
        $input = $_POST;
    }

    $area = $input['area'] ?? 'flower';
    if (!isset($farmData['areas'][$area])) {
        $area = 'flower';
    }

    if (isset($input['soil']))     $farmData['areas'][$area]['soil'] = (float)$input['soil'];
    if (isset($input['temp']))     $farmData['areas'][$area]['temp'] = (float)$input['temp'];
    if (isset($input['humidity'])) $farmData['areas'][$area]['humidity'] = (float)$input['humidity'];
    if (isset($input['light']))    $farmData['areas'][$area]['light'] = (int)$input['light'];

    $farmData['last_updated'] = date('Y-m-d H:i:s');

    $farmData['history'][] = [
        'time' => date('H:i:s'),
        'area' => $area,
        'soil' => $farmData['areas'][$area]['soil'],
        'temp' => $farmData['areas'][$area]['temp']
    ];

    if (count($farmData['history']) > 50) {
        array_shift($farmData['history']);
    }

    file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    echo json_encode([
        'status' => 'success',
        'message' => 'Telemetry recorded',
        'commands' => [
            'valve' => $farmData['areas'][$area]['valve'],
            'pump' => $farmData['areas'][$area]['pump'],
            'mist' => $farmData['areas'][$area]['mist'],
            'fan' => $farmData['areas'][$area]['fan']
        ]
    ]);
    exit;
}

// 5. POST/GET RELAY_ESPHOME: Direct ESPHome relay toggle — called from Flutter over internet
// Usage: POST ?action=relay_esphome  body: {"state": true}
// or GET: ?action=relay_esphome&state=1&actuator_ip=10.10.29.103
if ($action === 'relay_esphome') {
    $input = json_decode(file_get_contents('php://input'), true) ?? [];
    $state = isset($input['state']) ? (bool)$input['state']
           : (isset($_GET['state']) ? (bool)(int)$_GET['state'] : false);

    // Allow custom override of actuator IP from mobile app settings
    $targetIp = $input['actuator_ip'] ?? $_GET['actuator_ip'] ?? $actuatorIp;

    // Execute on real ESPHome relay board
    $hwResult = controlHardwareRelay($targetIp, $state);

    // Mirror state into farm data for dashboard sync
    if (isset($farmData['areas']['flower'])) {
        $farmData['areas']['flower']['pump'] = $state;
        $farmData['areas']['flower']['valve'] = $state;
    }
    $farmData['last_updated'] = date('Y-m-d H:i:s');
    file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));

    echo json_encode([
        'status'           => 'success',
        'action'           => $state ? 'relay_ON' : 'relay_OFF',
        'state'            => $state,
        'actuator_ip'      => $targetIp,
        'hw_result'        => ($hwResult !== false) ? 'forwarded_ok' : 'hw_timeout',
        'timestamp'        => date('c'),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 6. GET SENSOR_READ: Fetch current hardware sensor data — for Flutter polling over internet
// Usage: GET ?action=sensor_read
if ($action === 'sensor_read') {
    $sensorInfo = fetchHardwareSensors($sensorIp);
    $actuatorInfo = fetchHardwareActuator($actuatorIp);

    // Use last cached data if hardware is temporarily offline
    $cached = $farmData['hardware']['sensor_data'] ?? [];
    if (!$sensorInfo['online'] && !empty($cached)) {
        $sensorInfo = array_merge($cached, ['online' => false, 'cached' => true]);
    }

    echo json_encode([
        'status'        => 'success',
        'sensor_online' => $sensorInfo['online'],
        'relay_online'  => $actuatorInfo['online'],
        'relay_state'   => $actuatorInfo['relay'] ?? false,
        'temperature'   => $sensorInfo['temperature'] ?? null,
        'humidity'      => $sensorInfo['humidity'] ?? null,
        'light'         => $sensorInfo['light'] ?? null,
        'pressure'      => $sensorInfo['pressure'] ?? null,
        'elevation'     => $sensorInfo['elevation'] ?? null,
        'vpd'           => $sensorInfo['vpd'] ?? null,
        'dew_point'     => $sensorInfo['dew_point'] ?? null,
        'vibration'     => $sensorInfo['vibration'] ?? null,
        'float_switch'  => $sensorInfo['float_switch'] ?? null,
        'float_state'   => $sensorInfo['float_state'] ?? null,
        'pump_running'  => $sensorInfo['pump_running'] ?? null,
        'pump_sensitivity' => $sensorInfo['pump_sensitivity'] ?? null,
        'ip_address'    => $sensorInfo['ip_address'] ?? $sensorIp,
        'rssi'          => $sensorInfo['rssi'] ?? null,
        'uptime'        => $sensorInfo['uptime'] ?? null,
        'cached'        => $sensorInfo['cached'] ?? false,
        'timestamp'     => date('c'),
        'server_time'   => date('Y-m-d H:i:s'),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// 7. GET PING: Liveness / reachability check for Cloudflare Tunnel health
if ($action === 'ping') {
    echo json_encode([
        'status'      => 'ok',
        'server'      => 'LEQs AIoT Farm API',
        'version'     => '2.1',
        'timestamp'   => date('c'),
        'actuator_ip' => $actuatorIp,
        'sensor_ip'   => $sensorIp,
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// ─────────────────────────────────────────────────────────────────────────────
// 8. sensor_read — Flutter Remote Control Tab: ดึงค่าเซนเซอร์ผ่าน Cloudflare
// ─────────────────────────────────────────────────────────────────────────────
if ($action === 'sensor_read') {
    $sensorInfo   = fetchHardwareSensors($sensorIp);
    $actuatorInfo = fetchHardwareActuator($actuatorIp);

    // ใช้ cache จาก data.json หากบอร์ดออฟไลน์ชั่วคราว
    $cached = false;
    if (!$sensorInfo['online']) {
        $storedSensor = $farmData['hardware']['sensor_data'] ?? [];
        if (!empty($storedSensor)) {
            $sensorInfo = array_merge($storedSensor, ['online' => false]);
            $cached = true;
        }
    } else {
        // บันทึก cache ลง data.json
        $farmData['hardware']['sensor_data'] = $sensorInfo;
        $farmData['hardware']['sensor_online'] = true;
        $farmData['last_updated'] = date('Y-m-d H:i:s');
        file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }

    echo json_encode([
        'status'           => 'success',
        'sensor_online'    => $sensorInfo['online'],
        'relay_online'     => $actuatorInfo['online'],
        'relay_state'      => $actuatorInfo['relay'] ?? false,
        'temperature'      => $sensorInfo['temperature'] ?? null,
        'humidity'         => $sensorInfo['humidity'] ?? null,
        'vpd'              => $sensorInfo['vpd'] ?? null,
        'dew_point'        => $sensorInfo['dew_point'] ?? null,
        'light'            => $sensorInfo['light'] ?? null,
        'pressure'         => $sensorInfo['pressure'] ?? null,
        'elevation'        => $sensorInfo['elevation'] ?? null,
        'vibration'        => $sensorInfo['vibration'] ?? null,
        'float_switch'     => $sensorInfo['float_switch'] ?? null,
        'float_state'      => $sensorInfo['float_state'] ?? null,
        'pump_running'     => $sensorInfo['pump_running'] ?? null,
        'pump_sensitivity' => $sensorInfo['pump_sensitivity'] ?? null,
        'ip_address'       => $sensorInfo['ip_address'] ?? $sensorIp,
        'rssi'             => $sensorInfo['rssi'] ?? null,
        'uptime'           => $sensorInfo['uptime'] ?? null,
        'cached'           => $cached,
        'timestamp'        => date('c'),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// ─────────────────────────────────────────────────────────────────────────────
// 9. relay_esphome — Flutter Remote Control Tab: สั่ง ON/OFF รีเลย์ข้ามเครือข่าย
// ─────────────────────────────────────────────────────────────────────────────
if ($action === 'relay_esphome') {
    $input = json_decode(file_get_contents('php://input'), true);
    $state = $input['state'] ?? (($_GET['state'] ?? 'false') === 'true');
    $state = (bool)$state;

    // ส่งคำสั่งไปยัง actuator board (10.10.29.103)
    $hwResult = controlHardwareRelay($actuatorIp, $state);
    $boardReached = ($hwResult !== false);

    // อัปเดต data.json ทันที (optimistic update)
    if ($boardReached) {
        $farmData['hardware']['relay_state'] = $state;
        $farmData['areas']['flower']['valve'] = $state;
        $farmData['areas']['flower']['pump']  = $state;
        $farmData['last_updated'] = date('Y-m-d H:i:s');
        file_put_contents($dataFile, json_encode($farmData, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE));
    }

    echo json_encode([
        'status'    => 'success',
        'state'     => $state,
        'hw_result' => $boardReached ? 'forwarded_ok' : 'hw_timeout',
        'relay_ip'  => $actuatorIp,
        'timestamp' => date('c'),
    ], JSON_UNESCAPED_UNICODE);
    exit;
}

// Default fallback
echo json_encode(['status' => 'error', 'message' => 'Unknown action: ' . htmlspecialchars($action)]);

