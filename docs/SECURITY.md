# Safety and privacy

## Isolated teaching use only

- The PSK `SYNTHETIC_F031_F034_LAB_ONLY_V1` is an intentionally public example, not a secret. Never reuse it in a real network.
- The original router configs disable console login and console timeouts. Do not expose them to untrusted users or networks.
- Alpine startup scripts flush eth0 addressing and replace its default route. They belong only inside the disposable lab nodes. Do not run them on your host.
- No external connector or internet path is included. Keep it that way for this reproduction.
- Crypto settings are historical lab choices, not a current production security recommendation.
- Obtain Cisco/CML images only under an appropriate license through authorized channels.

## What was excluded

The files contain no real credentials, home/employer/customer identifiers, learner records, VM images or raw running configurations from restricted systems. Runtime UUIDs, MACs, serials, SPI values and session identifiers have been excluded from the recorded CLI excerpts.

Only the original synthetic startup configs, synthetic addressing/peer identities, newly written guidance and minimal selected historical observations are included. Generic node IDs such as n0/i0 are local topology keys, not runtime UUIDs.

## Review limits

An automated scan is a backstop, not an exhaustive secret detector. Review configuration and output in context before sharing it, and confirm that you have the right to share the material.

If future outputs contain real identifiers or uncertain provenance, keep them private until reviewed. The offline verification scripts do not contact, authenticate to, or modify any CML instance.
