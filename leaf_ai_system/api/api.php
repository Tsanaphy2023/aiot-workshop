<?php
/**
 * Dual Backend API for Leaf AI Workshop
 * Apache / XAMPP PHP REST API
 */

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type, Authorization');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

$baseDir = dirname(__DIR__);
$venvPython = $baseDir . '/.venv/bin/python';
if (!file_exists($venvPython)) {
    $venvPython = 'python3';
}

$action = $_GET['action'] ?? $_POST['action'] ?? 'get_status';

function json_response($data, $code = 200) {
    http_response_code($code);
    echo json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
    exit;
}

// 1. GET STATUS
if ($action === 'get_status') {
    $crops = [
        'corn' => ['name' => 'ข้าวโพด (Corn)', 'classes' => ['Blight', 'Common_Rust', 'Gray_Leaf_Spot', 'Healthy'], 'total' => 3924],
        'potato' => ['name' => 'มันฝรั่ง (Potato)', 'classes' => ['Potato___Early_blight', 'Potato___Late_blight', 'Potato___healthy'], 'total' => 901],
        'orange' => ['name' => 'ส้ม (Orange)', 'classes' => ['orange', 'Ripe orange'], 'total' => 426],
        'mango' => ['name' => 'มะม่วง (Mango)', 'classes' => ['Green mango', 'Rotten Mango', 'Yellow mango'], 'total' => 240],
        'banana' => ['name' => 'กล้วย (Banana)', 'classes' => ['Green banana', 'Rotten banana', 'Yellow banana'], 'total' => 205],
        'coffee' => ['name' => 'กาแฟ (Coffee)', 'classes' => ['healthy', 'leaf_rust', 'phoma'], 'total' => 150],
        'all' => ['name' => 'รวมทุกพืช (All 18 Classes)', 'classes' => 18, 'total' => 5846]
    ];

    // Check existing splits
    $splitsDir = $baseDir . '/data/splits';
    $existingSplits = [];
    if (is_dir($splitsDir)) {
        foreach (scandir($splitsDir) as $item) {
            if ($item !== '.' && $item !== '..' && is_dir("$splitsDir/$item")) {
                $summaryFile = "$splitsDir/$item/split_summary.json";
                if (file_exists($summaryFile)) {
                    $existingSplits[$item] = json_decode(file_get_contents($summaryFile), true);
                } else {
                    $existingSplits[$item] = ['status' => 'split_created'];
                }
            }
        }
    }

    // Check existing checkpoints
    $ckptDir = $baseDir . '/outputs/checkpoints';
    $checkpoints = [];
    if (is_dir($ckptDir)) {
        foreach (glob("$ckptDir/*.pth") as $pth) {
            $checkpoints[] = [
                'filename' => basename($pth),
                'path' => $pth,
                'filesize_mb' => round(filesize($pth) / (1024 * 1024), 2),
                'modified' => date('Y-m-d H:i:s', filemtime($pth))
            ];
        }
    }

    // Check existing reports
    $reportsDir = $baseDir . '/outputs/reports';
    $reports = [];
    if (is_dir($reportsDir)) {
        foreach (glob("$reportsDir/*") as $rep) {
            $reports[] = [
                'filename' => basename($rep),
                'url' => 'outputs/reports/' . basename($rep),
                'modified' => date('Y-m-d H:i:s', filemtime($rep))
            ];
        }
    }

    // Check hardware
    $hwCheck = shell_exec("$venvPython -c \"import torch; print('CUDA' if torch.cuda.is_available() else ('Apple Silicon MPS' if torch.backends.mps.is_available() else 'CPU'))\"");
    $hardware = trim($hwCheck ?: 'CPU');

    json_response([
        'status' => 'online',
        'backend' => 'PHP ' . PHP_VERSION . ' / Apache XAMPP',
        'python' => trim(shell_exec("$venvPython --version 2>&1") ?: 'unknown'),
        'hardware' => $hardware,
        'crops' => $crops,
        'existing_splits' => $existingSplits,
        'checkpoints' => $checkpoints,
        'reports' => $reports
    ]);
}

// 2. SPLIT DATASET
if ($action === 'split') {
    $crop = escapeshellarg($_POST['crop'] ?? 'corn');
    $train_ratio = floatval($_POST['train_ratio'] ?? 0.70);
    $val_ratio = floatval($_POST['val_ratio'] ?? 0.15);
    $test_ratio = floatval($_POST['test_ratio'] ?? 0.15);
    $seed = intval($_POST['seed'] ?? 42);

    $cmd = sprintf(
        '%s %s/scripts/01_split_dataset.py --crop %s --train_ratio %.2f --val_ratio %.2f --test_ratio %.2f --seed %d 2>&1',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        $crop,
        $train_ratio,
        $val_ratio,
        $test_ratio,
        $seed
    );

    $output = shell_exec($cmd);
    $cropClean = trim($crop, "'\"");
    $summaryFile = "$baseDir/data/splits/$cropClean/split_summary.json";
    $summaryData = null;
    if (file_exists($summaryFile)) {
        $summaryData = json_decode(file_get_contents($summaryFile), true);
    }

    json_response([
        'status' => 'success',
        'output' => $output,
        'summary' => $summaryData
    ]);
}

