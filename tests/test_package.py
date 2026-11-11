import copy, importlib.util, json, tempfile, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('verify',ROOT/'scripts/verify.py')
v=importlib.util.module_from_spec(spec); spec.loader.exec_module(v)
class PackageTests(unittest.TestCase):
    def setUp(self):
        self.t=json.loads((ROOT/'topology.yaml').read_text())
        self.c={p.stem:p.read_text() for p in (ROOT/'configs').glob('*.cfg')}
        self.p=json.loads((ROOT/'evidence/historical-proof.json').read_text())
    def test_01_valid_topology(self): self.assertTrue(v.check_topology(self.t,self.c))
    def test_02_four_configs(self): self.assertEqual(set(self.c),{'LAN-A','LAN-B','CR-R1','CR-R2'})
    def test_03_reject_extra_node(self):
        self.t['nodes'].append(copy.deepcopy(self.t['nodes'][0]))
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_04_reject_external_connector(self):
        self.t['nodes'][0]['node_definition']='external_connector'
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_05_reject_wrong_link(self):
        self.t['links'][0]['i2']='i0'
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_06_reject_embedded_drift(self):
        self.t['nodes'][1]['configuration'][0]['content']+='! changed'
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_07_reject_route_drift(self):
        self.c['CR-R1']=self.c['CR-R1'].replace('ip route 10.31.20.0 255.255.255.0 Tunnel31','ip route 10.31.20.0 255.255.255.0 Null0')
        self.t['nodes'][1]['configuration'][0]['content']=self.c['CR-R1']
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_08_reject_nonexample_key(self):
        self.c['CR-R1']=self.c['CR-R1'].replace(v.PUBLIC_PSK,'not-the-demo-key')
        self.t['nodes'][1]['configuration'][0]['content']=self.c['CR-R1']
        with self.assertRaises(AssertionError): v.check_topology(self.t,self.c)
    def test_09_dated_evidence(self): self.assertTrue(v.check_proof(self.p,ROOT))
    def test_10_reject_fresh_run_claim(self):
        self.p['fresh_runtime_test_performed']=True
        with self.assertRaises(AssertionError): v.check_proof(self.p,ROOT)
    def test_11_reject_counter_change(self):
        self.p['counters']['r1']['after']['encaps']=70
        with self.assertRaises(AssertionError): v.check_proof(self.p,ROOT)
    def test_12_reject_evidence_hash_drift(self):
        self.p['observations'][0]['excerpt_sha256']='0'*64
        with self.assertRaises(AssertionError): v.check_proof(self.p,ROOT)
    def test_13_privacy_scan_clean(self): self.assertEqual(v.privacy_findings(ROOT),[])
    def test_14_privacy_rejects_runtime_spi(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'bad.txt').write_text('Local spi: AABBCCDDEEFF1122')
            self.assertTrue(v.privacy_findings(Path(d)))
    def test_15_privacy_rejects_private_link(self):
        with tempfile.TemporaryDirectory() as d:
            (Path(d)/'bad.txt').write_text('https://github.com/'+'example-private/source')
            self.assertTrue(v.privacy_findings(Path(d)))
    def test_16_full_package_integrity(self): self.assertTrue(v.verify(ROOT))
    def test_17_reject_missing_traffic_directions(self):
        self.p['traffic']={}
        with self.assertRaises(AssertionError): v.check_proof(self.p,ROOT)
    def test_18_reject_missing_router_counters(self):
        self.p['counters']={}
        with self.assertRaises(AssertionError): v.check_proof(self.p,ROOT)
if __name__=='__main__': unittest.main()
