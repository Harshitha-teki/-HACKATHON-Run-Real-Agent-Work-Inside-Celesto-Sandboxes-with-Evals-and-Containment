from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import psycopg2
from typing import Optional

app = FastAPI()

class RunCreate(BaseModel):
    run_id: str
    sandbox_name: str
    problem_id: str
    state: str
    execution_target: str

def get_conn():
    db_url = os.environ.get("DATABASE_URL", "postgresql://ledger:ledger@ledger:5432/ledger")
    return psycopg2.connect(db_url)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/api/runs")
def get_runs():
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("SELECT run_id, sandbox_name, problem_id, state, execution_target FROM runs ORDER BY id")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        result = []
        for r in rows:
            result.append({
                "run_id": r[0],
                "sandbox_name": r[1],
                "problem_id": r[2],
                "state": r[3],
                "execution_target": r[4]
            })
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/runs", status_code=201)
def create_run(run: RunCreate):
    import re
    if run.execution_target != "celesto_sandbox":
        raise HTTPException(status_code=400, detail="bad execution_target")
    valid_states = {"created", "ready", "running", "succeeded", "failed", "deleted"}
    if run.state not in valid_states:
        raise HTTPException(status_code=400, detail="bad state")
    if not re.match(r"^sbx-[a-z0-9]{8,}$", run.sandbox_name):
        raise HTTPException(status_code=400, detail="bad sandbox_name")
    try:
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO runs (run_id, sandbox_name, problem_id, state, execution_target) VALUES (%s,%s,%s,%s,%s)",
            (run.run_id, run.sandbox_name, run.problem_id, run.state, run.execution_target)
        )
        conn.commit()
        cur.close()
        conn.close()
        return {
            "run_id": run.run_id,
            "sandbox_name": run.sandbox_name,
            "problem_id": run.problem_id,
            "state": run.state,
            "execution_target": run.execution_target
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))