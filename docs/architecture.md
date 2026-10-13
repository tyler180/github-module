# Local v1 architecture

```mermaid
flowchart TD
  Root[Consuming root: inventory and staged intent] --> Module[One repository per module]
  Root --> Policy[Trusted validator: separate base/record/snapshot/plan]
  Module --> Settings[Settings and explicit grants]
  Module --> Rules[Default-branch ruleset]
  Template[One generic template source] --> Bootstrap[Reviewed bootstrap PR]
  Bootstrap --> Caller[Repository-owned pinned caller and hook config]
  Caller --> Shared[Existing github-workflows plus new validation/hooks]
  Shared --> Checks[Deterministic results]
  Checks --> Rules
  Evidence[Independent observation: live adapter pending] --> Policy
  Policy --> Receipt[Offline binding only; no deployment authorization]
```

No organization policy is managed by this module. No workflow executes Terraform
from the trusted policy job. Candidate Terraform validation is unprivileged and
separate from credentialed infrastructure planning. The deployment workflow now connects isolated policy gates but blocks live
repository authorization. No backend, credential, record writer, live collector, or active
caller is created by this local implementation.

Functional increments: core/adoption; optional access/actions/rules; root staging;
generic template and Go pilot; trusted policy fixtures/bindings; documentation and
workflow linting. See verification.md for actual pass/blocked results, not inferred
operational readiness.
