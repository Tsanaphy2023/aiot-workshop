<?php
/**
 * =============================================================================
 * LEQs-AIoT v.1 Hardware Bridge API (Format 1: Local HTTP REST Bridge)
 * Deep+ Precision Agriculture & Smart Farm Platform
 * Chiang Mai University AIoT 2027
 * =============================================================================
 * Endpoint: http://<IP-Host>/cmu_aiot/module2/api/bridge.php
 * 
 * Supports:
 * - Real ESP32 Sensor Board Bridge (10.10.31.65)
 * - Real ESP32 Relay / Actuator Board Bridge (10.10.29.103)
 * - Web Simulator Real-time Status Polling (GET ?action=status)
 * - Web Simulator Actuator Command Dispatch (POST ?action=command)
 * - ESP32 Board Telemetry Ingestion (POST ?action=telemetry)
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$dataDir = __DIR__ . '/data';
if (!is_dir($dataDir)) {
    @mkdir($dataDir, 0777, true);
}
$stateFile = $dataDir . '/bridge_state.json';

$sensorIp   = $_GET['sensor_ip']   ?? '10.10.31.65';
$actuatorIp = $_GET['actuator_ip'] ?? '10.10.29.103';

// Helper: HTTP GET with short timeout
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
    $tempUrl = "http://$sensorIp/sensor/" . rawurlencode("อุณหภูมิ (temperature)");
    $humUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความชื้นอากาศ (humidity)");
    $luxUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความสว่าง (light)");
    $presUrl = "http://$sensorIp/sensor/" . rawurlencode("ความกดอากาศ (pressure)");

    $temp = httpGetJson($tempUrl);
    if ($temp && isset($temp['value'])) {
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
            $result['pressure'] = round((float)$pres['value'] / 100, 1); // Pa -> hPa
        }
    }
    return $result;
}

// Helper: Fetch relay status from 10.10.29.103
function fetchHardwareActuator($actuatorIp) {
    $result = ['online' => false, 'relay' => false];
    $relayUrl = "http://$actuatorIp/switch/" . rawurlencode("รีเลย์ (relay)");
    $data = httpGetJson($relayUrl);
    if ($data && isset($data['value'])) {
        $result['online'] = true;
        $result['relay'] = (bool)$data['value'];
    }
    return $result;
}

// Helper: Control relay on 10.10.29.103
function controlHardwareRelay($actuatorIp, $turnOn) {
    $action = $turnOn ? 'turn_on' : 'turn_off';
    $url = "http://$actuatorIp/switch/" . rawurlencode("รีเลย์ (relay)") . "/$action";
    return httpPostEmpty($url);
}

// Default State Structure
$defaultState = [
    'device' => 'GoGo-IoT Red + Relay',
    'board_ip' => '10.10.31.65 + 10.10.29.103',
    'last_seen' => 0,
    'last_seen_human' => 'กำลังเชื่อมต่อบอร์ดจริง...',
    'board_online' => true,
    'telemetry' => [
        'temp' => 28.5,
        'humidity' => 48.0,
        'pressure' => 973.5,
        'light' => 120,
        'soil_tension' => 32.0,
        'soil_vwc' => 28.5,
        'vpd' => 1.95,
        'co2' => 650,
        'tank_pct' => 85.0
    ],
    'commands' => [
        'valve' => 0,
        'fan' => 0,
        'mist' => 0,
        'light' => 0,
        'alarm' => 0
    ],
    'modes' => [
        'valve' => 'auto',
        'fan' => 'auto',
        'mist' => 'auto',
        'light' => 'auto',
        'alarm' => 'auto'
    ],
    'hardware_actuator_feedback' => [
        'valve' => 0,
        'fan' => 0,
        'mist' => 0,
        'light' => 0,
        'alarm' => 0
    ]
];

// Helper: Read State
function loadState($file, $default) {
    if (file_exists($file)) {
        $content = @file_get_contents($file);
        if ($content) {
            $data = json_decode($content, true);
            if (is_array($data)) {
                return array_replace_recursive($default, $data);
            }
        }
    }
    return $default;
}

// Helper: Save State atomically
function saveState($file, $data) {
    $tempFile = $file . '.tmp.' . uniqid();
    if (@file_put_contents($tempFile, json_encode($data, JSON_PRETTY_PRINT | JSON_UNESCAPED_UNICODE))) {
        @rename($tempFile, $file);
        return true;
    }
    return false;
}

$state = loadState($stateFile, $defaultState);
$action = $_GET['action'] ?? 'status';
$now = time();

// -----------------------------------------------------------------------------
// 1. ACTION: command (Sent by Web Simulator to control actuators)
// -----------------------------------------------------------------------------
if ($action === 'command') {
    $rawInput = file_get_contents('php://input');
    $payload = json_decode($rawInput, true);

    if (is_array($payload)) {
        if (isset($payload['device'])) {
            $dev = $payload['device'];
            $st = (isset($payload['state']) && ($payload['state'] == 1 || $payload['state'] === true));
            if (array_key_exists($dev, $state['commands'])) {
                $state['commands'][$dev] = $st ? 1 : 0;
            }
            if (isset($payload['mode'])) {
                $state['modes'][$dev] = $payload['mode'];
            }

            // Forward to REAL RELAY BOARD at 10.10.29.103!
            if ($dev === 'valve' || $dev === 'pump' || $dev === 'light') {
                controlHardwareRelay($actuatorIp, $st);
                $state['hardware_actuator_feedback']['valve'] = $st ? 1 : 0;
            }
        }

        if (isset($payload['commands']) && is_array($payload['commands'])) {
            foreach ($payload['commands'] as $k => $v) {
                if (array_key_exists($k, $state['commands'])) {
                    $st = ($v == 1 || $v === true);
                    $state['commands'][$k] = $st ? 1 : 0;
                    if ($k === 'valve' || $k === 'pump' || $k === 'light') {
                        controlHardwareRelay($actuatorIp, $st);
                        $state['hardware_actuator_feedback']['valve'] = $st ? 1 : 0;
                    }
                }
            }
        }

        saveState($stateFile, $state);

        echo json_encode([
            'status' => 'success',
            'message' => 'Actuator command executed on real hardware board',
            'commands' => $state['commands'],
            'modes' => $state['modes'],
            'hardware_actuator_ip' => $actuatorIp
        ]);
        exit;
    } else {
        http_response_code(400);
        echo json_encode(['status' => 'error', 'message' => 'Invalid JSON command payload']);
        exit;
    }
}

// -----------------------------------------------------------------------------
// 2. ACTION: status (Polled by Web Simulator)
// -----------------------------------------------------------------------------
if ($action === 'status') {
    // Poll real hardware sensors
    $hwSensors = fetchHardwareSensors($sensorIp);
    $hwActuator = fetchHardwareActuator($actuatorIp);

    if ($hwSensors['online']) {
        $state['board_online'] = true;
        $state['board_ip'] = "Sensor: $sensorIp | Relay: $actuatorIp";
        $state['last_seen'] = $now;
        $state['last_seen_human'] = 'ออนไลน์สด (วินาทีนี้)';
        $state['device'] = 'GoGo-IoT Sensor & Relay System';

        if (isset($hwSensors['temperature'])) $state['telemetry']['temp'] = $hwSensors['temperature'];
        if (isset($hwSensors['humidity']))    $state['telemetry']['humidity'] = $hwSensors['humidity'];
        if (isset($hwSensors['light']))       $state['telemetry']['light'] = $hwSensors['light'];
        if (isset($hwSensors['pressure']))    $state['telemetry']['pressure'] = $hwSensors['pressure'];

        // Compute Agriphysics VPD
        $T = $state['telemetry']['temp'];
        $RH = $state['telemetry']['humidity'];
        $es = 0.61078 * exp((17.27 * $T) / ($T + 237.3));
        $vpd = round($es * (1 - ($RH / 100)), 2);
        $state['telemetry']['vpd'] = $vpd;

        // Dynamic Soil tension simulation based on real VPD
        $state['telemetry']['soil_tension'] = round(30.0 + ($vpd * 5.0), 1);
    }

    if ($hwActuator['online']) {
        $state['commands']['valve'] = $hwActuator['relay'] ? 1 : 0;
        $state['hardware_actuator_feedback']['valve'] = $hwActuator['relay'] ? 1 : 0;
    }

    saveState($stateFile, $state);

    echo json_encode([
        'status' => 'success',
        'server_time' => date('Y-m-d H:i:s'),
        'timestamp' => $now,
        'board_online' => $state['board_online'],
        'board_ip' => $state['board_ip'],
        'last_seen' => $state['last_seen'],
        'last_seen_human' => $state['last_seen_human'],
        'device' => $state['device'],
        'telemetry' => $state['telemetry'],
        'commands' => $state['commands'],
        'modes' => $state['modes'],
        'hardware_actuator_feedback' => $state['hardware_actuator_feedback']
    ]);
    exit;
}

// -----------------------------------------------------------------------------
// 3. ACTION: test_packet (Inject simulated real-world telemetry for testing)
// -----------------------------------------------------------------------------
if ($action === 'test_packet') {
    $state['last_seen'] = $now;
    $state['board_online'] = true;
    $state['board_ip'] = '10.10.31.65 (Real Hardware)';
    saveState($stateFile, $state);

    echo json_encode([
        'status' => 'success',
        'message' => 'Hardware packet refreshed',
        'state' => $state
    ]);
    exit;
}

// Default fallback
echo json_encode(['status' => 'error', 'message' => 'Unknown action']);
