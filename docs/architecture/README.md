# Architecture - V2 Standards Pack

## System Model

```text
Dataset preparation -> explicit permission for one supported operation
                    -> signed authorization and sealed package
                    -> checked dry run or rejection -> evidence
```

The supported research operation is `validation_parameter_update`. The synthetic runbook verifies preparation, a valid dry run and selected rejection cases. It does not train a model or execute a complete enterprise session.

## Separate Boundaries

| Boundary | Implementation meaning |
|---|---|
| Dataset lifecycle | STATE_3 containment, STATE_2 review and STATE_1 preparation do not grant permission. |
| Authorization | ALLOW has exactly one explicit scope; DENY has none. |
| Endpoint binding | Research endpoints cannot become deployment or model-release endpoints by changing a label. |
| Package integrity | A separate sealing key binds the package files. |
| Human responsibilities | Legal review and organizational authorization are not replaced by cryptographic checks. |

## Repository Interfaces

The three existing path roots preserve the v1.0 interfaces. Shared schemas, configuration and standards stay at their established paths. Do not populate them with old production data merely to make this standards pack resemble an enterprise snapshot.

See the [layout comparison](../REPOSITORY_LAYOUT.md), [paper index](../research/README.md), [synthetic runbook](../execution/TR010_STANDARDS_REFERENCE_RUNBOOK.md) and [standards interface](../../shared/standards/README.md).
