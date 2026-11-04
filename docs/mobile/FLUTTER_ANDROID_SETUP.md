# Automind Mobile — Flutter Android Environment & Setup Guide

## 1. System Requirements & Prerequisites

- **Operating System:** Windows 10/11, macOS, or Linux.
- **Flutter SDK:** Version 3.44.x or higher (Dart 3.12.x+).
- **Java Development Kit (JDK):** JDK 17 or JDK 21 (Bundled in Android Studio `/jbr`).
- **Android SDK:**
  - Android SDK Platform 34 (Android 14) / Platform 35 (Android 15).
  - Android SDK Build-Tools 34.0.0+.
  - Platform-Tools (adb 37+).
- **Target Device / Emulator:**
  - Android physical device running Android 7.0 (API 24) or newer with USB debugging enabled.
  - Android Virtual Device (AVD) running API 34+ (e.g. `medium_phone`).

---

## 2. Environment Configuration

### Android SDK & Tooling on Windows
Set the following environment variables if not already defined:
```powershell
[System.Environment]::SetEnvironmentVariable("ANDROID_HOME", "C:\Users\ARKAN STOER\AppData\Local\Android\sdk", "User")
[System.Environment]::SetEnvironmentVariable("JAVA_HOME", "C:\Program Files\Android\Android Studio\jbr", "User")
```

Verify Flutter configuration:
```powershell
flutter config --android-studio-dir="C:\Program Files\Android\Android Studio"
flutter config --jdk-dir="C:\Program Files\Android\Android Studio\jbr"
flutter doctor -v
```

---

## 3. Local Backend Connectivity (Android Emulator vs Device)

When running the Automind backend locally on `http://localhost:8000`:
- **Android Emulator**: The Android emulator cannot access the host machine via `localhost`. Use the Android loopback address:
  `http://10.0.2.2:8000`
- **Physical Device**: Connect to your machine's local LAN IP (e.g. `http://192.168.1.X:8000`) or use ADB reverse proxy:
  ```powershell
  adb reverse tcp:8000 tcp:8000
  ```
  Once reversed, the physical device can communicate with `http://localhost:8000`.
- **Production Server**: The app connects directly to the production API:
  `https://ai-sales-bot-api-vdr6.onrender.com`

---

## 4. Building and Running the Application

### Dependencies Installation
Navigate to the mobile app directory:
```powershell
cd android
flutter pub get
```

### Static Analysis and Code Formatting
```powershell
dart format --output=none --set-exit-if-changed lib test
flutter analyze
```

### Running Automated Test Suite
```powershell
flutter test
```

### Debug Build
```powershell
flutter build apk --debug
```
Artifact location: `android/build/app/outputs/flutter-apk/app-debug.apk`

### Release Build
```powershell
flutter build apk --release
```
Artifact location: `android/build/app/outputs/flutter-apk/app-release.apk`
