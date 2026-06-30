"""
Email digest — generate HTML and send via Gmail SMTP
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from typing import List, Dict

from config import GMAIL_ADDRESS, GMAIL_PASSWORD, EMAIL_CONFIG

logger = logging.getLogger(__name__)


class EmailDigest:

    def generate_html(self, jobs: List[Dict], total_count: int) -> str:
        today = datetime.now().strftime("%A, %d %B %Y")

        job_rows = ""
        for job in jobs:
            score = job.get("relevance_score", 0)
            score_color = "#27ae60" if score >= 30 else "#e67e22" if score >= 15 else "#7f8c8d"
            job_rows += f"""
            <tr>
              <td style="padding:12px 8px;border-bottom:1px solid #E9EDF2;">
                <a href="{job.get('url','')}" style="color:#4D5A94;font-weight:600;text-decoration:none;">
                  {job.get('title','Untitled')}
                </a>
              </td>
              <td style="padding:12px 8px;border-bottom:1px solid #E9EDF2;color:#555;">{job.get('company','')}</td>
              <td style="padding:12px 8px;border-bottom:1px solid #E9EDF2;color:#555;">{job.get('sector','')}</td>
              <td style="padding:12px 8px;border-bottom:1px solid #E9EDF2;text-align:center;">
                <span style="background:{score_color};color:#fff;padding:2px 8px;border-radius:12px;font-size:12px;font-weight:700;">
                  {score}
                </span>
              </td>
            </tr>"""

        return f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;background:#f5f7fa;">
  <table width="100%" cellpadding="0" cellspacing="0" style="max-width:700px;margin:24px auto;">
    <tr>
      <td style="background:#4D5A94;padding:28px 32px;border-radius:8px 8px 0 0;">
        <h1 style="margin:0;color:#fff;font-size:22px;font-weight:700;">ASX Jobs Digest</h1>
        <p style="margin:6px 0 0;color:#9EB7DA;font-size:14px;">{today}</p>
      </td>
    </tr>
    <tr>
      <td style="background:#fff;padding:24px 32px;">
        <p style="margin:0 0 20px;color:#333;font-size:15px;">
          Found <strong style="color:#4D5A94;">{total_count} matching jobs</strong> across ASX 50 companies today.
          Showing top {len(jobs)}.
        </p>
        <table width="100%" cellpadding="0" cellspacing="0" style="border-collapse:collapse;">
          <thead>
            <tr style="background:#E9EDF2;">
              <th style="padding:10px 8px;text-align:left;font-size:12px;color:#666;font-weight:600;">ROLE</th>
              <th style="padding:10px 8px;text-align:left;font-size:12px;color:#666;font-weight:600;">COMPANY</th>
              <th style="padding:10px 8px;text-align:left;font-size:12px;color:#666;font-weight:600;">SECTOR</th>
              <th style="padding:10px 8px;text-align:center;font-size:12px;color:#666;font-weight:600;">SCORE</th>
            </tr>
          </thead>
          <tbody>{job_rows}</tbody>
        </table>
      </td>
    </tr>
    <tr>
      <td style="background:#E9EDF2;padding:16px 32px;border-radius:0 0 8px 8px;text-align:center;">
        <p style="margin:0;color:#888;font-size:12px;">
          ASX Job Scraper · Automated daily digest ·
          <a href="mailto:{GMAIL_ADDRESS}" style="color:#4D5A94;">Unsubscribe</a>
        </p>
      </td>
    </tr>
  </table>
</body>
</html>"""

    def send(self, recipient: str, jobs: List[Dict], total_count: int) -> bool:
        if not GMAIL_ADDRESS or not GMAIL_PASSWORD:
            logger.error("GMAIL_ADDRESS and GMAIL_PASSWORD not configured")
            return False

        html = self.generate_html(jobs, total_count)
        today = datetime.now().strftime("%d %b %Y")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"ASX Jobs Digest — {len(jobs)} roles — {today}"
        msg["From"] = GMAIL_ADDRESS
        msg["To"] = recipient
        msg.attach(MIMEText(html, "html"))

        try:
            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
                smtp.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
                smtp.sendmail(GMAIL_ADDRESS, recipient, msg.as_string())
            logger.info(f"✓ Email sent to {recipient}")
            return True
        except Exception as e:
            logger.error(f"✗ Email send failed: {e}")
            return False
