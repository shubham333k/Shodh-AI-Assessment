<<<<<<< HEAD
# Shodh-AI-Assessment
=======
# Shodh AI workflow reviewer

This repository implements the deterministic reviewer and evaluation harness described in `IMPLEMENTATION_PLAN.md`. It reviews support-ticket routing requirements and compares them with versioned JSON specs using exact `Fraction` arithmetic. Unsupported and ambiguous requirements remain in coverage; Python artifact code is parsed with `ast` and is never executed.

## Run

Python 3.11+ is required. Install with `pip install -r requirements.txt` and `pip install -e .`, then run `pytest -q`.

Review a bundle with PowerShell (run each line separately):

```powershell
$py = "C:\Users\shubh\AppData\Local\Python\pythoncore-3.14-64\python.exe"
& $py -m reviewer review data/bundles/D01 --model none --out report.json
Get-Content .\report.json
```

Run the full offline evaluation and ablation with `powershell -ExecutionPolicy Bypass -File .\run_all.ps1`. If running manually, keep each command on its own line (or separate commands with `;`). Export schemas with `& $py -m reviewer schema --export schemas`.

Workflow and supported Python snippets are checked alongside the spec. The model interface is advisory only and cannot change a deterministic status. Offline results do not measure real-model performance; configure `SHODH_MODEL_ENDPOINT`, `SHODH_MODEL_KEY`, and optional `SHODH_MODEL` only when using `--model real`.
>>>>>>> e071e4c (Complete Shodh AI workflow reviewer)
