from typing import Dict


def classify_ticket(question: str) -> Dict:
    question_lower = question.lower()

    category_scores = {
        "VPN Connectivity": 0,
        "Account Access": 0,
        "Multi-Factor Authentication": 0,
        "General IT Support": 1,
    }

    team_mapping = {
        "VPN Connectivity": "Network Support",
        "Account Access": "Identity and Access Management",
        "Multi-Factor Authentication": "Identity and Access Management",
        "General IT Support": "Service Desk",
    }

    # VPN-related signals
    if any(keyword in question_lower for keyword in ["vpn", "network", "connect", "connection"]):
        category_scores["VPN Connectivity"] += 3

    # Account-related signals
    if any(keyword in question_lower for keyword in ["password", "locked", "login", "sign in", "account"]):
        category_scores["Account Access"] += 2

    # MFA-related signals
    if any(keyword in question_lower for keyword in ["duo", "mfa", "authentication", "push"]):
        category_scores["Multi-Factor Authentication"] += 3

    category = max(category_scores, key=category_scores.get)
    assigned_team = team_mapping[category]
    priority = predict_priority(question_lower)

    return {
        "summary": generate_summary(question),
        "category": category,
        "priority": priority,
        "assigned_team": assigned_team,
    }


def predict_priority(question_lower: str) -> str:
    if any(keyword in question_lower for keyword in ["outage", "down", "production", "company-wide"]):
        return "Critical"

    if any(keyword in question_lower for keyword in ["multiple users", "department", "team blocked"]):
        return "High"

    if any(keyword in question_lower for keyword in ["cannot", "unable", "not working", "blocked", "failed"]):
        return "Medium"

    return "Low"


def generate_summary(question: str) -> str:
    question = question.strip()

    if len(question) <= 80:
        return question

    return question[:77] + "..."


if __name__ == "__main__":
    test_questions = [
        "My VPN is not working after I reset my password",
        "I cannot approve Duo push notifications",
        "My account is locked",
        "Company-wide authentication failure",
        "Multiple users cannot access VPN",
    ]

    for question in test_questions:
        print("\nQuestion:", question)
        print(classify_ticket(question))