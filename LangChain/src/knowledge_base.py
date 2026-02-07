knowledge_base = {
    "reset_password": {
        "title": "Reset Password",
        "summary": "Steps to reset a forgotten or compromised password.",
        "steps": [
            "Go to the login page.",
            "Click on 'Forgot Password'.",
            "Enter your registered email address.",
            "Check your email for the reset link.",
            "Create a new password and confirm.",
            "Login with your new password."
        ],
        "common_issues": {
            "no_email_received": "Check spam folder or verify email address.",
            "expired_link": "Request a new password reset link."
        }
    },

    "api_limits": {
        "title": "API Usage Limits",
        "summary": "Information about rate limits and usage quotas.",
        "limits": {
            "requests_per_minute": 60,
            "tokens_per_day": 100000
        },
        "best_practices": [
            "Implement request throttling.",
            "Cache frequent responses.",
            "Monitor usage metrics."
        ],
        "errors": {
            "429": "Rate limit exceeded. Retry after cooldown."
        }
    },

    "billing": {
        "title": "Billing & Payments",
        "summary": "Manage subscriptions, invoices, and payment methods.",
        "features": [
            "View invoices",
            "Update payment method",
            "Upgrade or downgrade plan",
            "Cancel subscription"
        ],
        "payment_methods": [
            "Credit Card",
            "Debit Card",
            "UPI"
        ],
        "faq": {
            "Where can I see invoices?": "Invoices are available in Account → Billing.",
            "What happens if payment fails?": "Account may be suspended after grace period."
        }
    }
}

def search_kb(query: str) -> str:
    query = query.lower()
    hits = []

    for k, v in knowledge_base.items():
        if query in k or query in v.lower():
            hits.append(f"[{k}] {v}")

    return "/n".join(hits) if hits else "No relevant KB entry found."
