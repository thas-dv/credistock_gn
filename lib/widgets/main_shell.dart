import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../core/router/app_router.dart';
import '../../core/theme/app_theme.dart';

class MainShell extends StatelessWidget {
  final Widget child;
  const MainShell({super.key, required this.child});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: child,
      bottomNavigationBar: _BottomNavBar(),
      floatingActionButton: _VocalFAB(),
      floatingActionButtonLocation: FloatingActionButtonLocation.centerDocked,
    );
  }
}

// ============================================================
// BOTTOM NAV — 4 items + slot central pour FAB
// ============================================================

class _BottomNavBar extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final location = GoRouterState.of(context).matchedLocation;

    return BottomAppBar(
      height: 64,
      padding: EdgeInsets.zero,
      color: Colors.white,
      shape: const CircularNotchedRectangle(),
      notchMargin: 6,
      child: Row(
        children: [
          // Accueil
          _NavItem(
            icon: Icons.home_outlined,
            iconActive: Icons.home,
            label: 'Accueil',
            route: AppRoutes.home,
            isActive: location == AppRoutes.home,
          ),
          // Stock
          _NavItem(
            icon: Icons.inventory_2_outlined,
            iconActive: Icons.inventory_2,
            label: 'Stock',
            route: AppRoutes.stock,
            isActive: location.startsWith(AppRoutes.stock),
          ),
          // Espace central (FAB)
          const Expanded(child: SizedBox()),
          // Clients
          _NavItem(
            icon: Icons.people_outline,
            iconActive: Icons.people,
            label: 'Clients',
            route: AppRoutes.clients,
            isActive: location.startsWith(AppRoutes.clients),
          ),
          // Dettes
          _NavItem(
            icon: Icons.account_balance_wallet_outlined,
            iconActive: Icons.account_balance_wallet,
            label: 'Dettes',
            route: AppRoutes.dettes,
            isActive: location.startsWith(AppRoutes.dettes),
          ),
        ],
      ),
    );
  }
}

class _NavItem extends StatelessWidget {
  final IconData icon;
  final IconData iconActive;
  final String label;
  final String route;
  final bool isActive;

  const _NavItem({
    required this.icon,
    required this.iconActive,
    required this.label,
    required this.route,
    required this.isActive,
  });

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: InkWell(
        onTap: () => context.go(route),
        borderRadius: BorderRadius.circular(12),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              isActive ? iconActive : icon,
              color: isActive ? AppColors.green : AppColors.gray400,
              size: 22,
            ),
            const SizedBox(height: 2),
            Text(
              label,
              style: TextStyle(
                fontSize: 10,
                fontWeight: isActive ? FontWeight.w500 : FontWeight.w400,
                color: isActive ? AppColors.green : AppColors.gray400,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

// ============================================================
// FAB VOCAL — bouton central animé
// ============================================================

class _VocalFAB extends StatefulWidget {
  @override
  State<_VocalFAB> createState() => _VocalFABState();
}

class _VocalFABState extends State<_VocalFAB>
    with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scaleAnim;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 1200),
    )..repeat(reverse: true);

    _scaleAnim = Tween<double>(begin: 1.0, end: 1.08).animate(
      CurvedAnimation(parent: _controller, curve: Curves.easeInOut),
    );
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return ScaleTransition(
      scale: _scaleAnim,
      child: FloatingActionButton(
        onPressed: () => context.push(AppRoutes.vente),
        backgroundColor: AppColors.green,
        foregroundColor: Colors.white,
        elevation: 4,
        shape: const CircleBorder(),
        child: const Icon(Icons.mic, size: 26),
      ),
    );
  }
}