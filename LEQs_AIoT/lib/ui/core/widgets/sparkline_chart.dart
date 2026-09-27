import 'dart:math';
import 'package:flutter/material.dart';

class SparklineChart extends StatelessWidget {
  final List<double> data;
  final Color lineColor;
  final String title;
  final String unit;
  final double height;

  const SparklineChart({
    super.key,
    required this.data,
    required this.lineColor,
    required this.title,
    required this.unit,
    this.height = 140,
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    if (data.isEmpty) {
      return SizedBox(
        height: height,
        child: const Center(child: Text('กำลังโหลดข้อมูล...')),
      );
    }

    final double minVal = data.reduce(min);
    final double maxVal = data.reduce(max);
    final double latest = data.last;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                        overflow: TextOverflow.ellipsis,
                        maxLines: 1,
                      ),
                      const SizedBox(height: 2),
                      Row(
                        children: [
                          Text(
                            'ต่ำสุด: ${minVal.toStringAsFixed(1)}',
                            style: TextStyle(
                              color: isDark ? Colors.white54 : Colors.black54,
                              fontSize: 11,
                            ),
                          ),
                          const SizedBox(width: 8),
                          Text(
                            'สูงสุด: ${maxVal.toStringAsFixed(1)}',
                            style: TextStyle(
                              color: isDark ? Colors.white54 : Colors.black54,
                              fontSize: 11,
                            ),
                          ),
                        ],
                      ),
                    ],
                  ),
                ),
                const SizedBox(width: 8),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: lineColor.withValues(alpha: 0.12),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: lineColor.withValues(alpha: 0.25)),
                  ),
                  child: Text(
                    '${latest.toStringAsFixed(1)} $unit',
                    style: TextStyle(
                      color: lineColor,
                      fontWeight: FontWeight.bold,
                      fontSize: 13,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 10),
            SizedBox(
              height: height,
              width: double.infinity,
              child: CustomPaint(
                painter: _SparklinePainter(
                  data: data,
                  lineColor: lineColor,
                  isDark: isDark,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _SparklinePainter extends CustomPainter {
  final List<double> data;
  final Color lineColor;
  final bool isDark;

  _SparklinePainter({
    required this.data,
    required this.lineColor,
    required this.isDark,
  });

  @override
  void paint(Canvas canvas, Size size) {
    if (data.length < 2) return;

    final double minVal = data.reduce(min);
    final double maxVal = data.reduce(max);
    final double range = (maxVal - minVal == 0) ? 1.0 : (maxVal - minVal);

    final path = Path();
    final fillPath = Path();

    final double stepX = size.width / (data.length - 1);

    for (int i = 0; i < data.length; i++) {
      final double normalizedY = (data[i] - minVal) / range;
      final double x = i * stepX;
      // Invert Y coordinate so higher value is at the top
      final double y = size.height - (normalizedY * (size.height - 16)) - 8;

      if (i == 0) {
        path.moveTo(x, y);
        fillPath.moveTo(x, size.height);
        fillPath.lineTo(x, y);
      } else {
        path.lineTo(x, y);
        fillPath.lineTo(x, y);
      }
    }

    fillPath.lineTo(size.width, size.height);
    fillPath.close();

    // Fill Gradient
    final fillPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topCenter,
        end: Alignment.bottomCenter,
        colors: [
          lineColor.withValues(alpha: 0.35),
          lineColor.withValues(alpha: 0.0),
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));

    canvas.drawPath(fillPath, fillPaint);

    // Stroke line
    final linePaint = Paint()
      ..color = lineColor
      ..strokeWidth = 2.5
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round
      ..strokeJoin = StrokeJoin.round;

    canvas.drawPath(path, linePaint);

    // Latest point circle
    final double lastNormalizedY = (data.last - minVal) / range;
    final double lastX = size.width;
    final double lastY =
        size.height - (lastNormalizedY * (size.height - 16)) - 8;

    final dotPaint = Paint()..color = lineColor;
    canvas.drawCircle(Offset(lastX, lastY), 4.5, dotPaint);

    final dotInnerPaint = Paint()..color = Colors.white;
    canvas.drawCircle(Offset(lastX, lastY), 2.0, dotInnerPaint);
  }

  @override
  bool shouldRepaint(covariant _SparklinePainter oldDelegate) {
    return true;
  }
}
