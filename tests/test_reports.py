import json
import os

def test_problem_json():
    with open('reports/problem.json') as f:
        d = json.load(f)
    assert len(d['who']) >= 40
    assert len(d['agent_work']) >= 40
    assert len(d['proof_output']) >= 20
    assert d['idea_source'] in ['idea_bank', 'original']

def test_capabilities():
    with open('reports/capabilities.json') as f:
        d = json.load(f)
    caps = d['capabilities']
    assert len(caps) >= 2
    ids = [c['id'] for c in caps]
    assert len(ids) == len(set(ids))
    allowed = {'persistence','snapshots','celestofs','browser','published_ports','network_policy','safety_hooks','host_mounts','coding_agent_preset','agentor_durable'}
    for c in caps:
        assert c['id'] in allowed
        assert len(c['why']) >= 80
        assert os.path.exists(c['evidence_path'])

def test_lifecycle():
    with open('reports/lifecycle.json') as f:
        d = json.load(f)
    assert d['cleanup_on_success'] is True
    assert d['cleanup_on_failure'] is True
    assert d['cleanup_on_interrupt'] is True
    assert len(d['sandbox_names']) > 0
    assert len(set(d['sandbox_names'])) == len(d['sandbox_names'])

def test_commands_log():
    with open('logs/commands.jsonl') as f:
        for line in f:
            if line.strip():
                obj = json.loads(line)
                assert obj['execution_target'] == 'celesto_sandbox'
                assert obj['decision'] in ['allow', 'block']
                assert obj['command']

def test_reliability():
    with open('reports/reliability.json') as f:
        d = json.load(f)
    assert d['run_count'] >= 20
    assert len(d['runs']) == d['run_count']
    # check stats
    import math
    runs = d['runs']
    for r in runs:
        assert r['fresh'] is True
        assert isinstance(r['success'], bool)
    success_rate = sum(1 for r in runs if r['success'])/len(runs)
    assert abs(success_rate - d['success_rate']) < 0.001
    ws = sorted([r['wall_clock_s'] for r in runs])
    n = len(ws)
    if n % 2 == 1:
        med = ws[n//2]
    else:
        med = (ws[n//2-1]+ws[n//2])/2
    assert abs(med - d['median_wall_clock_s']) < 0.001
    p90 = ws[math.ceil(0.9*n)-1]
    assert abs(p90 - d['p90_wall_clock_s']) < 0.001
    bs = sorted([r['boot_to_ready_s'] for r in runs])
    if n % 2 == 1:
        medb = bs[n//2]
    else:
        medb = (bs[n//2-1]+bs[n//2])/2
    assert abs(medb - d['median_boot_to_ready_s']) < 0.001
    total = sum(r['cost_usd'] for r in runs)
    assert abs(total - d['total_cost_usd']) < 0.01
    assert os.path.exists(d['postmortem_path'])
    assert os.path.getsize(d['postmortem_path']) >= 200