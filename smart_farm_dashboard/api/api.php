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
    $tempUrl = "http://$sensorIp/sensor/" . rawurlencode("อุณหภูมิ (temperature)");
    $humUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความชื้นอากาศ (humidity)");
    $luxUrl  = "http://$sensorIp/sensor/" . rawurlencode("ความสว่าง (light)");
    $presUrl = "http://$sensorIp/sensor/" . rawurlencode("ความกดอากาศ (pressure)");
    $rssiUrl = "http://$sensorIp/sensor/" . rawurlencode("ความแรงสัญญาณ WiFi");

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

        $rssi = httpGetJson($rssiUrl);
        if ($rssi && isset($rssi['value'])) {
            $result['rssi'] = (int)$rssi['value'];
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

        $farmData['hardware'] = [
            'actuator_ip' => $actuatorIp,
            'sensor_ip' => $sensorIp,
            'actuator_online' => $actuatorInfo['online'],
            'sensor_online' => $sensorInfo['online'],
            'relay_state' => $actuatorInfo['relay']
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

// Default fallback
echo json_encode(['status' => 'error', 'message' => 'Unknown action']);
