# Multiple Protocol Conformance

**Applies to:** Performance, UIKit/SwiftUI cells, reusable components

## Why this is bad

Many small protocols = many conformance checks at runtime:
- Each protocol is verified via `swift_conform_protocol`
- In cells/components with a large reuse count, costs multiply
- Replacing multiple protocols with one gave a 2.5-3x speedup in T-Bank

## Bad Example

```swift
// ❌ BAD: Many small protocols for cell configuration
protocol TitleConfigurable {
    var title: String { get }
}

protocol SubtitleConfigurable {
    var subtitle: String? { get }
}

protocol ImageConfigurable {
    var imageURL: URL? { get }
}

protocol ActionConfigurable {
    var action: (() -> Void)? { get }
}

// Each protocol cast is a separate swift_conform_protocol
func configure(cell: UITableViewCell, with model: Any) {
    if let titled = model as? TitleConfigurable {
        cell.textLabel?.text = titled.title
    }
    if let subtitled = model as? SubtitleConfigurable {
        cell.detailTextLabel?.text = subtitled.subtitle
    }
    if let imaged = model as? ImageConfigurable {
        loadImage(imaged.imageURL)
    }
    if let actionable = model as? ActionConfigurable {
        cell.accessoryType = actionable.action != nil ? .disclosureIndicator : .none
    }
}
```

## Good Example

```swift
// ✅ GOOD: One protocol with optional properties
protocol CellConfigurable {
    var title: String { get }
    var subtitle: String? { get }
    var imageURL: URL? { get }
    var action: (() -> Void)? { get }
}

// One cast instead of four
func configure(cell: UITableViewCell, with model: CellConfigurable) {
    cell.textLabel?.text = model.title
    cell.detailTextLabel?.text = model.subtitle
    if let url = model.imageURL { loadImage(url) }
    cell.accessoryType = model.action != nil ? .disclosureIndicator : .none
}

// ✅ GOOD: Alternative - struct configuration without castes
struct CellConfiguration {
    let title: String
    var subtitle: String?
    var imageURL: URL?
    var action: (() -> Void)?
}

func configure(cell: UITableViewCell, with config: CellConfiguration) {
    cell.textLabel?.text = config.title
    cell.detailTextLabel?.text = config.subtitle
    if let url = config.imageURL { loadImage(url) }
    cell.accessoryType = config.action != nil ? .disclosureIndicator : .none
}
```

## What to look for in code review

- Multiple `as?` to different protocols for one object
- Decomposition into 3+ small protocols for configuring UI components
- Protocol castes within `cellForRow` / `tableView(_:willDisplay:)` ​​and analogues
- “We check each protocol in turn” pattern in the hot path
