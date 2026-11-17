[REQ-1] If category is missing, route to manual_review.
[REQ-2] If the ticket is urgent, route to priority_queue.
[REQ-3] If waiting time is at least 30 minutes, route to escalation.
[REQ-5] If customer tier is vip and waiting time is at least 15 minutes, route to escalation.
[REQ-6] If urgent and category is security, route to security_queue.
[REQ-4] All remaining tickets go to normal_queue.
