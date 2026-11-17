from fractions import Fraction
from reviewer.lang.units import normalise_time
from reviewer.lang.nl_parser import parse_requirement
from reviewer.lang.evaluator import evaluate
from reviewer.lang.cond_ast import Cmp, IsMissing
from reviewer.report.status import decide
from reviewer.ingest.loader import load_bundle

def test_exact_time_conversion():
    assert normalise_time("0.5", "hours") == Fraction(30)

def test_missing_comparison_is_false():
    assert not evaluate(Cmp("waiting_time", ">=", Fraction(30), "minutes"), {})
    assert evaluate(IsMissing("category"), {"category": " "})

def test_parser_boundary():
    parsed = parse_requirement("if waiting time is at least 30 minutes, route to escalation")
    assert parsed.status == "PARSED"
    assert evaluate(parsed.condition, {"waiting_time": 30})

def test_status_incomplete_for_coverage():
    assert decide([], {"unsupported": [{"anchor": "REQ-1"}], "ambiguous": [], "approval_conflicts": [], "unreviewed": [], "verification_mode": "exhaustive"}, []) == "INCOMPLETE"

def test_sample_bundle_loads():
    bundle = load_bundle("data/bundles/D01")
    assert bundle["manifest"]["bundle_id"] == "D01"
    assert len(bundle["requirements"]) == 4
