test:
	python -m pytest -q

all:
	python -m pytest -q
	python -m reviewer eval --impl final --set all --out results/final
	python -m reviewer ablate --name sampled_vs_exhaustive --out results/ablation
