# Version Risk Model

| Constraint | Risk | Note |
|---|---|---|
| Up to next major | Low | Normal SemVer-compatible range |
| Up to next minor | Medium | Safer but may lag patch/minor improvements |
| Exact version | Medium | Reproducible but can block security updates |
| Branch | High | Moving target, weak reproducibility |
| Revision | High | Frozen commit, hard to reason about updates |
| Missing lockfile for app project | Medium | Reproducibility risk |
| Same dependency in SPM and CocoaPods | High | Duplicate or conflict risk |

Online latest checks require current source verification and the date checked.
