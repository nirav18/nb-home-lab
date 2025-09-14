
```mermaid
%%{init: {'theme':'forest', 'securityLevel': 'strict' }}%%
sequenceDiagram
    participant Eng as Network Engineer
    participant NB as Nautobot
    participant WH as Nautobot Webhook
    participant GH as GitHub Repo
    participant CI as GitHub Actions (CI)
    participant Reviewer as Reviewer (Peer/Lead)
    participant AAP as Ansible Automation Platform
    participant CVP as Arista CVP
    participant Dev as Existing Device

    Eng->>NB: Update intent (e.g. VLAN, interface description)
    NB-->>WH: Trigger webhook (object.updated)
    WH->>GH: Commit YAML changes & open PR
    GH->>CI: Run CI pipeline (lint, validate, render configs)
    CI-->>GH: Post status (✅/❌)

    Reviewer->>GH: Review PR (diff shows config change)
    GH->>GH: Merge PR to main
    GH->>AAP: Trigger Job Template via API
    AAP->>AAP: Run push-to-cvp.yml playbook
    AAP->>CVP: Upload updated configlets
    CVP->>CVP: Create Change Control
    CVP->>Dev: Deploy updated configuration
```


### 2nd Use Case
```mermaid
sequenceDiagram
    participant Eng as Network Engineer
    participant NB as Nautobot
    participant WH as Nautobot Webhook
    participant GH as GitHub Repo
    participant CI as GitHub Actions (CI)
    participant Reviewer as Reviewer (Peer/Lead)
    participant AAP as Ansible Automation Platform
    participant CVP as Arista CVP
    participant Dev as New Device

    Eng->>NB: Add new device (role, site, interfaces, etc.)
    NB-->>WH: Trigger webhook (device.created)
    WH->>GH: Commit YAML to designs/ & open PR
    GH->>CI: Run CI pipeline (lint, validate, render configs)
    CI-->>GH: Post status (✅/❌)

    Reviewer->>GH: Review & approve PR
    GH->>GH: Merge PR to main
    GH->>AAP: Trigger Job Template via API
    AAP->>AAP: Run push-to-cvp.yml playbook
    AAP->>CVP: Upload configlets, attach to new device
    CVP->>CVP: Create Change Control
    CVP->>Dev: Deploy configuration
```


Nautobot stays authoritative: you don’t duplicate intent into YAML — all truth for IPs, LAGs, VLANs, etc. lives in Nautobot.

AVD remains stateless: it only consumes structured vars in the format it expects, so configs are still deterministic.

Translation layer is explicit: you see the mapping logic from “how we model it in Nautobot” → “how AVD wants it.”

```mermaid
flowchart TD
    NB[(Nautobot)] -->|Webhook/API Call| EXP[Export Script / Custom Jinja Filters / Plugins]
    EXP -->|Generate YAML| VARS[AVD Vars format]
    VARS -->|GH Branch and Push | GHACP[GH New Branch]
    GHACP -->|Trigger on Push| CI[GitHub Actions CI]
    CI -->|Render & Validate| GEN[AVD Rendered Configs<br> generated/configlets]
    CI -->|Merge to main <br> Peer Approval| PeerApproval[(GitHub Repo)]
    PeerApproval -->|Trigger Job Template| AAPCI[Ansible Automation Platform GH Action]
    AAPCI -->|Run push-to-cvp.yml| CVP[Arista CVP]
    CVP -->|Change Control / Deploy| DEV[Arista EOS Devices]
```
