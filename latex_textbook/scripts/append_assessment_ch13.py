"""
Integrate all 19 quiz questions into ch13_yolo11_edge_ai_vision_manual.tex
"""

from pathlib import Path

CH13_PATH = Path("/Applications/XAMPP/xamppfiles/htdocs/cmu_aiot/latex_textbook/chapters/ch13_yolo11_edge_ai_vision_manual.tex")

assessment_latex = r"""
\section{คลังแบบทดสอบประเมินสมรรถนะการเรียนรู้และเฉลยเชิงวิเคราะห์}
\label{sec:ch13_assessment_bank}

เพื่อเป็นการประเมินผลสัมฤทธิ์ทางการเรียนรู้ของผู้เข้ารับการอบรมตามกรอบมาตรฐานสมรรถนะวิชาชีพ (Competency-Based Assessment) ด้านวิทยาการคอมพิวเตอร์วิทัศน์และระบบคัดแยกอัจฉริยะบนสายพานลำเลียง จึงได้รวบรวมแบบทดสอบปรนัยจำนวน 19 ข้อ พร้อมเฉลยเชิงวิเคราะห์ทางวิชาการและวิศวกรรม เพื่อใช้เป็นเกณฑ์มาตรฐานในการวัดผลการเรียนรู้ ดังปรากฏรายละเอียดในแต่ละหมวดวิชา

\subsection{หมวดที่ 1 มโนทัศน์พื้นฐานด้านภาพดิจิทัลและคอมพิวเตอร์วิทัศน์}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 1 หัวใจสำคัญเบื้องหลังภาพถ่ายที่คอมพิวเตอร์มองเห็น}}, breakable]
\textbf{คำถาม} หัวใจสำคัญเบื้องหลังภาพถ่ายที่คอมพิวเตอร์มองเห็น คือโครงสร้างข้อมูลในข้อใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item รหัสผ่านลับของผู้ใช้งาน
    \item เสียงดนตรีดิจิทัล
    \item ไฟล์เอกสาร Word
    \item \textbf{\checkmark\ ตารางตัวเลขพิกเซล (Grid of Numbers)}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ในทางวิทยาการคอมพิวเตอร์และปัญญาประดิษฐ์ คอมพิวเตอร์ไม่ได้รับรู้ภาพเป็นภาพศิลปะเหมือนสายตามนุษย์ แต่มองเห็นภาพเป็นเมทริกซ์หรือเทนเซอร์ของตัวเลข 2 มิติ หรือ 3 มิติ (2D/3D Tensor) ที่แต่ละพิกเซลเก็บค่าความสว่างตั้งแต่ 0 (มืดสนิท) ถึง 255 (สว่างสุด) โดยภาพสีแบบ RGB จะประกอบด้วยตารางตัวเลข 3 แชนเนลซ้อนทับกัน ตัวเลขเหล่านี้คือข้อมูลตั้งต้นที่อัลกอริทึมการเรียนรู้เชิงลึกนำไปคำนวณคอนโวลูชัน
\end{tcolorbox}

\subsection{หมวดที่ 2 การจัดการชุดข้อมูลภาพและแพลตฟอร์ม Roboflow}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 2 แพลตฟอร์มการจัดการข้อมูลภาพและ Data Augmentation}}, breakable]
\textbf{คำถาม} เว็บไซต์หรือแพลตฟอร์มใดที่ใช้ในการสร้างโปรเจกต์จัดการข้อมูลภาพ และทำ Data Augmentation ในบทเรียนนี้
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item \textbf{\checkmark\ Roboflow}
    \item Canva
    \item Google Drive
    \item Microsoft Word
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} Roboflow คือแพลตฟอร์มคลาวด์มาตรฐานสากลสำหรับนักพัฒนาคอมพิวเตอร์วิทัศน์ รองรับการอัปโหลดไฟล์ภาพ การตีกรอบระบุพิกัดวัตถุ (Annotation) การแปลงฟอร์แมตข้อมูล (YOLO, COCO, VOC) ตลอดจนการทำ Preprocessing และ Data Augmentation อย่างเป็นระบบ
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 3 การกำหนดชื่อคลาสสำหรับคัดแยกผลผลิต}}, breakable]
\textbf{คำถาม} ชื่อ Class สองกลุ่มหลักที่ใช้ในการคัดแยกผลผลิตปกติและผลผลิตเสียหายตามบทเรียนคือข้อใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item start / stop
    \item \textbf{\checkmark\ healthy / rotten}
    \item true / false
    \item open / close
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ในการฝึกสอนโมเดลคัดแยกเกรดและคุณภาพผลผลิตทางการเกษตร คลาสมาตรฐานที่นิยมใช้ในระดับสากล ได้แก่ \texttt{healthy} สำหรับผลผลิตสมบูรณ์ ผิวดี ได้มาตรฐาน และ \texttt{rotten} สำหรับผลผลิตที่มีตำหนิ รอยแตก หรือเน่าเสีย
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 4 ลักษณะการตีกรอบ Bounding Box ที่ผิดพลาด}}, breakable]
\textbf{คำถาม} ข้อใดคือลักษณะของการวาดกรอบ Bounding Box ที่ผิดพลาด และส่งผลให้ AI เรียนรู้ผิดเพี้ยนไปจากความเป็นจริง
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ตั้งชื่อ Class ให้ตรงกันทุกรูป
    \item แยกวาดกรอบแต่ละลูกกรณีที่ผลไม้วางอยู่ติดกัน
    \item \textbf{\checkmark\ วาดกรอบหลวมเกินไปจนติดฉากหลังสายพาน ทำให้ AI คิดว่าสายพานคือส่วนหนึ่งของแผล}
    \item วาดกรอบสี่เหลี่ยมให้ชิดขอบวัตถุพอดี
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} การตีกรอบหลวมเกินไปจะทำให้พิกเซลของฉากหลัง เช่น สีและลวดลายของสายพานลำเลียง ถูกรวมเข้าไปในคลาสรอยโรค โมเดลจะจดจำฟีเจอร์ของสายพานเป็นส่วนหนึ่งของแผลเน่า ก่อให้เกิดปัญหาโมเดลทำนายผิดพลาด (False Positive) เมื่อนำไปใช้งานจริง
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 5 การเพิ่มปริมาณภาพด้วย Data Augmentation}}, breakable]
\textbf{คำถาม} หากต้องการเพิ่มจำนวนภาพถ่ายโดยอัตโนมัติ เพื่อจำลองสภาพแสงและมุมมองที่หลากหลายบนสายพานโดยไม่ต้องออกไปถ่ายรูปใหม่ เราควรใช้ฟังก์ชันใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item Image Compression
    \item File Deletion
    \item Background Erase
    \item \textbf{\checkmark\ Data Augmentation}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} Data Augmentation คือกระบวนการเพิ่มความหลากหลายและปริมาณของชุดข้อมูลฝึกสอน โดยการจำลองการเปลี่ยนแปลงทางเรขาคณิตและสี เช่น การหมุนภาพ การกลับด้านซ้ายขวา การปรับค่าความสว่าง และการเพิ่มสัญญาณรบกวน ช่วยให้โมเดลมีความทนทานต่อสภาพแวดล้อมจริงในโรงงาน
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 6 ขั้นตอนหลังการตีกรอบภาพครบถ้วน}}, breakable]
\textbf{คำถาม} เมื่อเราวาดกรอบภาพครบถ้วน 100\% แล้ว สิ่งที่ระบบใน Roboflow จะปลดล็อกให้เราทำเป็นขั้นตอนถัดไปเพื่อเตรียมนำชุดข้อมูลไปใช้งานคือข้อใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ปุ่มแชร์หน้าจอไปยังโซเชียลมีเดีย
    \item ปุ่มลบโปรเจกต์ทิ้งทั้งหมด
    \item ปุ่มเปลี่ยนรหัสผ่านผู้ใช้งาน
    \item \textbf{\checkmark\ ปุ่ม Generate Dataset}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} เมื่อติดป้ายกำกับวัตถุครบทุกภาพ ระบบจะปลดล็อกขั้นตอน Generate เพื่อให้ผู้พัฒนาคลิกปุ่ม Generate Dataset สำหรับประมวลผล Preprocessing/Augmentation และสร้างเวอร์ชันชุดข้อมูลที่พร้อมดาวน์โหลดหรือดึงผ่าน REST API เข้าสู่ Google Colab
\end{tcolorbox}

\subsection{หมวดที่ 3 สถาปัตยกรรมโมเดล YOLO และการประเมินประสิทธิภาพ}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 7 วัตถุประสงค์ของ Object Detection บนสายพาน}}, breakable]
\textbf{คำถาม} เป้าหมายหลักของการใช้เทคโนโลยี Object Detection บนสายพานลำเลียงในโรงงานคือข้อใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item เพื่อบันทึกภาพเก็บไว้ทำรายงานประจำปี
    \item เพื่อปรับเปลี่ยนรูปร่างของผลไม้ให้ได้มาตรฐาน
    \item เพื่อเพิ่มความเร็วในการเคลื่อนที่ของสายพานให้เร็วขึ้น
    \item \textbf{\checkmark\ เพื่อตรวจจับและตีกรอบระบุตำแหน่งของผลผลิตหลายลูกพร้อมกัน เพื่อคัดแยกของเสียออกจากสายพาน}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} เทคโนโลยี Object Detection แตกต่างจาก Image Classification ตรงที่สามารถตรวจจับวัตถุได้หลายชิ้นพร้อมกันในหนึ่งเฟรม (Multi-object Detection) และส่งออกพิกัดจุดกึ่งกลาง $(x, y)$ ของผลผลิตทุกลูกบนสายพาน ทำให้ระบบนำพิกัดตำแหน่งไปสั่งการแขนกลหรือหัวพ่นลมได้อย่างตรงจุด
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 8 การเลือกรุ่นโมเดล YOLO สำหรับอุปกรณ์ฝังตัว}}, breakable]
\textbf{คำถาม} โมเดล YOLOv8 ขนาดใด ที่ถูกออกแบบมาให้มีขนาดเล็ก น้ำหนักเบา และมีความเร็วสูงสุด เหมาะสำหรับนำไปใช้กับกล้องติดสายพานความเร็วสูงหรือบอร์ดสมองกลขนาดเล็ก
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item YOLOv8x (Extra Large)
    \item YOLOv8m (Medium)
    \item \textbf{\checkmark\ YOLOv8n (Nano)}
    \item YOLOv8s (Small)
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ตระกูล YOLO โมเดลรุ่น Nano (n) มีจำนวนพารามิเตอร์ต่ำที่สุด (~3.2 ล้านพารามิเตอร์) และขนาดไฟล์เพียง ~6 MB จึงให้ค่าเวลาแฝงในการอนุมานผลสั้นที่สุด เหมาะสมที่สุดสำหรับการติดตั้งบนบอร์ดสมองกลฝังตัวที่มีทรัพยากรจำกัด
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 9 ไฟล์น้ำหนักที่ดีที่สุดจากการฝึกสอน}}, breakable]
\textbf{คำถาม} ไฟล์น้ำหนักที่ดีที่สุดที่ระบบการฝึกอบรม (Training) คัดเลือกและจัดเก็บไว้ให้โดยอัตโนมัติ เพื่อให้นำไปใช้ในการทดสอบจริง มีชื่อเรียกว่าอะไร
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item config.json
    \item yolov8n.pt
    \item \textbf{\checkmark\ best.pt}
    \item data.yaml
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ในระหว่างการฝึกสอน YOLO เฟรมเวิร์กจะทำการทดสอบบนชุด Validation ในทุก ๆ รอบ (Epoch) แล้วทำการบันทึกไฟล์น้ำหนักที่ให้ค่าความแม่นยำสูงสุดไว้ในชื่อ \texttt{best.pt} ส่วน \texttt{last.pt} คือไฟล์ของรอบสุดท้าย และ \texttt{data.yaml} คือไฟล์การตั้งค่าโครงสร้างข้อมูล
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 10 ความหมายและประโยชน์ของค่า Precision}}, breakable]
\textbf{คำถาม} ข้อใดคือความหมายและประโยชน์ของค่า Precision (ความแม่นยำ) ในการประเมินผล AI
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ความเร็วในการเปิดดูภาพซ้ำๆ ของ AI
    \item ขนาดความจุของไฟล์โมเดลหลังการเทรน
    \item มีผลเน่าทั้งหมด 100 ลูก AI ตรวจเจอครบกี่ลูก
    \item \textbf{\checkmark\ ทายว่าเน่า แล้วเน่าจริงกี่เปอร์เซ็นต์ (ช่วยป้องกันการตัดผลผลิตดีทิ้งโดยเปล่าประโยชน์)}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ค่า Precision คำนวณจากสูตร $\text{Precision} = TP / (TP + FP)$ บ่งชี้ว่าจากสิ่งที่ AI ทายว่าเป็นผลเน่าทั้งหมดนั้น มันเน่าจริงกี่เปอร์เซ็นต์ ประโยชน์คือช่วยควบคุมความผิดพลาดแบบ False Positive ป้องกันไม่ให้ระบบตีตราผลผลิตเกรดดีว่าเป็นผลเสียจนถูกคัดทิ้งโดยสูญเปล่า
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 11 ความหมายและประโยชน์ของค่า Recall}}, breakable]
\textbf{คำถาม} ข้อใดคือความหมายของค่า Recall (การเก็บตกครบ) ในการประเมินผล AI
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item การย้อนกลับไปแก้ไขภาพที่วาดกรอบผิดพลาด
    \item ความสามารถในการจดจำชื่อผู้ใช้งานระบบ
    \item การคำนวณต้นทุนค่าใช้จ่ายในการสร้างระบบ AI
    \item \textbf{\checkmark\ การตรวจสอบว่าผลเน่าทั้งหมดที่มี AI สามารถตรวจจับเจอครบถ้วนหรือไม่ เพื่อป้องกันผลเน่าหลุดรอดไปถึงมือลูกค้า}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ค่า Recall คำนวณจากสูตร $\text{Recall} = TP / (TP + FN)$ บ่งชี้ความครอบคลุมในการกวาดตรวจจับวัตถุเป้าหมายจริงทั้งหมด มีความสำคัญอย่างยิ่งในงานควบคุมคุณภาพสินค้า เพื่อรับประกันว่าไม่มีผลผลิตเน่าเสียหลุดรอดสายตา AI ออกไปสู่ตลาด
\end{tcolorbox}

\subsection{หมวดที่ 4 วิศวกรรมระบบฮาร์ดแวร์ Edge AI และบอร์ดเดี่ยว Raspberry Pi}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 12 บทบาทของคอมพิวเตอร์บอร์ดเดี่ยวในงาน Edge AI}}, breakable]
\textbf{คำถาม} อุปกรณ์ชิ้นใดทำหน้าที่เปรียบเสมือน สมองกลขนาดจิ๋ว ที่ติดตั้งหน้างานเพื่อรันระบบ AI ประมวลผลแบบ Edge Computing โดยไม่ต้องพึ่งพาอินเทอร์เน็ต
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item \textbf{\checkmark\ คอมพิวเตอร์บอร์ดเดี่ยว (เช่น Raspberry Pi)}
    \item เราเตอร์ไวไฟบ้าน
    \item เครื่องปริ้นเตอร์เอกสาร
    \item โทรศัพท์มือถือรุ่นเก่า
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} คอมพิวเตอร์บอร์ดเดี่ยว (Single-Board Computer: SBC) เช่น Raspberry Pi รวบรวมหน่วยประมวลผลกลาง แรม และพอร์ตเชื่อมต่อไว้บนบอร์ดเดียว สามารถติดตั้งระบบปฏิบัติการ Linux และรันโมเดล AI ในรูปแบบ Edge Computing ได้โดยอิสระโดยไม่ต้องเชื่อมต่ออินเทอร์เน็ต
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 13 หน้าที่หลักของ Raspberry Pi บนสายพานลำเลียง}}, breakable]
\textbf{คำถาม} ข้อใดอธิบายหน้าที่หลักของบอร์ด Raspberry Pi เมื่อนำมาติดตั้งใช้งานจริงบนสายพานลำเลียง
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item \textbf{\checkmark\ ทำหน้าที่รันโมเดลเพื่อทายภาพสด (Inference) ควบคุมรับส่งสัญญาณผ่าน GPIO และสั่งการกลไกคัดแยกที่หน้างาน}
    \item ทำหน้าที่พิมพ์ฉลากสินค้าและบาร์โค้ด
    \item ทำหน้าที่เป็นเครื่องแม่ข่ายสำหรับอัปโหลดคลิปวิดีโอขึ้น YouTube
    \item ทำหน้าที่เป็นแหล่งเก็บเงินสดของโรงงาน
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} Raspberry Pi หน้างานทำหน้าที่ครบวงจร ตั้งแต่การดึงสตรีมภาพสดจากกล้องมารันโมเดล YOLO ประมวลผลตำแหน่งพิกัดของผลเสีย และส่งสัญญาณไฟฟ้าลอจิกผ่านขา GPIO ไปควบคุมไดรเวอร์รีเลย์และวาล์วลมให้ทำงานสัมพันธ์กัน
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 14 บทบาทของขาพิน GPIO 40 ขา}}, breakable]
\textbf{คำถาม} ขาพิน GPIO 40 ขา บนบอร์ด Raspberry Pi มีบทบาทสำคัญอย่างไรเมื่อนำมาใช้ร่วมกับระบบสายพานคัดแยก
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item เป็นช่องระบายความร้อนออกจากตัวชิปประมวลผล
    \item เป็นช่องสำหรับเสียบสายชาร์จแบตเตอรี่สำรอง
    \item เป็นช่องเชื่อมต่อสัญญาณอินเทอร์เน็ตไร้สาย
    \item \textbf{\checkmark\ เป็นเส้นประสาทสั่งการที่รับสัญญาณจากเซนเซอร์ และส่งกระแสไฟฟ้าไปควบคุมกลไกภายนอก (เช่น หัวพ่นลมหรือรีเลย์)}
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} GPIO (General Purpose Input/Output) ทำหน้าที่เสมือนเส้นประสาทสั่งการที่แปลงผลการตัดสินใจทางซอฟต์แวร์ของ AI ให้กลายเป็นการกระทำทางกายภาพ เช่น การรับสัญญาณเมื่อผลผลิตมาถึงหน้ากล้อง และการจ่ายแรงดันไฟฟ้า 3.3V ไปทริกเกอร์รีเลย์ของหัวพ่นลม
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 15 กฎเหล็กการติดตั้งกล้องและระบบแสงสว่าง}}, breakable]
\textbf{คำถาม} กฎเหล็กข้อแรกในการติดตั้งกล้องและจัดสภาพแวดล้อมหน้างานให้ระบบ Vision ทำงานได้อย่างแม่นยำคือข้อใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ปล่อยให้แสงในโรงงานมืดสนิทเพื่อให้กล้องมองเห็นชัดขึ้น
    \item ต้องใช้แสงธรรมชาติจากดวงอาทิตย์ที่ส่องผ่านหน้าต่างเท่านั้น
    \item \textbf{\checkmark\ ต้องควบคุมแสงสว่างให้คงที่ (เช่น ใช้ตู้คุมแสงหรือไฟวงแหวน LED) ห้ามใช้แสงธรรมชาติที่เปลี่ยนไปมา}
    \item ขยับตำแหน่งกล้องขึ้นลงทุกๆ 1 ชั่วโมง
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} ในงาน Machine Vision แสงธรรมชาติมีความแปรปรวนสูงมากตามช่วงเวลาและสภาพอากาศ ซึ่งจะทำให้ค่าตัวเลขพิกเซลของภาพเปลี่ยนไปจน AI สับสน กฎเหล็กอันดับหนึ่งคือการตัดแสงภายนอกด้วยตู้ครอบแสง (Light Enclosure) และใช้แหล่งกำเนิดแสงประดิษฐ์ที่มีความเสถียรคงที่ 100%
\end{tcolorbox}

\subsection{หมวดที่ 5 การคำนวณทางฟิสิกส์ การควบคุม และการบริหารจัดการโครงการ}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 16 ตัวแปรทางกายภาพในการคำนวณจังหวะเวลาคัดแยก}}, breakable]
\textbf{คำถาม} ในขั้นตอนการสื่อสารกับนักพัฒนาเรื่อง จังหวะเวลาในการคัดแยก (Time Delay) ตัวแปรทางกายภาพใดบ้างที่นักพัฒนาต้องนำไปใช้คำนวณร่วมกับโค้ดเพื่อให้หัวพ่นลมทำงานได้แม่นยำเป๊ะ
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ถอดการ์ด MicroSD ออกแล้วใช้มือถือส่องแทน
    \item \textbf{\checkmark\ ระยะทางคงที่ระหว่างจุดตรวจจับ (กล้อง) กับจุดคัดแยก (หัวพ่นลม) หารด้วยความเร็วของสายพาน}
    \item ยี่ห้อของสมาร์ตโฟนของผู้จัดการโรงงาน
    \item อุณหภูมิและความชื้นสัมพัทธ์ในอากาศ
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} การซิงโครไนซ์เวลาใช้กฎการเคลื่อนที่เส้นตรงพื้นฐานทางฟิสิกส์ $t_{\text{delay}} = d / v$ โดยที่ $d$ คือระยะห่างระหว่างจุดศูนย์กลางภาพของกล้องไปยังหัวพ่นลม และ $v$ คือความเร็วเชิงเส้นของสายพาน การทราบตัวแปรนี้ช่วยให้โปรแกรมหน่วงเวลานับถอยหลังได้อย่างแม่นยำระดับมิลลิวินาที
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 17 เหตุผลทางวิศวกรรมในการเลือกใช้ Edge AI สำหรับโรงงานชุมชน}}, breakable]
\textbf{คำถาม} หากนักพัฒนาแนะนำให้ใช้สถาปัตยกรรมแบบ Edge AI สำหรับโรงงานชุมชน เหตุผลทางธุรกิจและวิศวกรรมข้อใดอธิบายได้ถูกต้องที่สุด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item เพราะเป็นระบบที่ไม่ต้องใช้กล้องถ่ายภาพและไม่มีการเขียนโปรแกรมใดๆ ทั้งสิ้น
    \item เพราะต้องใช้อินเทอร์เน็ตความเร็วสูงระดับ 10 Gbps เชื่อมต่อไปยังเซิร์ฟเวอร์ต่างประเทศตลอดเวลา
    \item \textbf{\checkmark\ เพราะช่วยประหยัดต้นทุนฮาร์ดแวร์ กินไฟต่ำ (~5W), ประมวลผลรวดเร็วที่หน้างานทันที และทำงานได้แม้อินเทอร์เน็ตล่ม}
    \item เพราะทำให้คอมพิวเตอร์ตั้งโต๊ะขนาดใหญ่ทำงานได้ช้าลง
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} สถาปัตยกรรม Edge AI ตอบโจทย์วิสาหกิจชุมชนและ SME ได้ดีที่สุด เพราะบอร์ดเดี่ยวกินไฟต่ำเพียง 5-15W มีต้นทุนอุปกรณ์สมเหตุสมผล ประมวลผลได้รวดเร็วโดยไม่มี Latency ของเครือข่าย และยังคงทำงานคัดแยกผลผลิตได้ต่อเนื่องแม้อินเทอร์เน็ตจะขัดข้อง
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 18 โครงสร้างระบบคัดแยกที่คุ้มค่าสำหรับ SME}}, breakable]
\textbf{คำถาม} ในฐานะผู้บริหารหรือผู้จัดการโครงการ หากต้องพูดคุยและสื่อสารโจทย์กับทีมนักพัฒนา เพื่อสร้างระบบคัดแยกอัตโนมัติในงบประมาณที่คุ้มค่าสำหรับ SME ควรเลือกโครงสร้างระบบแบบใด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ซื้อซูเปอร์คอมพิวเตอร์เซิร์ฟเวอร์ราคาหลักล้านมาตั้งไว้กลางไร่
    \item \textbf{\checkmark\ ใช้ระบบ Edge AI บนคอมพิวเตอร์บอร์ดเดี่ยว (Raspberry Pi) ร่วมกับกล้องและตู้คุมแสง ประมวลผลหน้างานแบบประหยัดพลังงาน (~5W) และสั่งการกลไกผ่าน GPIO}
    \item เขียนจดหมายส่งไปให้ต่างประเทศช่วยประมวลผล
    \item จ้างพนักงานมานั่งคัดแยกด้วยมือเหมือนเดิมแต่ให้ใส่เสื้อกาวน์
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} การลงทุนสร้างระบบคัดแยกด้วย Edge AI บนบอร์ดเดี่ยวร่วมกับกล้องและตู้คุมแสง ให้ผลตอบแทนการลงทุน (ROI) สูงสุดสำหรับ SME เนื่องจากควบคุมต้นทุนได้ง่าย บำรุงรักษาสะดวก และทำงานได้จริงในสภาพแวดล้อมหน้างาน
\end{tcolorbox}

\begin{tcolorbox}[colback=white, colframe=rbruNavy, title={\textbf{ข้อคำถามที่ 19 สรุปภาพรวมคอนเซปต์ระบบคัดแยกอัจฉริยะแบบองค์รวม}}, breakable]
\textbf{คำถาม} ข้อสรุปใดสะท้อนภาพรวมความเข้าใจเชิงคอนเซปต์ทั้งหมดของการทำระบบคัดแยกอัจฉริยะ (Smart Sorting System) ได้ถูกต้องสมบูรณ์ที่สุด
\begin{enumerate}[label=(\alph*), leftmargin=2em]
    \item ซื้อแขนกลหุ่นยนต์ราคาแพงโดยไม่ต้องใช้กล้องและไม่ต้องตั้งค่าแสง
    \item \textbf{\checkmark\ ควบคุมแสงและฉากหลังให้เสถียร $\rightarrow$ ใช้ Image Processing กรองขนาดและรูปทรง $\rightarrow$ ใช้ AI ตรวจจับตำหนิผิว $\rightarrow$ ประมวลผลด้วย Edge AI บนบอร์ดเดี่ยว และสั่งการกลไกผ่านพิน GPIO อย่างแม่นยำ}
    \item เขียนโค้ดสุ่มผลลัพธ์ $\rightarrow$ ติดตั้งกลางแจ้งโดยไม่ต้องมีหลังคา $\rightarrow$ รอให้ฝนตกแล้วปิดระบบ
    \item ถ่ายภาพด้วยมือถือ $\rightarrow$ โพสต์ลงโซเชียล $\rightarrow$ รอคนมากดไลค์แล้วค่อยคัดแยกผลไม้
\end{enumerate}
\tcblower
\textbf{เฉลยเชิงวิเคราะห์} นี่คือสายการผลิตอัจฉริยะที่ถูกต้องตามหลักวิศวกรรมแบบบูรณาการ เริ่มต้นจากการคุมสภาพแวดล้อมทางแสง $\rightarrow$ ใช้การประมวลผลภาพเบื้องต้นคัดกรองมิติภายนอก $\rightarrow$ ส่งต่อให้ AI วินิจฉัยรอยโรคระดับลึก $\rightarrow$ และประมวลผลสั่งการกลไกทางกายภาพผ่าน GPIO ได้อย่างแม่นยำสมบูรณ์แบบ
\end{tcolorbox}
"""

with open(CH13_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Replace or append before the end of chapter or after review questions
if r"\section{คลังแบบทดสอบประเมินสมรรถนะการเรียนรู้และเฉลยเชิงวิเคราะห์}" not in content:
    updated_content = content + "\n" + assessment_latex
    with open(CH13_PATH, "w", encoding="utf-8") as f:
        f.write(updated_content)
    print("✅ Appended Assessment Bank to Chapter 13 successfully!")
else:
    print("ℹ️ Assessment Bank already present in Chapter 13.")
