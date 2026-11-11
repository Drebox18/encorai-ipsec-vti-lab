# What the evidence proves

## Historical, not freshly reproduced

The bundled observations were captured on October 19, 2026 between 17:09 and 17:14 UTC. This package was assembled November 11. Hashes of all eight source texts and their manifests were verified against the existing evidence index before excerpts were made.

The excerpts retain exact selected lines, with a new explanatory header. They are not full device output, screenshots or reconstructed CLI. Runtime SPI/session identifiers and unrelated lines were excluded. The numeric JSON summary is derived from those original observations; IKE `READY` was read from the original status rows, which are not reproduced because they also carry a runtime tunnel identifier.

| Check | Recorded result |
|---|---|
| IKE state | READY on both routers |
| LAN-A to LAN-B | 5 sent, 5 received, 0% loss |
| LAN-B to LAN-A | 5 sent, 5 received, 0% loss |
| Router 1 encaps / decaps | 59 / 59 before, 69 / 69 after |
| Router 2 encaps / decaps | 59 / 59 before, 69 / 69 after |

The original four configs match their recorded SHA-256 values exactly. The showcase changes only lab title/description/notes in the topology, not nodes, links or embedded configs. Historical observations came after a naming-only change, so observed runtime names and the preserved source hostnames are not identical. The protocol and addressing configuration is the same; the new packaging has not been dynamically revalidated.

## New checks performed for the package

`scripts/verify.py` performs offline consistency and privacy checks. `tests/test_package.py` includes negative tests that reject altered routing, mismatched embedded configs, external nodes and evidence drift. The verifier and all 18 unit tests passed on November 11, 2026. These are static checks, not a fresh router run.

The [CML screenshot](CML-SCREENSHOT.md) was captured separately on November 11. It shows the existing topology with four booted nodes. No console commands or traffic tests were run for the screenshot, so it does not update or replace the October 19 protocol and forwarding evidence.

## Not established

- Deployment in another CML installation or compatibility with different images.
- Production security, internet connectivity, AWS VPN integration or performance.
- An injected failure, hands-on diagnosis, repair or retention of the lesson.
- PFS rekey behavior, path-MTU correctness or arbitrary application reachability.
- Hands-on time or independent troubleshooting ability.

## How to make the claim stronger later

To reproduce the result, import this topology into a new disposable lab in an environment you are authorized to use. Record the CML/image versions, run the documented bounded checks and save a new dated result. Preserve the older evidence rather than relabeling it as new.
