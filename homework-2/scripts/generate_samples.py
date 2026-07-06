"""Generate sample ticket files for homework-2."""

import csv
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

SUBJECTS = {
    "account_access": ("Cannot login to account", "I forgot my password and cannot sign in to my account."),
    "billing_question": ("Invoice question", "I was charged twice on my latest invoice and need a refund."),
    "technical_issue": ("Application crash", "The app crashes with an error when I open settings."),
    "feature_request": ("Feature suggestion", "It would be great to add dark mode support to the dashboard."),
    "bug_report": ("Bug report with steps", "Bug report: steps to reproduce the checkout failure on mobile."),
    "other": ("General inquiry", "I have a general question about your service availability."),
}

PRIORITIES = ["urgent", "high", "medium", "low"]
STATUSES = ["new", "in_progress", "waiting_customer", "resolved", "closed"]


def ticket(index: int, category: str) -> dict:
    subject, description = SUBJECTS[category]
    return {
        "customer_id": f"cust-{index:03d}",
        "customer_email": f"user{index}@example.com",
        "customer_name": f"User {index}",
        "subject": f"{subject} #{index}",
        "description": f"{description} Ticket reference {index}.",
        "category": category,
        "priority": PRIORITIES[index % len(PRIORITIES)],
        "status": STATUSES[index % len(STATUSES)],
        "assigned_to": f"agent-{index % 5}" if index % 3 == 0 else "",
        "tags": f"tag{index % 4},support",
        "metadata_source": ["web_form", "email", "api", "chat", "phone"][index % 5],
        "metadata_browser": ["Chrome", "Firefox", "Safari"][index % 3],
        "metadata_device_type": ["desktop", "mobile", "tablet"][index % 3],
        "auto_classify": "false",
    }


def write_csv(count: int, path: Path) -> None:
    rows = []
    categories = list(SUBJECTS.keys())
    for i in range(1, count + 1):
        rows.append(ticket(i, categories[i % len(categories)]))
    headers = list(rows[0].keys())
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)


def write_json(count: int, path: Path) -> None:
    categories = list(SUBJECTS.keys())
    tickets = [ticket(i, categories[i % len(categories)]) for i in range(1, count + 1)]
    payload = {"tickets": tickets}
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def write_xml(count: int, path: Path) -> None:
    categories = list(SUBJECTS.keys())
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', "<tickets>"]
    for i in range(1, count + 1):
        t = ticket(i, categories[i % len(categories)])
        lines.extend(
            [
                "  <ticket>",
                f"    <customer_id>{t['customer_id']}</customer_id>",
                f"    <customer_email>{t['customer_email']}</customer_email>",
                f"    <customer_name>{t['customer_name']}</customer_name>",
                f"    <subject>{t['subject']}</subject>",
                f"    <description>{t['description']}</description>",
                f"    <category>{t['category']}</category>",
                f"    <priority>{t['priority']}</priority>",
                f"    <status>{t['status']}</status>",
                f"    <assigned_to>{t['assigned_to']}</assigned_to>",
                "    <tags>",
                "      <tag>support</tag>",
                f"      <tag>tag{i % 4}</tag>",
                "    </tags>",
                "    <metadata>",
                f"      <source>{t['metadata_source']}</source>",
                f"      <browser>{t['metadata_browser']}</browser>",
                f"      <device_type>{t['metadata_device_type']}</device_type>",
                "    </metadata>",
                f"    <auto_classify>{t['auto_classify']}</auto_classify>",
                "  </ticket>",
            ]
        )
    lines.append("</tickets>")
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    write_csv(50, ROOT / "sample_tickets.csv")
    write_json(20, ROOT / "sample_tickets.json")
    write_xml(30, ROOT / "sample_tickets.xml")
    print("Generated sample files.")
