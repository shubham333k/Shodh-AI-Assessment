def route(ticket):
    if ticket.get("category") is None:
        return "manual_review"
    elif ticket.get("urgent") is True:
        return "priority_queue"
    elif ticket.get("waiting_time") is not None and ticket.get("waiting_time") >= 30:
        return "escalation"
    else:
        return "normal_queue"
