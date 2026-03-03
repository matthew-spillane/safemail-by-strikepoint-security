import email
import email.utils
import re
from email import policy


SUSPICIOUS_TLDS = [".ru", ".cn", ".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz", ".buzz", ".click", ".link"]
URGENCY_KEYWORDS = [
    "urgent", "immediate", "action required", "act now", "expires", "suspended",
    "verify your", "confirm your", "update your", "click here", "limited time",
    "within 24 hours", "within 48 hours", "account will be", "unauthorized",
    "unusual activity", "security alert", "locked", "disabled", "compromised",
]
BRAND_KEYWORDS = [
    "paypal", "apple", "microsoft", "google", "amazon", "netflix", "facebook",
    "instagram", "twitter", "linkedin", "bank", "chase", "wellsfargo", "citibank",
    "dropbox", "adobe", "docusign", "fedex", "ups", "usps", "dhl", "irs",
    "walmart", "costco", "target", "bestbuy",
]
RISKY_EXTENSIONS = [
    ".exe", ".bat", ".cmd", ".com", ".scr", ".pif", ".msi", ".msp",
    ".vbs", ".vbe", ".js", ".jse", ".wsf", ".wsh", ".ps1",
    ".zip", ".rar", ".7z", ".tar", ".gz",
    ".docm", ".xlsm", ".pptm", ".dotm", ".xltm",
    ".iso", ".img", ".hta", ".cpl", ".dll",
]
SHORTENER_DOMAINS = [
    "bit.ly", "tinyurl.com", "t.co", "goo.gl", "ow.ly", "is.gd",
    "buff.ly", "adf.ly", "bl.ink", "lnkd.in", "rb.gy",
]


