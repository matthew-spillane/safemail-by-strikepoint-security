import os
import json
import anthropic


def get_ai_verdict(analysis: dict) -> dict:
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        return {
            "verdict": "Unknown",
            "confidence": "N/A",
            "explanation": "AI analysis unavailable — ANTHROPIC_API_KEY not configured.",
        }

    checks_summary = []
    for check in analysis.get("checks", []):
        checks_summary.append(f"- {check['name']}: {check['status'].upper()} — {check['detail']}")

    urls_summary = ""
    urls = analysis.get("urls", [])
    if urls:
        url_lines = []
        for u in urls[:10]:
            flags = ", ".join(u["flags"]) if u["flags"] else "no flags"
            url_lines.append(f"  - {u['url'][:100]} ({flags})")
        urls_summary = "Embedded URLs:\n" + "\n".join(url_lines)

    attachments_summary = ""
    attachments = analysis.get("attachments", [])
    if attachments:
        att_lines = [f"  - {a['filename']} ({a['content_type']}, risky={a['risky']})" for a in attachments]
        attachments_summary = "Attachments:\n" + "\n".join(att_lines)

    prompt = f"""You are a senior email security analyst at Strikepoint Security. Analyze the following email data and provide a phishing assessment.

Email Details:
- From: {analysis.get('from', 'N/A')}
- To: {analysis.get('to', 'N/A')}
- Reply-To: {analysis.get('reply_to', 'N/A') or 'Not set'}
- Subject: {analysis.get('subject', 'N/A')}
- Date: {analysis.get('date', 'N/A')}

Body Preview:
{analysis.get('body_preview', 'N/A')[:1000]}

Authentication Results:
- SPF: {analysis.get('authentication', {}).get('spf', 'none')}
- DKIM: {analysis.get('authentication', {}).get('dkim', 'none')}
- DMARC: {analysis.get('authentication', {}).get('dmarc', 'none')}

Security Check Results:
{chr(10).join(checks_summary)}

{urls_summary}

{attachments_summary}

Based on this analysis, provide your assessment in the following JSON format:
{{
  "verdict": "<one of: Safe, Suspicious, Likely Phishing, Phishing>",
  "confidence": "<one of: Low, Medium, High>",
  "explanation": "<2-4 sentences explaining your findings in plain English, as a security analyst would explain to a non-technical user>"
}}

Respond ONLY with the JSON object, no other text."""

    try:
        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}],
        )
        response_text = message.content[0].text.strip()

        # Parse JSON from response
        json_match = response_text
        if "```" in response_text:
            lines = response_text.split("```")
            for block in lines:
                block = block.strip()
                if block.startswith("json"):
                    block = block[4:].strip()
                if block.startswith("{"):
                    json_match = block
                    break

        result = json.loads(json_match)
        return {
            "verdict": result.get("verdict", "Unknown"),
            "confidence": result.get("confidence", "Medium"),
            "explanation": result.get("explanation", "Analysis completed."),
        }
    except json.JSONDecodeError:
        return {
            "verdict": "Suspicious",
            "confidence": "Low",
            "explanation": f"AI analysis completed but response parsing failed. Raw: {response_text[:200]}",
        }
    except Exception as e:
        return {
            "verdict": "Unknown",
            "confidence": "N/A",
            "explanation": f"AI analysis failed: {str(e)}",
        }
