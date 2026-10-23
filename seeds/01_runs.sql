CREATE TABLE IF NOT EXISTS runs (
  id SERIAL PRIMARY KEY,
  run_id VARCHAR(255),
  sandbox_name VARCHAR(64),
  problem_id VARCHAR(64),
  state VARCHAR(32),
  execution_target VARCHAR(64),
  created_at TIMESTAMP DEFAULT NOW()
);

INSERT INTO runs (run_id, sandbox_name, problem_id, state, execution_target)
VALUES ('seed-demo', 'sbx-seeddemo1', 'seed', 'deleted', 'celesto_sandbox')
ON CONFLICT DO NOTHING;