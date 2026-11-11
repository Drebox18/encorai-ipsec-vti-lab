#!/usr/bin/env python3
"""Offline checks only. Does not contact or configure devices."""
from pathlib import Path
import hashlib, ipaddress, json, re, sys

ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PSK = 'SYNTHETIC_F031_F034_LAB_ONLY_V1'
EXPECTED_ROUTES = {'CR-R1':'ip route 10.31.20.0 255.255.255.0 Tunnel31', 'CR-R2':'ip route 10.31.10.0 255.255.255.0 Tunnel31'}
def check_topology(t, configs):
    assert len(t['nodes']) == 4 and len(t['links']) == 3, 'Expected exactly four nodes and three links'
    nodes = {n['id']:n for n in t['nodes']}
    assert len(nodes)==4, 'Duplicate node IDs'
    assert {n['label'] for n in nodes.values()}=={'LAN-A','LAN-B','CR-R1','CR-R2'}, 'Unknown or external node'
    assert {n['node_definition'] for n in nodes.values()}=={'alpine','csr1000v'}, 'Unexpected node definition'
    assert sum(n['ram'] for n in nodes.values())==7168
    assert sum(n['cpus'] for n in nodes.values())==4
    edges=set(); used=set()
    for link in t['links']:
        endpoints=[]
        for ni, ii in [('n1','i1'),('n2','i2')]:
            n=nodes[link[ni]]
            ints={i['id']:i for i in n['interfaces']}
            assert len(ints)==len(n['interfaces']), 'Duplicate interface ID'
            endpoint=(n['label'],ints[link[ii]]['label'])
            assert endpoint not in used, 'Interface reused by another link'
            used.add(endpoint); endpoints.append(endpoint)
        edges.add(frozenset(endpoints))
    expected={frozenset([('LAN-A','eth0'),('CR-R1','GigabitEthernet2')]),frozenset([('CR-R1','GigabitEthernet1'),('CR-R2','GigabitEthernet1')]),frozenset([('CR-R2','GigabitEthernet2'),('LAN-B','eth0')])}
    assert edges==expected, 'Unexpected link adjacency'
    for n in nodes.values():
        assert len(n['configuration'])==1
        assert n['configuration'][0]['content']==configs[n['label']], 'Embedded config mismatch'
    for name, route in EXPECTED_ROUTES.items():
        c=configs[name]
        assert route in c.splitlines(), 'Missing remote LAN route'
        peer='192.0.2.2' if name=='CR-R1' else '192.0.2.1'
        assert ' tunnel destination '+peer in c.splitlines()
        assert ' tunnel protection ipsec profile CR-IPSEC' in c.splitlines()
        keys=re.findall(r'^  pre-shared-key (?:local|remote) (.+)$',c,re.M)
        assert keys==[PUBLIC_PSK,PUBLIC_PSK], 'Unexpected credential'
        assert ' no login' in c.splitlines(), 'Original console boundary changed'
    for label, addr, gw in [('LAN-A','10.31.10.10','10.31.10.1'),('LAN-B','10.31.20.10','10.31.20.1')]:
        assert 'ip address add '+addr+'/24 dev eth0' in configs[label].splitlines()
        assert 'ip route replace default via '+gw in configs[label].splitlines()
    return True

def check_proof(p, root):
    assert p['observed_date']=='2026-10-19'
    assert p['fresh_runtime_test_performed'] is False and p['repackaged_topology_import_tested'] is False
    assert p['ike_status']=={'r1':'READY','r2':'READY'}
    assert len(p['observations'])==8
    assert set(p['traffic'])=={'lan_a_to_b','lan_b_to_a'}, 'Missing traffic direction'
    assert set(p['counters'])=={'r1','r2'}, 'Missing router counters'
    for v in p['traffic'].values(): assert v=={'sent':5,'received':5,'loss_percent':0}
    for v in p['counters'].values(): assert v=={'before':{'encaps':59,'decaps':59},'after':{'encaps':69,'decaps':69}}
    for o in p['observations']:
        path=Path(o['file']); assert not path.is_absolute() and '..' not in path.parts
        data=(root/path).read_bytes()
        assert hashlib.sha256(data).hexdigest()==o['excerpt_sha256'], 'Evidence excerpt changed'
        assert o['captured_at'].startswith('2026-10-19T')
    return True

def privacy_findings(root):
    # An intentionally bounded detector. Contextual review remains necessary.
    patterns=[r'github\.com/[^/\s]+/',r'trello\.com/c/',r'libfile_[A-Za-z0-9_-]+',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',r'gh[pousr]_[A-Za-z0-9]{20,}',r'AKIA[A-Z0-9]{16}',r'(?i)(?:local |remote |outbound )?spi:\s*(?:0x)?[0-9A-F]{8,}',r'[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}']
    findings=[]
    for path in sorted(root.rglob('*')):
        if not path.is_file() or '__pycache__' in path.parts: continue
        if path.suffix not in {'.md','.txt','.json','.yaml','.cfg','.svg','.html','.py'}: continue
        # Regex definitions contain detector examples, not payloads.
        if path.suffix=='.py': continue
        text=path.read_text()
        for pattern in patterns:
            if re.search(pattern,text): findings.append(str(path.relative_to(root))+': disallowed content pattern')
    return findings

def verify(root=ROOT):
    t=json.loads((root/'topology.yaml').read_text())
    configs={p.stem:p.read_text() for p in (root/'configs').glob('*.cfg')}
    check_topology(t,configs)
    check_proof(json.loads((root/'evidence/historical-proof.json').read_text()),root)
    findings=privacy_findings(root); assert not findings, findings
    manifest=json.loads((root/'PACKAGE_MANIFEST.json').read_text())
    expected={x['path'] for x in manifest['files']}
    actual={str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts and p.name!='PACKAGE_MANIFEST.json'}
    assert actual==expected, 'Unlisted or missing package file'
    for f in manifest['files']:
        data=(root/f['path']).read_bytes()
        assert hashlib.sha256(data).hexdigest()==f['sha256'], 'Package file changed: '+f['path']
    print('PASS: topology, configs, historical evidence, bounded privacy scan and '+str(len(expected))+' file hashes. No CML calls made.')
    return True
if __name__=='__main__':
    try: verify()
    except (AssertionError, KeyError, ValueError, OSError) as e:
        print('FAIL:',str(e),file=sys.stderr); sys.exit(1)
