import os
import json
import requests
import sys

def notify_slack():
    slack_webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    if not slack_webhook_url:
        print("Skipping Slack notification: SLACK_WEBHOOK_URL not set.")
        return

    try:
        with open("ragas_results.json", "r") as f:
            results = json.load(f)
    except FileNotFoundError:
        print("Error: ragas_results.json not found. Run eval_ragas.py first.")
        sys.exit(1)

    # Calculate averages for the summary
    if not results:
        print("No results to report.")
        return

    # Assuming results is a list of records based on orient="records"
    # We need to compute the average of the metrics
    metrics = ["context_precision", "context_recall", "faithfulness", "answer_relevancy"]
    averages = {m: 0.0 for m in metrics}
    count = len(results)

    for row in results:
        for m in metrics:
            if m in row:
                averages[m] += row[m]
    
    msg_blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":chart_with_upwards_trend: Ragas Evaluation Results",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Total Test Cases:* {count}"
            }
        },
        {
            "type": "divider"
        }
    ]

    for m in metrics:
        avg_score = averages[m] / count if count > 0 else 0
        msg_blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{m.replace('_', ' ').title()}*: {avg_score:.4f}"
            }
        })

    payload = {"blocks": msg_blocks}
    
    response = requests.post(slack_webhook_url, json=payload)
    if response.status_code != 200:
        print(f"Failed to send Slack notification: {response.status_code} {response.text}")
    else:
        print("Slack notification sent successfully.")

if __name__ == "__main__":
    notify_slack()