// 3. START TRAINING
if ($action === 'train') {
    $crop = escapeshellarg($_POST['crop'] ?? 'corn');
    $backbone = escapeshellarg($_POST['backbone'] ?? 'mobilenet_v2');
    $epochs = intval($_POST['epochs'] ?? 10);
    $batch_size = intval($_POST['batch_size'] ?? 32);
    $lr = floatval($_POST['lr'] ?? 0.001);

    $logFile = "$baseDir/outputs/logs/train_active.log";
    $pidFile = "$baseDir/outputs/logs/train_active.pid";

    // Run in background
    $cmd = sprintf(
        '%s %s/scripts/02_train.py --crop %s --backbone %s --epochs %d --batch_size %d --lr %f > %s 2>&1 & echo $!',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        $crop,
        $backbone,
        $epochs,
        $batch_size,
        $lr,
        escapeshellarg($logFile)
    );

    $pid = trim(shell_exec($cmd));
    file_put_contents($pidFile, $pid);

    json_response([
        'status' => 'started',
        'pid' => $pid,
        'crop' => trim($crop, "'\""),
        'backbone' => trim($backbone, "'\""),
        'epochs' => $epochs,
        'log_file' => 'outputs/logs/train_active.log'
    ]);
}

// 4. CHECK TRAINING STATUS
if ($action === 'train_status') {
    $logFile = "$baseDir/outputs/logs/train_active.log";
    $pidFile = "$baseDir/outputs/logs/train_active.pid";

    $isRunning = false;
    $pid = null;

    if (file_exists($pidFile)) {
        $pid = trim(file_get_contents($pidFile));
        if ($pid) {
            $check = trim(shell_exec("ps -p $pid -o pid="));
            $isRunning = ($check === $pid);
        }
    }

    $logContent = '';
    if (file_exists($logFile)) {
        $lines = file($logFile);
        $lastLines = array_slice($lines, -35);
        $logContent = implode('', $lastLines);
    }

    json_response([
        'running' => $isRunning,
        'pid' => $pid,
        'log' => $logContent
    ]);
}

// 5. EVALUATE MODEL
if ($action === 'evaluate') {
    $checkpoint = $_POST['checkpoint'] ?? '';
    if (!$checkpoint || !file_exists($checkpoint)) {
        // Fallback to first available checkpoint
        $files = glob("$baseDir/outputs/checkpoints/*_best.pth");
        if ($files) {
            $checkpoint = $files[0];
        } else {
            json_response(['status' => 'error', 'message' => 'No checkpoint found to evaluate.'], 400);
        }
    }

    $cmd = sprintf(
        '%s %s/scripts/03_evaluate.py --checkpoint %s 2>&1',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        escapeshellarg($checkpoint)
    );

    $output = shell_exec($cmd);

    // Find generated reports
    $reports = [];
    foreach (glob("$baseDir/outputs/reports/*_test_report.json") as $rf) {
        $reports[] = json_decode(file_get_contents($rf), true);
    }

    json_response([
        'status' => 'success',
        'output' => $output,
        'reports' => $reports
    ]);
}

// 6. PREDICT
if ($action === 'predict') {
    $checkpoint = $_POST['checkpoint'] ?? '';
    if (!$checkpoint || !file_exists($checkpoint)) {
        $files = glob("$baseDir/outputs/checkpoints/*_best.pth");
        if ($files) {
            $checkpoint = $files[0];
        } else {
            json_response(['status' => 'error', 'message' => 'No trained checkpoint found.'], 400);
        }
    }

    $imagePath = '';
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $uploadDir = "$baseDir/outputs/uploads";
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0777, true);
        }
        $filename = 'upload_' . time() . '_' . basename($_FILES['image']['name']);
        $imagePath = "$uploadDir/$filename";
        move_uploaded_file($_FILES['image']['tmp_name'], $imagePath);
    } elseif (!empty($_POST['image_path'])) {
        $imagePath = $_POST['image_path'];
    }

    if (!$imagePath || !file_exists($imagePath)) {
        json_response(['status' => 'error', 'message' => 'Image file not provided or not found.'], 400);
    }

    $cmd = sprintf(
        '%s %s/scripts/04_predict.py --checkpoint %s --image %s --json 2>&1',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        escapeshellarg($checkpoint),
        escapeshellarg($imagePath)
    );

    $raw = shell_exec($cmd);
    // Find json substring in output
    $jsonStart = strpos($raw, '{');
    $jsonEnd = strrpos($raw, '}');
    $parsed = null;
    if ($jsonStart !== false && $jsonEnd !== false) {
        $jsonStr = substr($raw, $jsonStart, $jsonEnd - $jsonStart + 1);
        $parsed = json_decode($jsonStr, true);
    }

    json_response([
        'status' => 'success',
        'result' => $parsed,
        'raw_output' => $raw
    ]);
}

