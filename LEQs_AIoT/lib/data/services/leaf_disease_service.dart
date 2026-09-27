import 'dart:async';
import '../models/farm_models.dart';

/// Vision Deep Learning Service: Leaf Disease Diagnostics
class LeafDiseaseService {
  final Map<String, LeafDiseaseDiagnosis> _diseaseDatabase = {
    'healthy': LeafDiseaseDiagnosis(
      diseaseId: 'healthy',
      diseaseNameTh: 'ใบพืชสุขภาพดี สมบูรณ์',
      diseaseNameEn: 'Healthy Plant Leaf',
      scientificName: 'Normal Cellular Physiology',
      confidence: 0.985,
      severity: 'ปกติ/สมบูรณ์ (Healthy)',
      symptomsTh: 'เนื้อใบมีสีเขียวสม่ำเสมอ ผิวใบเรียบ เส้นใบและปากใบสมบูรณ์ ไม่พบคราบเชื้อราหรือรอยกัดเจาะ',
      organicRemedies: [
        'รักษาระดับการให้น้ำและธาตุอาหารตามสมดุลปัจจุบัน',
        'ฉีดพ่นน้ำหมักชีวภาพหรือสาหร่ายทะเลสกัดเพื่อกระตุ้นภูมิคุ้มกันตามรอบปกติ',
      ],
      chemicalRemedies: ['ไม่จำเป็นต้องใช้สารเคมี'],
      preventionTips: [
        'รักษาการระบายอากาศในแปลงปลูกเพื่อลดความชื้นสะสมช่วงกลางคืน',
        'ตรวจวัดค่า VPD ให้อยู่ในช่วง 0.8 - 1.2 kPa สม่ำเสมอ',
      ],
      diagnosedAt: DateTime.now(),
    ),
    'powdery_mildew': LeafDiseaseDiagnosis(
      diseaseId: 'powdery_mildew',
      diseaseNameTh: 'โรคราแป้ง (Powdery Mildew)',
      diseaseNameEn: 'Powdery Mildew Fungus',
      scientificName: 'Podosphaera xanthii / Erysiphe cichoracearum',
      confidence: 0.948,
      severity: 'ระยะปานกลาง (Stage 2: Moderate)',
      symptomsTh: 'พบคราบผงสีขาวคล้ายแป้งกระจายทั่วผิวใบด้านบน ใบเริ่มม้วนงอและสังเคราะห์แสงลดลง',
      organicRemedies: [
        'พ่นเชื้อราปฏิปักษ์ ไตรโคเดอร์มา (Trichoderma harzianum) อัตรา 50 กรัมต่อน้ำ 20 ลิตร ในช่วงแดดร่ม',
        'ฉีดพ่นสารสกัดสะเดา หรือเบกกิ้งโซดา 1 ช้อนชา + น้ำมันพืช 1 ช้อนชา ผสมน้ำ 1 ลิตร',
      ],
      chemicalRemedies: [
        'กำมะถันผงชนิดละลายน้ำ (Wettable Sulfur 80% WG) อัตรา 30-40 กรัม/น้ำ 20 ลิตร',
        'ไดฟีโนโคนาโซล (Difenoconazole 25% EC) หรือ อะซ็อกซีสโตรบิน',
      ],
      preventionTips: [
        'หลีกเลี่ยงการให้น้ำพ่นฝอยโดนใบในช่วงเย็นหรือค่ำ',
        'ตัดแต่งใบด้านล่างของทรงพุ่มเพื่อให้ลมถ่ายเทสะดวก แสงส่องถึงโคนต้น',
      ],
      diagnosedAt: DateTime.now(),
    ),
    'early_blight': LeafDiseaseDiagnosis(
      diseaseId: 'early_blight',
      diseaseNameTh: 'โรคใบไหม้ / ใบจุดวงแหวน (Early Blight)',
      diseaseNameEn: 'Early Blight Fungus',
      scientificName: 'Alternaria solani',
      confidence: 0.923,
      severity: 'ระยะรุนแรง (Stage 3: Severe)',
      symptomsTh: 'แผลวงกลมหรือรูปไข่สีน้ำตาลเข้ม มีรอยวงซ้อนกันคล้ายเป้ายิงปืน ขอบแผลมีวงสีเหลืองล้อมรอบ',
      organicRemedies: [
        'ตัดใบที่เป็นโรครุนแรงนำไปเผาทำลายนอกแปลงทันที ห้ามทิ้งลงกองปุ๋ยหมัก',
        'ฉีดพ่นเชื้อแบคทีเรีย บาซิลลัส ซับทิลิส (Bacillus subtilis - BS) ทุก 5-7 วัน',
      ],
      chemicalRemedies: [
        'คอปเปอร์ออกซีคลอไรด์ (Copper oxychloride) หรือ แมนโคเซบ (Mancozeb 80% WP)',
        'โพรพิเนบ (Propineb 70% WP)',
      ],
      preventionTips: [
        'คลุมแปลงด้วยฟางหรือพลาสติกเพื่อป้องกันสปอร์เชื้อราจากดินกระเด็นโดนใบ',
        'ควบคุมความชื้นสัมพัทธ์ในแปลงไม่ให้แช่ขังเกิน 85% ติดต่อกันเกิน 6 ชั่วโมง',
      ],
      diagnosedAt: DateTime.now(),
    ),
    'rust': LeafDiseaseDiagnosis(
      diseaseId: 'rust',
      diseaseNameTh: 'โรคราสนิม (Rust Disease)',
      diseaseNameEn: 'Plant Rust Fungus',
      scientificName: 'Puccinia spp.',
      confidence: 0.895,
      severity: 'ระยะเริ่มต้น (Stage 1: Mild)',
      symptomsTh: 'ตุ่มนูนสีส้มอมน้ำตาลคล้ายผงสนิมเหล็กใต้ใบ ผิวใบด้านบนเริ่มมีจุดเหลืองซีดตรงกับตำแหน่งตุ่ม',
      organicRemedies: [
        'พ่นน้ำส้มควันไม้เจือจาง 1:200 ทุก 7 วัน',
        'ฉีดพ่นเชื้อราไตรโคเดอร์มาสดเคลือบผิวใบ',
      ],
      chemicalRemedies: [
        'โคลโรทาโลนิล (Chlorothalonil 75% WP)',
        'ทีบูโคนาโซล (Tebuconazole)',
      ],
      preventionTips: [
        'กำจัดวัชพืชรอบแปลงที่เป็นพืชอาศัยร่วมของสปอร์รา',
        'เสริมความแข็งแรงของผนังเซลล์พืชด้วยแคลเซียม-โบรอน และซิลิคอน',
      ],
      diagnosedAt: DateTime.now(),
    ),
    'thrips_pest': LeafDiseaseDiagnosis(
      diseaseId: 'thrips_pest',
      diseaseNameTh: 'รอยทำลายจากเพลี้ยไฟและไรแดง (Thrips & Mites)',
      diseaseNameEn: 'Thrips and Spider Mite Damage',
      scientificName: 'Scirtothrips dorsalis / Tetranychus urticae',
      confidence: 0.912,
      severity: 'ระยะปานกลาง (Stage 2: Moderate)',
      symptomsTh: 'ยอดหงิกงอ ปลายใบม้วนขึ้น ผิวใบด้านล่างมีคราบสีบรอนซ์เงิน หรือมีจุดสีขาวละเอียดคล้ายฝุ่นทราย',
      organicRemedies: [
        'พ่นเชื้อราบิวเวอเรีย (Beauveria bassiana) ผสมเชื้อราเมตาไรเซียม ช่วงเย็นความชื้นสูง',
        'ฉีดพ่นสารสกัดจากใบยาสูบ หรือน้ำหมึกสะเดาเข้มข้น',
      ],
      chemicalRemedies: [
        'สไปนีโทแรม (Spinetoram 12% SC)',
        'อะบาเมกติน (Abamectin 1.8% EC) หรือ อิมิดาโคลพริด (Imidacloprid)',
      ],
      preventionTips: [
        'ติดตั้งกับดักกาวเหนียวสีเหลืองและสีฟ้าบริเวณรอบแปลงปลูก',
        'เพิ่มความชื้นในอากาศด้วยระบบพ่นหมอก เพราะเพลี้ยไฟชอบสภาพอากาศแห้งจัด',
      ],
      diagnosedAt: DateTime.now(),
    ),
  };

  List<String> get availableDiseaseIds => _diseaseDatabase.keys.toList();

  /// Mock camera AI diagnosis with processing latency simulation
  Future<LeafDiseaseDiagnosis> diagnoseFromImage({String? targetDiseaseId}) async {
    // Simulate Edge Neural Inference time (180ms)
    await Future.delayed(const Duration(milliseconds: 280));

    final id = targetDiseaseId ?? 'powdery_mildew';
    final base = _diseaseDatabase[id] ?? _diseaseDatabase['healthy']!;

    return LeafDiseaseDiagnosis(
      diseaseId: base.diseaseId,
      diseaseNameTh: base.diseaseNameTh,
      diseaseNameEn: base.diseaseNameEn,
      scientificName: base.scientificName,
      confidence: base.confidence,
      severity: base.severity,
      symptomsTh: base.symptomsTh,
      organicRemedies: base.organicRemedies,
      chemicalRemedies: base.chemicalRemedies,
      preventionTips: base.preventionTips,
      diagnosedAt: DateTime.now(),
    );
  }

  LeafDiseaseDiagnosis getSampleDiagnosis(String id) {
    return _diseaseDatabase[id] ?? _diseaseDatabase['healthy']!;
  }
}
