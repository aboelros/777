# Automind Mobile — Release Checklist & Security Verification

## 1. Security & Data Protection Review

- [x] **No Hardcoded Secrets**: Verified zero API keys, passwords, or database credentials in source code.
- [x] **Token Isolation**: All access and refresh tokens stored strictly in `FlutterSecureStorage` (hardware-backed Android Keystore).
- [x] **Zero Cross-Tenant Leakage**: State containers flush cached project data immediately upon project or user account change.
- [x] **HTTPS/WSS Strict Enforcement**: Release builds reject plaintext HTTP connections.
- [x] **Log Sanitization**: Auth payloads, passwords, and PII excluded from console/debug logs in release mode.
- [x] **Permissions Minimization**: Only `INTERNET` and `ACCESS_NETWORK_STATE` permissions declared in AndroidManifest.xml.

---

## 2. Code Quality & Architecture Conformance

- [x] **File Line Limits**: All files strictly conform to the 250-line rule (Rule 11).
- [x] **Type Safety**: Sound null safety enforced across all Dart models and services.
- [x] **State Management**: Uniform Riverpod usage; no giant monolithic `StatefulWidget` or unstructured globals.
- [x] **RTL / Localization**: Full support for English and Arabic layout mirroring, text direction, and date/numeral formatters.
- [x] **Design Tokens**: Standardized colors (Sky 500, Slate 950), elevations, typography, and neuro-prism monogram logo.

---

## 3. Pre-Release Verification Commands

1. **Format Check**:
   ```powershell
   dart format --output=none --set-exit-if-changed lib test
   ```
2. **Static Analysis**:
   ```powershell
   flutter analyze
   ```
3. **Automated Unit & Widget Testing**:
   ```powershell
   flutter test
   ```
4. **Debug APK Build**:
   ```powershell
   flutter build apk --debug
   ```
5. **Release APK Build**:
   ```powershell
   flutter build apk --release
   ```

---

## 4. Release Sign-Off Matrix

| Check | Expected | Status | Notes |
|---|---|---|---|
| Health check `/health` | 200 OK | Verified | Server running |
| Login `/api/v1/auth/login` | 200 OK + JWT | Verified | Dual Bearer + Token |
| Token Refresh `/api/v1/auth/refresh` | 200 OK | Verified | Revokes old token |
| Project Isolation | 404 on unowned | Verified | Enforced via tenant context |
| Inbox & Takeover `/toggle-ai` | 200 OK | Verified | Switches AI handling off |
| Orders Listing & Transition | 200 OK | Verified | Status enum transitions |
| Bot Training CRUD | 200/204 | Verified | Instructions & templates |
| Android Build Artifact | `.apk` file | Verified | Generated upon build |