def analyze_eml(eml_text: str) -> dict:
    msg = email.message_from_string(eml_text, policy=policy.default)

    headers = extract_headers(msg)
    body = extract_body(msg)
    urls = extract_urls(body)
    attachments = extract_attachments(msg)
    auth_results = parse_authentication_results(msg)

    checks = []
    checks.append(check_spf(auth_results))
    checks.append(check_dkim(auth_results))
    checks.append(check_dmarc(auth_results))
    checks.append(check_from_reply_to_mismatch(headers))
    checks.append(check_display_name_spoofing(headers))
    checks.append(check_embedded_urls(urls))
    checks.append(check_attachment_risk(attachments))
    checks.append(check_header_path(msg))
    checks.append(check_subject_line(headers.get("subject", "")))

    passed = sum(1 for c in checks if c["status"] == "pass")
    warned = sum(1 for c in checks if c["status"] == "warn")
    failed = sum(1 for c in checks if c["status"] == "fail")
    skipped = sum(1 for c in checks if c["status"] == "skip")

    return {
        "from": headers.get("from", ""),
        "to": headers.get("to", ""),
        "reply_to": headers.get("reply-to", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
        "body_preview": body[:500] if body else "",
        "urls": urls,
        "attachments": attachments,
        "authentication": auth_results,
        "checks": checks,
        "summary": {
            "passed": passed,
            "warned": warned,
            "failed": failed,
            "skipped": skipped,
        },
    }


def extract_headers(msg) -> dict:
    headers = {}
    for key in ["from", "to", "reply-to", "subject", "date", "return-path"]:
        val = msg.get(key, "")
        headers[key] = str(val) if val else ""
    return headers


def extract_body(msg) -> str:
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    body += payload.decode("utf-8", errors="replace")
            elif ct == "text/html" and not body:
                payload = part.get_payload(decode=True)
                if payload:
                    html = payload.decode("utf-8", errors="replace")
                    body += strip_html(html)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            ct = msg.get_content_type()
            text = payload.decode("utf-8", errors="replace")
            if ct == "text/html":
                body = strip_html(text)
            else:
                body = text
    return body.strip()


def strip_html(html: str) -> str:
    text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<script[^>]*>.*?</script>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_urls(text: str) -> list[dict]:
    url_pattern = re.compile(r'https?://[^\s<>"\')\]]+', re.IGNORECASE)
    found = url_pattern.findall(text)
    urls = []
    seen = set()
    for url in found:
        url = url.rstrip(".,;:!?)")
        if url not in seen:
            seen.add(url)
            flags = analyze_url(url)
            urls.append({"url": url, "flags": flags, "suspicious": len(flags) > 0})
    return urls


def analyze_url(url: str) -> list[str]:
    flags = []
    lower = url.lower()

    for tld in SUSPICIOUS_TLDS:
        domain_part = re.search(r'https?://([^/]+)', lower)
        if domain_part and domain_part.group(1).endswith(tld):
            flags.append(f"Suspicious TLD: {tld}")
            break

    domain_match = re.search(r'https?://([^/]+)', lower)
    if domain_match:
        domain = domain_match.group(1)
        if re.match(r'^\d+\.\d+\.\d+\.\d+', domain):
            flags.append("IP address used instead of domain")
        for sd in SHORTENER_DOMAINS:
            if sd in domain:
                flags.append("URL shortener detected")
                break
        if domain.count(".") > 3:
            flags.append("Excessive subdomains")

    if "@" in url:
        flags.append("Contains @ symbol (potential redirect)")

    return flags


def extract_attachments(msg) -> list[dict]:
    attachments = []
    if msg.is_multipart():
        for part in msg.walk():
            filename = part.get_filename()
            if filename:
                ct = part.get_content_type()
                ext = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
                risky = ext in RISKY_EXTENSIONS
                attachments.append({
                    "filename": filename,
                    "content_type": ct,
                    "extension": ext,
                    "risky": risky,
                })
    return attachments


def parse_authentication_results(msg) -> dict:
    auth_header = str(msg.get("Authentication-Results", ""))
    results = {"spf": "none", "dkim": "none", "dmarc": "none", "raw": auth_header}

    if auth_header:
        spf_match = re.search(r'spf=(pass|fail|softfail|neutral|none|temperror|permerror)', auth_header, re.IGNORECASE)
        if spf_match:
            results["spf"] = spf_match.group(1).lower()

        dkim_match = re.search(r'dkim=(pass|fail|neutral|none|temperror|permerror)', auth_header, re.IGNORECASE)
        if dkim_match:
            results["dkim"] = dkim_match.group(1).lower()

        dmarc_match = re.search(r'dmarc=(pass|fail|bestguesspass|none|temperror|permerror)', auth_header, re.IGNORECASE)
        if dmarc_match:
            results["dmarc"] = dmarc_match.group(1).lower()

    return results


def check_spf(auth: dict) -> dict:
    spf = auth.get("spf", "none")
    if spf == "pass":
        return {"name": "SPF Authentication", "status": "pass", "detail": "SPF check passed — sender is authorized by the domain."}
    elif spf in ("fail", "softfail"):
        return {"name": "SPF Authentication", "status": "fail", "detail": f"SPF check returned '{spf}' — sender may not be authorized."}
    elif spf == "none":
        return {"name": "SPF Authentication", "status": "skip", "detail": "No SPF record found in authentication headers."}
    else:
        return {"name": "SPF Authentication", "status": "warn", "detail": f"SPF check returned '{spf}'."}


def check_dkim(auth: dict) -> dict:
    dkim = auth.get("dkim", "none")
    if dkim == "pass":
        return {"name": "DKIM Authentication", "status": "pass", "detail": "DKIM signature verified — message integrity confirmed."}
    elif dkim == "fail":
        return {"name": "DKIM Authentication", "status": "fail", "detail": "DKIM verification failed — message may have been tampered with."}
    elif dkim == "none":
        return {"name": "DKIM Authentication", "status": "skip", "detail": "No DKIM record found in authentication headers."}
    else:
        return {"name": "DKIM Authentication", "status": "warn", "detail": f"DKIM check returned '{dkim}'."}


def check_dmarc(auth: dict) -> dict:
    dmarc = auth.get("dmarc", "none")
    if dmarc == "pass":
        return {"name": "DMARC Authentication", "status": "pass", "detail": "DMARC policy evaluation passed."}
    elif dmarc == "fail":
        return {"name": "DMARC Authentication", "status": "fail", "detail": "DMARC evaluation failed — domain alignment issue detected."}
    elif dmarc == "none":
        return {"name": "DMARC Authentication", "status": "skip", "detail": "No DMARC record found in authentication headers."}
    else:
        return {"name": "DMARC Authentication", "status": "warn", "detail": f"DMARC check returned '{dmarc}'."}


def check_from_reply_to_mismatch(headers: dict) -> dict:
    from_addr = headers.get("from", "")
    reply_to = headers.get("reply-to", "")

    if not reply_to:
        return {"name": "From / Reply-To Mismatch", "status": "pass", "detail": "No Reply-To header set — replies go to the sender."}

    from_email = extract_email_address(from_addr)
    reply_email = extract_email_address(reply_to)

    if from_email and reply_email and from_email.lower() != reply_email.lower():
        from_domain = from_email.split("@")[-1] if "@" in from_email else ""
        reply_domain = reply_email.split("@")[-1] if "@" in reply_email else ""
        if from_domain.lower() != reply_domain.lower():
            return {
                "name": "From / Reply-To Mismatch",
                "status": "fail",
                "detail": f"Reply-To ({reply_email}) uses a different domain than From ({from_email}). This is a common phishing indicator.",
            }
        return {
            "name": "From / Reply-To Mismatch",
            "status": "warn",
            "detail": f"Reply-To ({reply_email}) differs from From ({from_email}), though domains match.",
        }

    return {"name": "From / Reply-To Mismatch", "status": "pass", "detail": "From and Reply-To addresses match."}


def check_display_name_spoofing(headers: dict) -> dict:
    from_header = headers.get("from", "")
    display_name, email_addr = "", ""

    match = re.match(r'^"?([^"<]+)"?\s*<([^>]+)>', from_header)
    if match:
        display_name = match.group(1).strip().lower()
        email_addr = match.group(2).strip().lower()
    else:
        email_addr = extract_email_address(from_header).lower() if from_header else ""

    if not display_name:
        return {"name": "Display Name Spoofing", "status": "pass", "detail": "No display name set — no spoofing risk."}

    domain = email_addr.split("@")[-1] if "@" in email_addr else ""

    for brand in BRAND_KEYWORDS:
        if brand in display_name and brand not in domain:
            return {
                "name": "Display Name Spoofing",
                "status": "warn",
                "detail": f"Display name contains '{brand}' but the sender domain is '{domain}'. Possible brand impersonation.",
            }

    return {"name": "Display Name Spoofing", "status": "pass", "detail": "Display name does not appear to impersonate a known brand."}


def check_embedded_urls(urls: list[dict]) -> dict:
    if not urls:
        return {"name": "Embedded URL Analysis", "status": "pass", "detail": "No URLs found in the email body."}

    suspicious = [u for u in urls if u["suspicious"]]
    total = len(urls)

    if suspicious:
        flag_summary = "; ".join(
            f"{u['url'][:60]}... — {', '.join(u['flags'])}" if len(u["url"]) > 60
            else f"{u['url']} — {', '.join(u['flags'])}"
            for u in suspicious[:5]
        )
        return {
            "name": "Embedded URL Analysis",
            "status": "fail" if len(suspicious) > 1 else "warn",
            "detail": f"Found {len(suspicious)} suspicious URL(s) out of {total} total. {flag_summary}",
        }

    return {"name": "Embedded URL Analysis", "status": "pass", "detail": f"All {total} URL(s) appear benign."}


def check_attachment_risk(attachments: list[dict]) -> dict:
    if not attachments:
        return {"name": "Attachment Risk", "status": "pass", "detail": "No attachments found."}

    risky = [a for a in attachments if a["risky"]]
    if risky:
        names = ", ".join(a["filename"] for a in risky)
        return {
            "name": "Attachment Risk",
            "status": "fail",
            "detail": f"Risky attachment(s) detected: {names}. These file types can contain malware or macros.",
        }

    names = ", ".join(a["filename"] for a in attachments)
    return {"name": "Attachment Risk", "status": "pass", "detail": f"Attachment(s) found ({names}) with no high-risk file types."}


def check_header_path(msg) -> dict:
    received_headers = msg.get_all("Received", [])
    if not received_headers:
        return {"name": "Header Path Analysis", "status": "skip", "detail": "No Received headers found to analyze."}

    flags = []
    hop_count = len(received_headers)

    if hop_count > 8:
        flags.append(f"Unusually high number of hops ({hop_count})")

    for h in received_headers:
        h_str = str(h).lower()
        if re.search(r'\b(?:\d{1,3}\.){3}\d{1,3}\b', h_str):
            ip_match = re.search(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', h_str)
            if ip_match:
                ip = ip_match.group(1)
                if ip.startswith(("10.", "192.168.", "127.")):
                    continue
                for tld in SUSPICIOUS_TLDS:
                    if tld[1:] in h_str:
                        flags.append(f"Header references suspicious domain ({tld})")
                        break

    if flags:
        return {
            "name": "Header Path Analysis",
            "status": "warn",
            "detail": "Potential issues in mail routing: " + "; ".join(flags),
        }

    return {
        "name": "Header Path Analysis",
        "status": "pass",
        "detail": f"Email passed through {hop_count} hop(s) with no suspicious routing detected.",
    }


def check_subject_line(subject: str) -> dict:
    if not subject:
        return {"name": "Subject Line Analysis", "status": "skip", "detail": "No subject line found."}

    flags = []
    lower = subject.lower()

    for keyword in URGENCY_KEYWORDS:
        if keyword in lower:
            flags.append(f"Urgency keyword: '{keyword}'")
            break

    if subject == subject.upper() and len(subject) > 5:
        flags.append("Subject is in ALL CAPS")

    excl_count = subject.count("!")
    quest_count = subject.count("?")
    if excl_count >= 3 or quest_count >= 3:
        flags.append("Excessive punctuation")

    if re.search(r'RE:|FW:', subject) and not re.search(r'^(RE|FW):', subject, re.IGNORECASE):
        flags.append("Fake reply/forward prefix")

    if flags:
        return {
            "name": "Subject Line Analysis",
            "status": "warn",
            "detail": f"Subject line flags: {'; '.join(flags)}",
        }

    return {"name": "Subject Line Analysis", "status": "pass", "detail": "Subject line appears normal."}


def extract_email_address(text: str) -> str:
    match = re.search(r'[\w.+-]+@[\w.-]+\.\w+', text)
    return match.group(0) if match else ""
