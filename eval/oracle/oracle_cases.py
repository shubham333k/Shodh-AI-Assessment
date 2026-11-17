"""Independent reference routes for evaluation. Imports nothing from reviewer."""
def route(ticket, threshold=30, vip=False, security=False):
    if ticket.get("category") is None or (isinstance(ticket.get("category"), str) and not ticket["category"].strip()): return "manual_review"
    if ticket.get("urgent") is True: return "priority_queue"
    if vip and ticket.get("customer_tier") == "vip" and ticket.get("waiting_time") is not None and ticket["waiting_time"] >= 15: return "escalation"
    if security and ticket.get("category") == "security" and ticket.get("urgent") is True: return "security_queue"
    if ticket.get("waiting_time") is not None and ticket["waiting_time"] >= threshold: return "escalation"
    return "normal_queue"

def expected_route(bundle_id, ticket):
    if bundle_id == "D03" or bundle_id == "H04": return route(ticket, 25, bundle_id == "H04", False)
    return route(ticket, 30, bundle_id in ("D09", "H03"), bundle_id in ("H03",))
