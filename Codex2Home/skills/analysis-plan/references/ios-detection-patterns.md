# iOS and Swift Detection Patterns

## Project Files

| File | Meaning |
|---|---|
| `Package.swift` | SwiftPM package, targets, products and dependencies |
| `Package.resolved` | Resolved SwiftPM versions |
| `.xcodeproj` | Xcode project |
| `.xcworkspace` | Xcode workspace |
| `Podfile`, `Podfile.lock` | CocoaPods |
| `Cartfile`, `Cartfile.resolved` | Carthage |
| `.swiftlint.yml` | SwiftLint |
| `.swiftformat` | SwiftFormat |

## Architecture Signals

| Signal | Meaning |
|---|---|
| `import SwiftUI` | SwiftUI |
| `import UIKit` | UIKit |
| `ViewModel`, `ObservableObject`, `@Published` | MVVM |
| `Presenter`, `Interactor`, `Router` | VIPER-like |
| `Store`, `Reducer`, `Effect`, `ComposableArchitecture` | TCA or Redux-like |
| `Coordinator` | Coordinator navigation |

## Infrastructure Signals

| Signal | Meaning |
|---|---|
| `.github/workflows/*.yml` | GitHub Actions |
| `.gitlab-ci.yml` | GitLab CI |
| `fastlane/Fastfile` | Fastlane |
| `Jenkinsfile` | Jenkins |
| `*.generated.swift` | generated Swift |
| `.xcstrings`, `.strings` | localization |
