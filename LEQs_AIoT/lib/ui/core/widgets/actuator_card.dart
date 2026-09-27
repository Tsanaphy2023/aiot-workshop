import 'package:flutter/material.dart';

class ActuatorCard extends StatelessWidget {
  final String title;
  final String subtitle;
  final IconData icon;
  final bool isOn;
  final bool isLocked;
  final String? lockReason;
  final int? remainingSeconds;
  final ValueChanged<bool>? onToggle;
  final Color activeColor;

  const ActuatorCard({
    super.key,
    required this.title,
    required this.subtitle,
    required this.icon,
    required this.isOn,
    this.isLocked = false,
    this.lockReason,
    this.remainingSeconds,
    this.onToggle,
    this.activeColor = const Color(0xFF10B981),
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final isDark = theme.brightness == Brightness.dark;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Row(
              children: [
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: isOn
                        ? activeColor.withValues(alpha: 0.2)
                        : (isDark ? Colors.white10 : Colors.black12),
                    shape: BoxShape.circle,
                  ),
                  child: Icon(
                    icon,
                    color: isOn
                        ? activeColor
                        : (isDark ? Colors.white54 : Colors.black54),
                    size: 26,
                  ),
                ),
                const SizedBox(width: 14),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        title,
                        style: theme.textTheme.titleMedium?.copyWith(
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 2),
                      Text(
                        subtitle,
                        style: theme.textTheme.bodySmall?.copyWith(
                          color: isDark ? Colors.white60 : Colors.black54,
                        ),
                      ),
                      if (remainingSeconds != null && remainingSeconds! > 0) ...[
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            Icon(Icons.timer, size: 14, color: activeColor),
                            const SizedBox(width: 4),
                            Text(
                              'หยุดอัตโนมัติใน: ${remainingSeconds}s',
                              style: TextStyle(
                                color: activeColor,
                                fontSize: 12,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ],
                        ),
                      ],
                    ],
                  ),
                ),
                Switch.adaptive(
                  value: isOn,
                  activeThumbColor: activeColor,
                  onChanged: isLocked ? null : onToggle,
                ),
              ],
            ),
            if (isLocked && lockReason != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: Colors.red.withValues(alpha: 0.12),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(color: Colors.red.withValues(alpha: 0.3)),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.shield_outlined,
                        color: Colors.red, size: 18),
                    const SizedBox(width: 8),
                    Expanded(
                      child: Text(
                        lockReason!,
                        style: const TextStyle(
                          color: Colors.red,
                          fontSize: 12,
                          fontWeight: FontWeight.w500,
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
