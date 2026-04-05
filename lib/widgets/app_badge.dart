import 'package:flutter/material.dart';
import '../../core/theme/app_theme.dart';

// ============================================================
// APP BADGE — score client, statut dette
// ============================================================

class AppBadge extends StatelessWidget {
  final String label;
  final String type; // bon | moyen | mauvais | paye | non_paye | partiel | info

  const AppBadge({super.key, required this.label, required this.type});

  @override
  Widget build(BuildContext context) {
    final (bg, fg) = _colors;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: bg,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(
        label,
        style: TextStyle(fontSize: 11, fontWeight: FontWeight.w500, color: fg),
      ),
    );
  }

  (Color, Color) get _colors => switch (type) {
    'bon' || 'paye' => (AppColors.greenLight, AppColors.greenDark),
    'moyen' || 'partiel' => (AppColors.amberLight, AppColors.amber),
    'mauvais' || 'non_paye' => (AppColors.redLight, AppColors.red),
    'info' => (AppColors.blueLight, AppColors.blue),
    _ => (AppColors.gray50, AppColors.gray600),
  };
}

// ============================================================
// METRIC CARD — dashboard chiffres clés
// ============================================================

class MetricCard extends StatelessWidget {
  final String label;
  final String value;
  final String unit;
  final String trend;
  final bool? trendPositive;
  final Color color;

  const MetricCard({
    super.key,
    required this.label,
    required this.value,
    required this.unit,
    required this.trend,
    required this.trendPositive,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.black.withOpacity(0.07), width: 0.5),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            label,
            style: const TextStyle(fontSize: 11, color: AppColors.gray400),
            maxLines: 1,
            overflow: TextOverflow.ellipsis,
          ),
          const SizedBox(height: 6),
          Text(
            value,
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.w600,
              color: color,
            ),
          ),
          if (unit.isNotEmpty)
            Text(unit, style: const TextStyle(fontSize: 10, color: AppColors.gray400)),
          const SizedBox(height: 4),
          Row(
            children: [
              if (trendPositive != null)
                Icon(
                  trendPositive! ? Icons.trending_up : Icons.trending_down,
                  size: 12,
                  color: trendPositive! ? AppColors.green : AppColors.red,
                ),
              const SizedBox(width: 2),
              Text(
                trend,
                style: TextStyle(
                  fontSize: 10,
                  color: trendPositive == null
                      ? AppColors.gray400
                      : trendPositive!
                          ? AppColors.green
                          : AppColors.red,
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

// ============================================================
// SECTION HEADER
// ============================================================

class SectionHeader extends StatelessWidget {
  final String title;
  final String? actionLabel;
  final VoidCallback? onAction;

  const SectionHeader({
    super.key,
    required this.title,
    this.actionLabel,
    this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: [
        Text(
          title.toUpperCase(),
          style: const TextStyle(
            fontSize: 11,
            fontWeight: FontWeight.w600,
            color: AppColors.gray400,
            letterSpacing: 0.5,
          ),
        ),
        if (actionLabel != null && onAction != null)
          TextButton(
            onPressed: onAction,
            style: TextButton.styleFrom(
              foregroundColor: AppColors.green,
              padding: const EdgeInsets.symmetric(horizontal: 4),
              minimumSize: Size.zero,
              tapTargetSize: MaterialTapTargetSize.shrinkWrap,
            ),
            child: Text(actionLabel!, style: const TextStyle(fontSize: 12)),
          ),
      ],
    );
  }
}

// ============================================================
// PROGRESS DEBT BAR
// ============================================================

class DetteProgressBar extends StatelessWidget {
  final int montant;
  final int montantPaye;
  final Color color;

  const DetteProgressBar({
    super.key,
    required this.montant,
    required this.montantPaye,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    final ratio = montant > 0 ? (montantPaye / montant).clamp(0.0, 1.0) : 0.0;
    return ClipRRect(
      borderRadius: BorderRadius.circular(3),
      child: LinearProgressIndicator(
        value: ratio,
        backgroundColor: color.withOpacity(0.15),
        valueColor: AlwaysStoppedAnimation(color),
        minHeight: 5,
      ),
    );
  }
}