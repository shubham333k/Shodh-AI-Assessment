$ErrorActionPreference = "Stop"
$python = "C:/Users/shubh/AppData/Local/Python/pythoncore-3.14-64/python.exe"
& $python -m pytest -q
& $python -m reviewer eval --impl final --set all --out results/final
& $python -m reviewer ablate --name sampled_vs_exhaustive --out results/ablation
Write-Output "Completed. Reports: results/final; ablation: results/ablation."
