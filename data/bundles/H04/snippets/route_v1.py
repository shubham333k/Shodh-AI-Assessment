def route(ticket):
    if ticket.get("category") is None:
        return "manual_review"
    elif ticket.get("urgent") is True:
        return "priority_queue"
    elif ticket.get("customer_tier") == "vip" and ticket.get("waiting_time") is not None and ticket.get("waiting_time") >= 15:
        return "escalation"
    elif ticket.get("waiting_time") is not None and ticket.get("waiting_time") >= 25:
        return "escalation"
    else:
        return "normal_queue"
