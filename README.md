# credistock_gn

A new Flutter project.

## Getting Started

This project is a starting point for a Flutter application.

A few resources to get you started if this is your first Flutter project:

- [Learn Flutter](https://docs.flutter.dev/get-started/learn-flutter)
- [Write your first Flutter app](https://docs.flutter.dev/get-started/codelab)
- [Flutter learning resources](https://docs.flutter.dev/reference/learning-resources)

For help getting started with Flutter development, view the
[online documentation](https://docs.flutter.dev/), which offers tutorials,
samples, guidance on mobile development, and a full API reference.


 `cmake -E tar: error: ZIP decompression failed (-5)`
- `...extracted/firebase_cpp_sdk_windows does not contain a CMakeLists.txt`
- `get_target_property() called with non-existent target "firebase_app"`

cela veut généralement dire que le SDK C++ Firebase téléchargé pendant le build Windows est corrompu ou incomplet.

### Correctif recommandé

Dans un terminal PowerShell, à la racine du projet :

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\fix_windows_firebase_build.ps1
```

Puis relancez le build :

```bash
flutter build windows
```

### Correctif manuel (si besoin)

1. Fermez l’application et tout process de build Flutter/CMake.
2. Supprimez les dossiers de build temporaires :
   - `build/windows/x64`
   - `.dart_tool`
3. Exécutez :
   - `flutter clean`
   - `flutter pub get`
4. Relancez :
   - `flutter build windows`

### Conseils si l’erreur persiste

- Évitez les dossiers synchronisés cloud (OneDrive/Dropbox) pendant le build.
- Vérifiez qu’un antivirus ne bloque pas l’extraction ZIP.
- Assurez-vous d’avoir Visual Studio Build Tools + composants C++ pour Desktop.