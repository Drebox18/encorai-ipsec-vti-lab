# Reproduction and verification guide

## 1. Check the package before touching a lab

Run `python3 scripts/verify.py` and `python3 -m unittest discover -s tests -v` from the candidate root. Preserve the outputs. The verifier checks file hashes, embedded/separate config equality, addressing, routes, four-node isolation and dated evidence consistency. It does not parse every IOS command or certify Cisco compatibility.

Only import into your own new disposable lab. Do not attach this topology to an external network. If a node definition or image is missing, stop and obtain a properly licensed compatible image through official channels; do not download images from this project or substitute an untested image silently.

## 2. Confirm expected topology

| Link | First endpoint | Second endpoint |
|---|---|---|
| LAN A | LAN-A eth0 | CR-R1 GigabitEthernet2 |
| Underlay | CR-R1 GigabitEthernet1 | CR-R2 GigabitEthernet1 |
| LAN B | CR-R2 GigabitEthernet2 | LAN-B eth0 |

| Segment | Left | Right |
|---|---|---|
| LAN A | host 10.31.10.10/24 | gateway 10.31.10.1 |
| Underlay | CR-R1 192.0.2.1/30 | CR-R2 192.0.2.2/30 |
| Encrypted VTI | CR-R1 172.31.255.1/30 | CR-R2 172.31.255.2/30 |
| LAN B | gateway 10.31.20.1 | host 10.31.20.10/24 |

The 192.0.2.0/24 documentation range is used only inside the isolated lab. The other addresses are synthetic private addresses, not actual home or employer network details. The FQDN peer identities are under the reserved `.test` namespace and require no DNS lookup.

## 3. Start and inspect only the new lab

Use the normal CML controls for the newly imported disposable lab. Confirm all four nodes are booted. These startup configs are applied by the node environment; **never execute LAN-A.cfg or LAN-B.cfg in your workstation's shell**. They replace an interface address and default route.

On each router:

```text
show interfaces Tunnel31
show ip route
show crypto ikev2 sa detailed
show crypto ipsec sa
```

On LAN-A and LAN-B:

```text
ip address show dev eth0
ip route
```

Check local addressing, the correct host default gateway and the remote LAN route through Tunnel31. Before traffic, an IPsec session may still be negotiating. Do not mark a failure or success from that single moment.

## 4. Establish a traffic-ready baseline

If no IKE/ESP association exists yet, run one five-packet probe from each host using the commands below to trigger negotiation. Keep those warm-up results separate from the measured test. Recheck both routers for IKE `READY`, inbound/outbound active ESP SAs, Tunnel31 up/up and remote LAN routes. If still not healthy, stop and record the discrepancy instead of retrying without a limit or changing crypto settings by guesswork.

Before the measured traffic, record encaps and decaps counts on **both** routers. Then run once on each host:

LAN-A:
```text
ping -c 5 -W 2 10.31.20.10
```

LAN-B:
```text
ping -c 5 -W 2 10.31.10.10
```

Immediately reread `show crypto ipsec sa` on both routers. Record actual values, not the example counts. A successful small-packet check requires five replies in each direction and growth in all four counter samples. Other lab traffic may change exact deltas; explain discrepancies rather than editing evidence.

## 5. Explain the result

- IKE `READY`: peer negotiation/authentication succeeded. It is not proof of application reachability.
- Active ESP SAs: protected data-plane associations exist in both directions.
- Route through Tunnel31: packets for the remote LAN select the encrypted path.
- Host-to-host replies: both forwarding and return paths worked for these probes.
- Encaps and decaps growth on both routers: corroborates encrypted transmission and reception over the measured interval.

The ten-packet counter increase in the archived sample is compatible with five echo requests from each end and their replies. It is not a throughput measurement or a promise that future runs have identical counters.

## 6. Preserve and stop safely

Save your own dated, sanitized observations outside the bundled historical evidence. Remove runtime identifiers, SPI values, device serials, MACs and any real credentials before sharing. Stop only the disposable lab you created when done. This guide does not authorize modifying an existing personal, employer, customer or golden-baseline lab.

## Optional next experiment, not completed proof

A future separately planned exercise could remove a remote-LAN route, predict the symptom, diagnose it, restore the exact route and repeat the checks. No fault script is bundled, and this package does not claim such an exercise was executed or mastered.