// 7. GET SAMPLE IMAGES
if ($action === 'get_sample_images') {
    $rawDir = dirname($baseDir) . '/leaf workshop';
    $samples = [];
    $crops = ['corn_dataset', 'coffee_dataset', 'potato_dataset', 'BANANA', 'MANGO', 'ORANGE'];

    foreach ($crops as $c) {
        $cropPath = "$rawDir/$c";
        if (is_dir($cropPath)) {
            foreach (scandir($cropPath) as $sub) {
                if ($sub !== '.' && $sub !== '..' && is_dir("$cropPath/$sub")) {
                    $files = glob("$cropPath/$sub/*.jpg");
                    if (!empty($files)) {
                        $f = $files[0];
                        $rel = '../leaf%20workshop/' . rawurlencode($c) . '/' . rawurlencode($sub) . '/' . rawurlencode(basename($f));
                        $samples[] = [
                            'crop' => $c,
                            'class' => $sub,
                            'filename' => basename($f),
                            'path' => $f,
                            'url' => $rel
                        ];
                    }
                }
            }
        }
    }

    json_response([
        'status' => 'success',
        'samples' => $samples
    ]);
}

// 8. EXPORT MODEL
if ($action === 'export') {
    $checkpoint = $_POST['checkpoint'] ?? '';
    if (!$checkpoint || !file_exists($checkpoint)) {
        $files = glob("$baseDir/outputs/checkpoints/*_best.pth");
        if ($files) {
            $checkpoint = $files[0];
        } else {
            json_response(['status' => 'error', 'message' => 'No checkpoint found to export.'], 400);
        }
    }

    $cmd = sprintf(
        '%s %s/models/export.py --checkpoint %s 2>&1',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        escapeshellarg($checkpoint)
    );

    $output = shell_exec($cmd);
    $exported = [];
    foreach (glob("$baseDir/outputs/exported/*") as $ef) {
        $exported[] = [
            'filename' => basename($ef),
            'filesize_mb' => round(filesize($ef) / (1024 * 1024), 2),
            'url' => 'outputs/exported/' . basename($ef)
        ];
    }

    json_response([
        'status' => 'success',
        'output' => $output,
        'exported_files' => $exported
    ]);
// 9. OBJECT DETECTION & BOUNDING BOXES
if ($action === 'detect_bounding_boxes') {
    $imagePath = '';
    if (isset($_FILES['image']) && $_FILES['image']['error'] === UPLOAD_ERR_OK) {
        $uploadDir = "$baseDir/outputs/uploads";
        if (!is_dir($uploadDir)) {
            mkdir($uploadDir, 0777, true);
        }
        $filename = 'det_upload_' . time() . '_' . basename($_FILES['image']['name']);
        $imagePath = "$uploadDir/$filename";
        move_uploaded_file($_FILES['image']['tmp_name'], $imagePath);
    } elseif (!empty($_POST['image_path'])) {
        $imagePath = $_POST['image_path'];
    }

    if (!$imagePath || !file_exists($imagePath)) {
        json_response(['status' => 'error', 'message' => 'Image file not provided or not found.'], 400);
    }

    $crop = $_POST['crop'] ?? 'auto';
    $conf = floatval($_POST['conf_threshold'] ?? 0.35);
    $iou = floatval($_POST['iou_threshold'] ?? 0.45);

    $outDir = "$baseDir/outputs/detections";
    if (!is_dir($outDir)) {
        mkdir($outDir, 0777, true);
    }
    $annotatedName = 'annotated_' . time() . '_' . pathinfo($imagePath, PATHINFO_FILENAME) . '.jpg';
    $outputPath = "$outDir/$annotatedName";

    $cmd = sprintf(
        '%s %s/scripts/05_object_detection.py --image %s --crop %s --conf_threshold %f --iou_threshold %f --output_img %s --json 2>&1',
        escapeshellcmd($venvPython),
        escapeshellcmd($baseDir),
        escapeshellarg($imagePath),
        escapeshellarg($crop),
        $conf,
        $iou,
        escapeshellarg($outputPath)
    );

    $raw = shell_exec($cmd);
    $jsonStart = strpos($raw, '{');
    $jsonEnd = strrpos($raw, '}');
    $parsed = null;
    if ($jsonStart !== false && $jsonEnd !== false) {
        $jsonStr = substr($raw, $jsonStart, $jsonEnd - $jsonStart + 1);
        $parsed = json_decode($jsonStr, true);
    }

    if ($parsed && !empty($parsed['annotated_image_filename'])) {
        $parsed['annotated_image_url'] = 'outputs/detections/' . $parsed['annotated_image_filename'];
    }

    json_response([
        'status' => 'success',
        'result' => $parsed,
        'annotated_image_url' => 'outputs/detections/' . $annotatedName,
        'raw_output' => $raw
    ]);
}

json_response(['status' => 'error', 'message' => "Unknown action: $action"], 400);
