"""
app/services/email_service.py
──────────────────────────────
Full transactional email service — all lifecycle events, no markdown asterisks.
"""

from __future__ import annotations

import structlog
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional

import aiosmtplib

from app.core.config import settings

logger = structlog.get_logger()

BASE_URL = "https://applivo.in"
SUPPORT_EMAIL = "support@applivo.in"
BRAND = "#0f0f0f"


# ── Layout primitives ──────────────────────────────────────────────────────────

def _wrap(content: str, preheader: str = "") -> str:
    return f"""<!DOCTYPE html>
<html lang="en">
<head><meta charset="UTF-8"/><meta name="viewport" content="width=device-width,initial-scale=1.0"/></head>
<body style="margin:0;padding:0;background:#f4f4f5;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
<span style="display:none;max-height:0;overflow:hidden;">{preheader}</span>
<table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f4f5;padding:40px 16px;">
<tr><td align="center">
<table width="560" cellpadding="0" cellspacing="0" style="max-width:560px;width:100%;">
  <tr><td style="background:#0f0f0f;border-radius:12px 12px 0 0;padding:24px 40px;text-align:center;">
    <span style="font-size:20px;font-weight:900;color:#fff;letter-spacing:-0.5px;">APPLIVO</span>
  </td></tr>
  <tr><td style="background:#fff;padding:40px;border-radius:0 0 12px 12px;border:1px solid #e4e4e7;border-top:none;">
    {content}
  </td></tr>
  <tr><td style="padding:20px 0;text-align:center;">
    <p style="margin:0;font-size:11px;color:#a1a1aa;line-height:1.8;">
      You received this because you have an Applivo account.<br/>
      <a href="{BASE_URL}/settings" style="color:#71717a;">Manage notifications</a> &middot;
      <a href="{BASE_URL}" style="color:#71717a;">applivo.in</a> &middot;
      <a href="mailto:{SUPPORT_EMAIL}" style="color:#71717a;">{SUPPORT_EMAIL}</a>
    </p>
  </td></tr>
</table>
</td></tr></table>
</body></html>"""


def _h1(text: str) -> str:
    return f'<h1 style="margin:0 0 8px;font-size:26px;font-weight:900;color:#0f0f0f;letter-spacing:-0.5px;">{text}</h1>'

def _p(text: str, color: str = "#52525b") -> str:
    return f'<p style="margin:0 0 16px;font-size:15px;color:{color};line-height:1.7;">{text}</p>'

def _small(text: str) -> str:
    return f'<p style="margin:0 0 8px;font-size:13px;color:#71717a;line-height:1.6;">{text}</p>'

def _hr() -> str:
    return '<hr style="border:none;border-top:1px solid #f0f0f0;margin:28px 0;"/>'

def _btn(label: str, url: str, bg: str = "#0f0f0f") -> str:
    return f'<a href="{url}" style="display:inline-block;background:{bg};color:#fff;font-size:14px;font-weight:700;padding:13px 28px;border-radius:8px;text-decoration:none;">{label}</a>'

def _tag(label: str, fg: str = "#0f0f0f", bg: str = "#f4f4f5") -> str:
    return f'<span style="display:inline-block;background:{bg};color:{fg};font-size:10px;font-weight:700;letter-spacing:0.1em;text-transform:uppercase;padding:3px 10px;border-radius:100px;margin-bottom:10px;">{label}</span>'

def _stat_row(stats: list[tuple[str, str]]) -> str:
    cells = "".join(
        f'<td style="text-align:center;padding:16px 12px;background:#f9f9f9;border-radius:8px;">'
        f'<div style="font-size:24px;font-weight:900;color:#0f0f0f;">{v}</div>'
        f'<div style="font-size:10px;color:#71717a;margin-top:2px;text-transform:uppercase;letter-spacing:0.05em;">{l}</div>'
        f'</td><td width="8"></td>'
        for v, l in stats
    )
    return f'<table cellpadding="0" cellspacing="0" width="100%"><tr>{cells}</tr></table>'

def _kv_table(rows: list[tuple[str, str]]) -> str:
    inner = "".join(
        f'<tr><td style="padding:9px 0;font-size:13px;color:#71717a;border-bottom:1px solid #f4f4f5;">{k}</td>'
        f'<td style="padding:9px 0;font-size:13px;font-weight:600;color:#0f0f0f;text-align:right;border-bottom:1px solid #f4f4f5;">{v}</td></tr>'
        for k, v in rows
    )
    return f'<table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:4px;">{inner}</table>'

def _bullets(items: list[str]) -> str:
    rows = "".join(
        f'<tr><td style="padding:6px 0;font-size:14px;color:#3f3f46;">'
        f'<span style="color:#0f0f0f;font-weight:700;margin-right:8px;">—</span>{item}</td></tr>'
        for item in items
    )
    return f'<table cellpadding="0" cellspacing="0" width="100%" style="margin-bottom:4px;">{rows}</table>'

def _quote(text: str, accent: str = "#7c3aed") -> str:
    return (f'<div style="background:#fafafa;border-left:3px solid {accent};border-radius:4px;'
            f'padding:14px 16px;margin:16px 0;">'
            f'<p style="margin:0;font-size:13px;color:#52525b;font-style:italic;line-height:1.7;">{text}</p></div>')

def _alert(text: str, color: str = "#dc2626", bg: str = "#fef2f2") -> str:
    return (f'<div style="background:{bg};border-left:3px solid {color};border-radius:4px;'
            f'padding:14px 16px;margin:16px 0;">'
            f'<p style="margin:0;font-size:13px;color:{color};font-weight:600;">{text}</p></div>')


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — ONBOARDING & ACCOUNT
# ══════════════════════════════════════════════════════════════════════════════

def build_welcome_email(name: str) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _h1(f"Welcome to Applivo, {first}.") +
        _p("Your AI career agent is ready. Let's get you hired.", "#71717a") +
        _hr() +
        _bullets([
            "Scrapes new jobs every 6 hours across platforms",
            "Analyses each role against your profile using AI",
            "Writes a personalised cover letter for every application",
            "Applies automatically to matching jobs",
            "Monitors your inbox for recruiter replies",
        ]) +
        _hr() +
        _p("Complete your profile so the agent can start working.") +
        _btn("Set Up My Profile", f"{BASE_URL}/onboarding"),
        f"Your AI career agent is ready, {first}."
    )
    return "Welcome to Applivo — your AI career agent is ready", html


def build_otp_email(otp: str, purpose: str = "verification") -> tuple[str, str]:
    labels = {"register": "Email Verification", "login": "Login Code", "reset": "Password Reset"}
    label = labels.get(purpose, "Verification Code")
    html = _wrap(
        _tag(label, "#0f0f0f", "#f4f4f5") +
        _h1(label) +
        _p("Use the code below. It expires in 10 minutes.", "#71717a") +
        _hr() +
        f'<div style="text-align:center;padding:32px;background:#f9f9f9;border-radius:12px;margin-bottom:24px;">'
        f'<span style="font-size:42px;font-weight:900;letter-spacing:0.25em;color:#0f0f0f;font-family:monospace;">{otp}</span></div>' +
        _small("If you did not request this, you can safely ignore this email."),
        f"Your code is {otp} — expires in 10 minutes."
    )
    return f"Your Applivo code: {otp}", html


def build_new_device_login_email(name: str, device: str, location: str, time: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Security Alert", "#dc2626", "#fef2f2") +
        _h1("New sign-in detected") +
        _p("Your account was accessed from a new device.", "#71717a") +
        _hr() +
        _kv_table([("Device", device), ("Location", location), ("Time", time)]) +
        _hr() +
        _alert("If this was not you, change your password immediately.") +
        _btn("Secure My Account", f"{BASE_URL}/settings/security", "#dc2626"),
        "New sign-in to your Applivo account."
    )
    return "New sign-in to your Applivo account", html


def build_password_changed_email(name: str, time: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Security", "#0f0f0f", "#f4f4f5") +
        _h1("Password changed") +
        _p(f"Your Applivo password was changed on {time}.", "#71717a") +
        _hr() +
        _alert("If you did not make this change, contact support immediately.") +
        _btn("Contact Support", f"mailto:{SUPPORT_EMAIL}", "#dc2626"),
        "Your Applivo password was changed."
    )
    return "Your Applivo password was changed", html


def build_account_export_ready_email(name: str, download_url: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Ready", "#16a34a", "#f0fdf4") +
        _h1("Your data export is ready") +
        _p("Your account export has been prepared. The link expires in 24 hours.", "#71717a") +
        _hr() +
        _btn("Download My Data", download_url),
        "Your Applivo data export is ready to download."
    )
    return "Your Applivo data export is ready", html


def build_api_key_created_email(name: str, key_name: str, time: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Security Alert", "#ea580c", "#fff7ed") +
        _h1("New API key created") +
        _kv_table([("Key name", key_name), ("Created at", time)]) +
        _hr() +
        _alert("If you did not create this key, revoke it from your security settings immediately.", "#ea580c", "#fff7ed") +
        _btn("Manage API Keys", f"{BASE_URL}/settings/security", "#ea580c"),
        "A new API key was created for your Applivo account."
    )
    return "New API key created — Applivo security alert", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — TRIAL & SUBSCRIPTION
# ══════════════════════════════════════════════════════════════════════════════

def build_trial_started_email(name: str, trial_end: str, plan: str = "Starter") -> tuple[str, str]:
    html = _wrap(
        _tag("Trial Started", "#16a34a", "#f0fdf4") +
        _h1("Your 7-day free trial is live.") +
        _p("Everything is unlocked. Your agent is already running.", "#71717a") +
        _hr() +
        _stat_row([("7", "Days Free"), ("10/day", "Auto-Apply"), ("Unlimited", "AI Analysis")]) +
        _hr() +
        _kv_table([
            ("Trial ends", trial_end),
            ("After trial", f"{plan} plan — 199/month"),
            ("Cancel policy", "Cancel any time before trial ends"),
        ]) +
        _hr() +
        _btn("Go to Dashboard", f"{BASE_URL}/dashboard"),
        "7 days of full AI job automation starts now."
    )
    return "Your Applivo free trial has started", html


def build_trial_day3_email(name: str, jobs_applied: int, jobs_found: int) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _tag("Day 3 of 7", "#2563eb", "#eff6ff") +
        _h1(f"Your agent has been busy, {first}.") +
        _p("Here is what it has done in the first 3 days of your trial.", "#71717a") +
        _hr() +
        _stat_row([(str(jobs_found), "Jobs Found"), (str(jobs_applied), "Applications Sent")]) +
        _hr() +
        _p("4 days remain in your trial. Complete your profile to improve match quality.") +
        _btn("View My Progress", f"{BASE_URL}/analytics"),
        f"{jobs_applied} applications sent in 3 days."
    )
    return f"Day 3 update: your agent sent {jobs_applied} applications", html


def build_trial_ending_email(name: str, days_left: int, trial_end: str) -> tuple[str, str]:
    html = _wrap(
        _tag(f"{days_left} days left", "#ea580c", "#fff7ed") +
        _h1(f"Your trial ends on {trial_end}.") +
        _p("After that, your agent pauses. Keep it running for 199/month.", "#71717a") +
        _hr() +
        _p("Everything you have set up stays intact. Your subscription continues automatically if you added a card.") +
        _btn("Manage Subscription", f"{BASE_URL}/settings"),
        f"Your AI agent pauses in {days_left} days."
    )
    return f"Your Applivo trial ends in {days_left} days", html


def build_trial_last_chance_email(name: str, trial_end: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Last Chance", "#dc2626", "#fef2f2") +
        _h1("Your trial ends tomorrow.") +
        _p(f"On {trial_end}, your agent will pause unless you are subscribed.", "#71717a") +
        _hr() +
        _kv_table([("Starter plan", "199/month"), ("Pro plan", "499/month"), ("Premium plan", "999/month")]) +
        _hr() +
        _btn("Subscribe Now", f"{BASE_URL}/pricing", "#dc2626"),
        "Last day of your free trial."
    )
    return "Last chance: your Applivo trial ends tomorrow", html


def build_trial_expired_email(name: str) -> tuple[str, str]:
    html = _wrap(
        _h1("Your trial has ended.") +
        _p("Your AI agent is paused. Reactivate to keep applying automatically.", "#71717a") +
        _hr() +
        _kv_table([("Starter", "199/month"), ("Pro", "499/month"), ("Premium", "999/month")]) +
        _hr() +
        _btn("Reactivate My Agent", f"{BASE_URL}/pricing"),
        "Your agent is paused. One click to reactivate."
    )
    return "Your Applivo trial has ended — reactivate your agent", html


def build_trial_success_snapshot_email(name: str, jobs_found: int, jobs_applied: int, interviews: int) -> tuple[str, str]:
    html = _wrap(
        _tag("Trial Complete", "#7c3aed", "#f5f3ff") +
        _h1("Here is what your agent did in 7 days.") +
        _hr() +
        _stat_row([(str(jobs_found), "Jobs Found"), (str(jobs_applied), "Applied"), (str(interviews), "Replies")]) +
        _hr() +
        _p("Keep the momentum going. Subscribe to continue.") +
        _btn("Continue with Applivo", f"{BASE_URL}/pricing", "#7c3aed"),
        f"{jobs_applied} applications in 7 days. Keep going."
    )
    return "Your Applivo trial results — keep the momentum", html


def build_subscription_activated_email(name: str, plan: str, amount: str, next_billing: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Payment Confirmed", "#16a34a", "#f0fdf4") +
        _h1(f"{plan} plan activated.") +
        _p("Your AI agent is fully operational.", "#71717a") +
        _hr() +
        _kv_table([("Plan", plan), ("Amount charged", amount), ("Next billing", next_billing)]) +
        _hr() +
        _btn("View Dashboard", f"{BASE_URL}/dashboard"),
        f"{plan} plan is live. Your agent never stops."
    )
    return f"Applivo {plan} — payment confirmed", html


def build_subscription_renewal_reminder_email(name: str, plan: str, amount: str, renewal_date: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Renewal Reminder", "#2563eb", "#eff6ff") +
        _h1("Your subscription renews soon.") +
        _kv_table([("Plan", plan), ("Amount", amount), ("Renewal date", renewal_date)]) +
        _hr() +
        _p("No action needed — your card will be charged automatically.") +
        _btn("Manage Subscription", f"{BASE_URL}/settings"),
        f"Your {plan} plan renews on {renewal_date}."
    )
    return f"Applivo subscription renews on {renewal_date}", html


def build_payment_failed_email(name: str, plan: str, retry_date: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Action Required", "#dc2626", "#fef2f2") +
        _h1("Payment failed.") +
        _p(f"We could not charge your card for the {plan} plan. Update your payment method to keep your agent running.", "#71717a") +
        _hr() +
        _kv_table([("Retry date", retry_date)]) +
        _alert("If the retry also fails, your subscription will be paused.") +
        _btn("Update Payment Method", f"{BASE_URL}/settings", "#dc2626"),
        "Update your payment to keep your agent running."
    )
    return "Action required: Applivo payment failed", html


def build_cancellation_recovery_email(name: str, plan: str) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _h1(f"We noticed you cancelled, {first}.") +
        _p("Your agent has been paused. We want to understand what went wrong.", "#71717a") +
        _hr() +
        _bullets([
            "Was the price too high? We offer a lower tier.",
            "Did the agent not perform as expected? We can help.",
            "Running out of time to review results? We can slow down.",
        ]) +
        _hr() +
        _p("If you change your mind, reactivating takes 30 seconds.") +
        _btn("Reactivate at a Discount", f"{BASE_URL}/pricing"),
        f"Come back — your agent is waiting."
    )
    return "We're sorry to see you go — a note from Applivo", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — APPLICATION JOURNEY
# ══════════════════════════════════════════════════════════════════════════════

def build_application_submitted_email(name: str, company: str, role: str, match_score: int, total_today: int) -> tuple[str, str]:
    html = _wrap(
        _tag("Applied", "#2563eb", "#eff6ff") +
        _h1(role) +
        f'<p style="margin:0 0 20px;font-size:15px;color:#71717a;">{company}</p>' +
        _hr() +
        _stat_row([(f"{match_score}%", "Match Score"), (str(total_today), "Applied Today")]) +
        _hr() +
        _small("A personalised cover letter was generated and submitted. The agent is monitoring your inbox for replies.") +
        _btn("View Application", f"{BASE_URL}/applications"),
        f"Your agent applied to {role} at {company}."
    )
    return f"Applied: {role} at {company}", html


def build_high_match_alert_email(name: str, company: str, role: str, match_score: int, closes_in: str = "") -> tuple[str, str]:
    urgency = f" — closes in {closes_in}" if closes_in else ""
    html = _wrap(
        _tag(f"{match_score}% Match", "#16a34a", "#f0fdf4") +
        _h1("High-match opportunity found.") +
        _kv_table([("Role", role), ("Company", company), ("Match score", f"{match_score}%")] +
                  ([("Closes", closes_in)] if closes_in else [])) +
        _hr() +
        _p("Your agent will apply automatically. You can review the application from your dashboard.") +
        _btn("View Job", f"{BASE_URL}/jobs"),
        f"{match_score}% match at {company}{urgency}."
    )
    return f"High match: {role} at {company} ({match_score}%)", html


def build_urgent_job_alert_email(name: str, company: str, role: str, closes_in: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Closing Soon", "#dc2626", "#fef2f2") +
        _h1("This role closes soon.") +
        _kv_table([("Role", role), ("Company", company), ("Closes in", closes_in)]) +
        _hr() +
        _alert(f"This job closes in {closes_in}. Your agent is prioritising it.", "#ea580c", "#fff7ed") +
        _btn("View Job", f"{BASE_URL}/jobs"),
        f"{role} at {company} closes in {closes_in}."
    )
    return f"Urgent: {role} at {company} closes in {closes_in}", html


def build_application_aging_email(name: str, company: str, role: str, days_inactive: int) -> tuple[str, str]:
    html = _wrap(
        _tag("No Activity", "#71717a", "#f4f4f5") +
        _h1(f"No update on your {company} application.") +
        _p(f"It has been {days_inactive} days since you applied to {role} at {company} with no response.", "#71717a") +
        _hr() +
        _p("Consider sending a follow-up to stay visible to the recruiter.") +
        _btn("Send Follow-Up", f"{BASE_URL}/applications"),
        f"{days_inactive} days with no response from {company}."
    )
    return f"No response from {company} in {days_inactive} days", html


def build_follow_up_recommended_email(name: str, company: str, role: str, applied_date: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Follow-Up Window", "#7c3aed", "#f5f3ff") +
        _h1("Ideal time to follow up.") +
        _p(f"You applied to {role} at {company} on {applied_date}. The AI recommends following up now.", "#71717a") +
        _hr() +
        _p("Sending a polite follow-up at the right time increases response rates significantly.") +
        _btn("Generate Follow-Up", f"{BASE_URL}/applications", "#7c3aed"),
        f"Best time to follow up with {company}."
    )
    return f"Follow up with {company} now — timing is right", html


def build_interview_reminder_email(name: str, company: str, role: str, interview_time: str, hours_until: int) -> tuple[str, str]:
    tag_label = "Tomorrow" if hours_until >= 20 else "In 1 Hour"
    tag_color = "#2563eb" if hours_until >= 20 else "#dc2626"
    tag_bg = "#eff6ff" if hours_until >= 20 else "#fef2f2"
    html = _wrap(
        _tag(tag_label, tag_color, tag_bg) +
        _h1("Interview reminder.") +
        _kv_table([("Role", role), ("Company", company), ("Time", interview_time)]) +
        _hr() +
        _bullets([
            "Review your application and cover letter",
            "Research the company and role",
            "Prepare 3 questions to ask the interviewer",
            "Test your audio and video if it is remote",
        ]) +
        _btn("View Application", f"{BASE_URL}/applications"),
        f"Interview with {company} in {hours_until} hours."
    )
    return f"Interview reminder: {company} — {interview_time}", html


def build_interview_feedback_request_email(name: str, company: str, role: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Interview Passed", "#7c3aed", "#f5f3ff") +
        _h1("How did your interview go?") +
        _p(f"Your interview with {company} for {role} has passed. Log the outcome to keep your pipeline accurate.", "#71717a") +
        _hr() +
        _bullets([
            "Mark as Offer Received if they extended one",
            "Mark as Rejected if they passed",
            "Mark as Awaiting Decision if still in process",
        ]) +
        _btn("Update Interview Status", f"{BASE_URL}/applications"),
        f"Log the outcome of your {company} interview."
    )
    return f"How did your interview go? — {company}", html


def build_offer_received_email(name: str, company: str, role: str, offer_deadline: str = "") -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    deadline_row = [("Respond by", offer_deadline)] if offer_deadline else []
    html = _wrap(
        _tag("Offer Received", "#16a34a", "#f0fdf4") +
        _h1(f"Congratulations, {first}.") +
        _p(f"You received an offer for {role} at {company}.", "#71717a") +
        _hr() +
        _kv_table([("Role", role), ("Company", company)] + deadline_row) +
        _hr() +
        _bullets([
            "Review the full offer letter carefully",
            "Research market salary for this role and location",
            "Consider negotiating — most offers have room",
            "Respond professionally regardless of your decision",
        ]) +
        _btn("View Application", f"{BASE_URL}/applications", "#16a34a"),
        f"Offer received from {company}."
    )
    return f"Offer received: {role} at {company}", html


def build_offer_deadline_email(name: str, company: str, role: str, deadline: str, days_left: int) -> tuple[str, str]:
    html = _wrap(
        _tag(f"{days_left} days to respond", "#ea580c", "#fff7ed") +
        _h1("Offer response deadline approaching.") +
        _kv_table([("Role", role), ("Company", company), ("Respond by", deadline)]) +
        _hr() +
        _p("Make sure you have reviewed the offer and are prepared to respond.") +
        _btn("View Offer", f"{BASE_URL}/applications"),
        f"Respond to the {company} offer by {deadline}."
    )
    return f"Respond to {company} by {deadline}", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — RECRUITER INTELLIGENCE
# ══════════════════════════════════════════════════════════════════════════════

def build_interview_detected_email(name: str, company: str, role: str, snippet: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Recruiter Replied", "#7c3aed", "#f5f3ff") +
        _h1("A recruiter sent you a message.") +
        _p(f"{role} — {company}", "#71717a") +
        _hr() +
        _quote(f'"{snippet[:300]}{"..." if len(snippet) > 300 else ""}"') +
        _btn("Open Messages", f"{BASE_URL}/messages", "#7c3aed"),
        f"A recruiter from {company} replied to your application."
    )
    return f"Recruiter replied: {company}", html


def build_positive_signal_email(name: str, company: str, role: str, signal: str) -> tuple[str, str]:
    signal_map = {
        "interview": "Interview invitation",
        "assessment": "Assessment request",
        "shortlist": "Shortlist confirmation",
    }
    label = signal_map.get(signal, "Positive signal")
    html = _wrap(
        _tag(label, "#16a34a", "#f0fdf4") +
        _h1(f"{label} from {company}.") +
        _kv_table([("Role", role), ("Signal type", label)]) +
        _hr() +
        _p("Respond promptly — recruiters appreciate timely candidates.") +
        _btn("Reply Now", f"{BASE_URL}/messages", "#16a34a"),
        f"{label} detected from {company}."
    )
    return f"{label}: {company} — {role}", html


def build_rejection_detected_email(name: str, company: str, role: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Application Closed", "#71717a", "#f4f4f5") +
        _h1(f"{company} has moved forward with other candidates.") +
        _p(f"Your application for {role} has been declined.", "#71717a") +
        _hr() +
        _bullets([
            "Your agent is continuing to find new matches",
            "Review your profile for improvements",
            "Request feedback if the recruiter is open to it",
        ]) +
        _btn("View Active Applications", f"{BASE_URL}/applications"),
        f"Application closed at {company}."
    )
    return f"Application update: {company} — {role}", html


def build_ghosting_alert_email(name: str, company: str, role: str, days_silent: int) -> tuple[str, str]:
    html = _wrap(
        _tag(f"{days_silent} days silent", "#71717a", "#f4f4f5") +
        _h1(f"No response from {company}.") +
        _p(f"It has been {days_silent} days since your last contact with {company} regarding {role}.", "#71717a") +
        _hr() +
        _p("You can attempt one final follow-up or mark this application as closed.") +
        _btn("Send Final Follow-Up", f"{BASE_URL}/applications"),
        f"{company} has been silent for {days_silent} days."
    )
    return f"Recruiter ghosting alert: {company} ({days_silent} days)", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — AI AGENT ACTIVITY
# ══════════════════════════════════════════════════════════════════════════════

def build_daily_agent_summary_email(
    name: str,
    date_label: str,
    jobs_found: int,
    jobs_applied: int,
    interviews: int,
    top_companies: list[str],
) -> tuple[str, str]:
    companies_html = "".join(
        f'<span style="display:inline-block;background:#f4f4f5;color:#3f3f46;font-size:12px;font-weight:600;'
        f'padding:4px 10px;border-radius:6px;margin:3px 3px 3px 0;">{c}</span>'
        for c in top_companies[:5]
    )
    html = _wrap(
        _tag(date_label, "#0f0f0f", "#f4f4f5") +
        _h1("Daily agent summary.") +
        _hr() +
        _stat_row([(str(jobs_found), "Jobs Found"), (str(jobs_applied), "Applications"), (str(interviews), "Replies")]) +
        (_hr() + '<p style="margin:0 0 8px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#a1a1aa;">Companies</p>' + companies_html if top_companies else "") +
        _hr() +
        _btn("View Full Activity", f"{BASE_URL}/analytics"),
        f"{jobs_applied} applications sent today."
    )
    return f"Daily summary: {jobs_applied} applications sent", html


def build_milestone_email(name: str, milestone: int, total_companies: int) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _tag("Milestone", "#7c3aed", "#f5f3ff") +
        _h1(f"{milestone} applications submitted.") +
        _p(f"Your agent has now submitted {milestone} applications across {total_companies} companies.", "#71717a") +
        _hr() +
        _p("Keep your profile updated to maintain high match quality.") +
        _btn("View All Applications", f"{BASE_URL}/applications", "#7c3aed"),
        f"Your agent just hit {milestone} applications."
    )
    return f"Milestone: {milestone} applications submitted", html


def build_resume_optimized_email(name: str, changes: list[str]) -> tuple[str, str]:
    html = _wrap(
        _tag("Resume Updated", "#2563eb", "#eff6ff") +
        _h1("Your resume was optimized by AI.") +
        _p("The following improvements were applied:", "#71717a") +
        _hr() +
        _bullets(changes[:6]) +
        _hr() +
        _btn("View Updated Resume", f"{BASE_URL}/resumes"),
        "Your AI-optimized resume is ready."
    )
    return "Your Applivo resume was just optimized", html


def build_cover_letter_generated_email(name: str, company: str, role: str) -> tuple[str, str]:
    html = _wrap(
        _tag("Ready", "#2563eb", "#eff6ff") +
        _h1("Cover letter generated.") +
        _kv_table([("Role", role), ("Company", company)]) +
        _hr() +
        _p("Your personalised cover letter is attached to this application and ready to submit.") +
        _btn("Review Cover Letter", f"{BASE_URL}/applications"),
        f"Cover letter ready for {role} at {company}."
    )
    return f"Cover letter ready: {role} at {company}", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 6 — ENGAGEMENT & RETENTION
# ══════════════════════════════════════════════════════════════════════════════

def build_weekly_digest_email(
    name: str,
    week_label: str,
    jobs_found: int,
    jobs_applied: int,
    interviews: int,
    response_rate: float,
    top_companies: list[str],
    top_skills: list[str],
) -> tuple[str, str]:
    companies_html = "".join(
        f'<span style="display:inline-block;background:#f4f4f5;color:#3f3f46;font-size:12px;font-weight:600;'
        f'padding:4px 10px;border-radius:6px;margin:3px 3px 3px 0;">{c}</span>'
        for c in top_companies[:6]
    )
    skills_html = "".join(
        f'<span style="display:inline-block;background:#eff6ff;color:#2563eb;font-size:12px;font-weight:600;'
        f'padding:4px 10px;border-radius:6px;margin:3px 3px 3px 0;">{s}</span>'
        for s in top_skills[:6]
    )
    html = _wrap(
        _tag(week_label, "#0f0f0f", "#f4f4f5") +
        _h1("Your weekly career report.") +
        _hr() +
        _stat_row([(str(jobs_found), "Jobs Found"), (str(jobs_applied), "Applied"), (str(interviews), "Replies"), (f"{response_rate:.0f}%", "Response Rate")]) +
        (_hr() + '<p style="margin:0 0 8px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#a1a1aa;">Top Companies</p>' + companies_html if top_companies else "") +
        (_hr() + '<p style="margin:0 0 8px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#a1a1aa;">Skills in Demand</p>' + skills_html if top_skills else "") +
        _hr() +
        _btn("View Full Report", f"{BASE_URL}/analytics"),
        f"{jobs_applied} applications, {interviews} replies this week."
    )
    return f"Applivo Weekly — {week_label}", html


def build_ai_agent_performance_report_email(
    name: str,
    week_label: str,
    jobs_analyzed: int,
    jobs_matched: int,
    jobs_applied: int,
    recruiter_replies: int,
    interviews: int,
    top_skills: list[str],
    recommended_actions: list[str],
) -> tuple[str, str]:
    skills_html = "".join(
        f'<span style="display:inline-block;background:#f4f4f5;color:#3f3f46;font-size:12px;font-weight:600;'
        f'padding:4px 10px;border-radius:6px;margin:3px 3px 3px 0;">{s}</span>'
        for s in top_skills[:8]
    )
    match_rate = f"{(jobs_matched/jobs_analyzed*100):.0f}%" if jobs_analyzed else "—"
    html = _wrap(
        _tag(f"Week {week_label}", "#0f0f0f", "#f4f4f5") +
        _h1("AI Agent Performance Report.") +
        _p("A complete breakdown of what your autonomous agent did this week.", "#71717a") +
        _hr() +
        _stat_row([(str(jobs_analyzed), "Analyzed"), (str(jobs_matched), "Matched"), (str(jobs_applied), "Applied")]) +
        '<div style="height:8px;"></div>' +
        _stat_row([(str(recruiter_replies), "Recruiter Replies"), (str(interviews), "Interviews"), (match_rate, "Match Rate")]) +
        (_hr() + '<p style="margin:0 0 8px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#a1a1aa;">Top Skills in Demand</p>' + skills_html if top_skills else "") +
        (_hr() + '<p style="margin:0 0 10px;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#a1a1aa;">Recommended Actions</p>' + _bullets(recommended_actions) if recommended_actions else "") +
        _hr() +
        _btn("View Full Analytics", f"{BASE_URL}/analytics"),
        f"{jobs_applied} applications, {interviews} interviews this week."
    )
    return f"Your AI Career Agent Report — {week_label}", html


def build_monthly_career_report_email(
    name: str,
    month_label: str,
    total_applied: int,
    total_interviews: int,
    total_offers: int,
    response_rate: float,
    days_active: int,
) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _tag(month_label, "#0f0f0f", "#f4f4f5") +
        _h1(f"Your {month_label} career report.") +
        _p(f"Here is everything your agent accomplished for you in {month_label}.", "#71717a") +
        _hr() +
        _stat_row([(str(total_applied), "Applications"), (str(total_interviews), "Interviews"), (str(total_offers), "Offers")]) +
        '<div style="height:8px;"></div>' +
        _stat_row([(f"{response_rate:.0f}%", "Response Rate"), (str(days_active), "Days Active")]) +
        _hr() +
        _btn("View Full Report", f"{BASE_URL}/analytics"),
        f"{total_applied} applications, {total_interviews} interviews in {month_label}."
    )
    return f"Applivo Monthly Report — {month_label}", html


def build_thirty_day_progress_email(
    name: str,
    total_applied: int,
    total_interviews: int,
    profile_score: int,
) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _tag("30 Days", "#7c3aed", "#f5f3ff") +
        _h1(f"30 days since you joined Applivo, {first}.") +
        _hr() +
        _stat_row([(str(total_applied), "Applications Sent"), (str(total_interviews), "Interviews"), (f"{profile_score}%", "Profile Score")]) +
        _hr() +
        _p("Keep your profile and resume updated to maintain high match rates.") +
        _btn("View My Progress", f"{BASE_URL}/analytics", "#7c3aed"),
        f"{total_applied} applications in your first 30 days."
    )
    return "Your first 30 days on Applivo", html


def build_profile_strength_email(name: str, score: int, missing: list[str]) -> tuple[str, str]:
    color = "#16a34a" if score >= 80 else "#ea580c" if score >= 50 else "#dc2626"
    html = _wrap(
        _tag("Profile Score", color, "#f9f9f9") +
        _h1(f"Your profile is {score}% complete.") +
        _p("A stronger profile means higher match rates and better applications.", "#71717a") +
        _hr() +
        (_bullets([f"Missing: {m}" for m in missing]) if missing else _p("Your profile is in great shape.", "#16a34a")) +
        _hr() +
        _btn("Improve My Profile", f"{BASE_URL}/onboarding"),
        f"Profile score: {score}%."
    )
    return f"Your Applivo profile score: {score}%", html


def build_reengagement_email(name: str, days_inactive: int) -> tuple[str, str]:
    first = name.split()[0] if name else "there"
    html = _wrap(
        _h1(f"Your agent has been busy, {first}.") +
        _p(f"It has been {days_inactive} days since you last logged in. New job matches are waiting.", "#71717a") +
        _hr() +
        _p("Some of those roles may have deadlines approaching.") +
        _btn("See What I Missed", f"{BASE_URL}/dashboard"),
        f"New job matches are waiting — {days_inactive} days of activity."
    )
    return "New job matches waiting — your agent found opportunities", html


def build_profile_incomplete_email(name: str, missing: list[str]) -> tuple[str, str]:
    html = _wrap(
        _h1("Your agent needs more information.") +
        _p("The following profile sections are incomplete. Without them, the agent cannot match or apply effectively.", "#71717a") +
        _hr() +
        _bullets([f"Missing: {m}" for m in missing]) +
        _hr() +
        _btn("Complete My Profile", f"{BASE_URL}/onboarding"),
        "A few minutes of setup = hundreds of applications sent."
    )
    return "Complete your profile — your agent is waiting", html


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 7 — SENDER
# ══════════════════════════════════════════════════════════════════════════════

async def send_email(to_email: str, subject: str, html: str) -> bool:
    if not all([settings.SMTP_HOST, settings.SMTP_USERNAME, settings.SMTP_PASSWORD]):
        logger.warning("email_service: SMTP not configured", to=to_email, subject=subject)
        return False
    from_addr = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{settings.SMTP_FROM_NAME} <{from_addr}>"
        msg["To"] = to_email
        msg.attach(MIMEText(html, "html"))
        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("email_service: sent", to=to_email, subject=subject)
        return True
    except Exception as e:
        logger.error("email_service: failed", to=to_email, subject=subject, error=str(e))
        return False


# ── Fire-and-forget helpers ────────────────────────────────────────────────────

async def send_welcome(to: str, name: str) -> None:
    s, h = build_welcome_email(name); await send_email(to, s, h)

async def send_otp(to: str, otp: str, purpose: str = "verification") -> bool:
    s, h = build_otp_email(otp, purpose); return await send_email(to, s, h)

async def send_new_device_login(to: str, name: str, device: str, location: str, time: str) -> None:
    s, h = build_new_device_login_email(name, device, location, time); await send_email(to, s, h)

async def send_password_changed(to: str, name: str, time: str) -> None:
    s, h = build_password_changed_email(name, time); await send_email(to, s, h)

async def send_account_export_ready(to: str, name: str, url: str) -> None:
    s, h = build_account_export_ready_email(name, url); await send_email(to, s, h)

async def send_api_key_created(to: str, name: str, key_name: str, time: str) -> None:
    s, h = build_api_key_created_email(name, key_name, time); await send_email(to, s, h)

async def send_trial_started(to: str, name: str, trial_end: str, plan: str = "Starter") -> None:
    s, h = build_trial_started_email(name, trial_end, plan); await send_email(to, s, h)

async def send_trial_day3(to: str, name: str, jobs_applied: int, jobs_found: int) -> None:
    s, h = build_trial_day3_email(name, jobs_applied, jobs_found); await send_email(to, s, h)

async def send_trial_ending(to: str, name: str, days_left: int, trial_end: str) -> None:
    s, h = build_trial_ending_email(name, days_left, trial_end); await send_email(to, s, h)

async def send_trial_last_chance(to: str, name: str, trial_end: str) -> None:
    s, h = build_trial_last_chance_email(name, trial_end); await send_email(to, s, h)

async def send_trial_expired(to: str, name: str) -> None:
    s, h = build_trial_expired_email(name); await send_email(to, s, h)

async def send_trial_success_snapshot(to: str, name: str, jobs_found: int, jobs_applied: int, interviews: int) -> None:
    s, h = build_trial_success_snapshot_email(name, jobs_found, jobs_applied, interviews); await send_email(to, s, h)

async def send_subscription_activated(to: str, name: str, plan: str, amount: str, next_billing: str) -> None:
    s, h = build_subscription_activated_email(name, plan, amount, next_billing); await send_email(to, s, h)

async def send_subscription_renewal_reminder(to: str, name: str, plan: str, amount: str, renewal_date: str) -> None:
    s, h = build_subscription_renewal_reminder_email(name, plan, amount, renewal_date); await send_email(to, s, h)

async def send_payment_failed(to: str, name: str, plan: str, retry_date: str) -> None:
    s, h = build_payment_failed_email(name, plan, retry_date); await send_email(to, s, h)

async def send_cancellation_recovery(to: str, name: str, plan: str) -> None:
    s, h = build_cancellation_recovery_email(name, plan); await send_email(to, s, h)

async def send_application_submitted(to: str, name: str, company: str, role: str, match_score: int, total_today: int) -> None:
    s, h = build_application_submitted_email(name, company, role, match_score, total_today); await send_email(to, s, h)

async def send_high_match_alert(to: str, name: str, company: str, role: str, match_score: int, closes_in: str = "") -> None:
    s, h = build_high_match_alert_email(name, company, role, match_score, closes_in); await send_email(to, s, h)

async def send_urgent_job_alert(to: str, name: str, company: str, role: str, closes_in: str) -> None:
    s, h = build_urgent_job_alert_email(name, company, role, closes_in); await send_email(to, s, h)

async def send_application_aging(to: str, name: str, company: str, role: str, days_inactive: int) -> None:
    s, h = build_application_aging_email(name, company, role, days_inactive); await send_email(to, s, h)

async def send_follow_up_recommended(to: str, name: str, company: str, role: str, applied_date: str) -> None:
    s, h = build_follow_up_recommended_email(name, company, role, applied_date); await send_email(to, s, h)

async def send_interview_reminder(to: str, name: str, company: str, role: str, interview_time: str, hours_until: int) -> None:
    s, h = build_interview_reminder_email(name, company, role, interview_time, hours_until); await send_email(to, s, h)

async def send_interview_feedback_request(to: str, name: str, company: str, role: str) -> None:
    s, h = build_interview_feedback_request_email(name, company, role); await send_email(to, s, h)

async def send_offer_received(to: str, name: str, company: str, role: str, offer_deadline: str = "") -> None:
    s, h = build_offer_received_email(name, company, role, offer_deadline); await send_email(to, s, h)

async def send_offer_deadline(to: str, name: str, company: str, role: str, deadline: str, days_left: int) -> None:
    s, h = build_offer_deadline_email(name, company, role, deadline, days_left); await send_email(to, s, h)

async def send_interview_detected(to: str, name: str, company: str, role: str, snippet: str) -> None:
    s, h = build_interview_detected_email(name, company, role, snippet); await send_email(to, s, h)

async def send_positive_signal(to: str, name: str, company: str, role: str, signal: str) -> None:
    s, h = build_positive_signal_email(name, company, role, signal); await send_email(to, s, h)

async def send_rejection_detected(to: str, name: str, company: str, role: str) -> None:
    s, h = build_rejection_detected_email(name, company, role); await send_email(to, s, h)

async def send_ghosting_alert(to: str, name: str, company: str, role: str, days_silent: int) -> None:
    s, h = build_ghosting_alert_email(name, company, role, days_silent); await send_email(to, s, h)

async def send_daily_agent_summary(to: str, name: str, date_label: str, jobs_found: int, jobs_applied: int, interviews: int, top_companies: list) -> None:
    s, h = build_daily_agent_summary_email(name, date_label, jobs_found, jobs_applied, interviews, top_companies); await send_email(to, s, h)

async def send_milestone(to: str, name: str, milestone: int, total_companies: int) -> None:
    s, h = build_milestone_email(name, milestone, total_companies); await send_email(to, s, h)

async def send_resume_optimized(to: str, name: str, changes: list) -> None:
    s, h = build_resume_optimized_email(name, changes); await send_email(to, s, h)

async def send_cover_letter_generated(to: str, name: str, company: str, role: str) -> None:
    s, h = build_cover_letter_generated_email(name, company, role); await send_email(to, s, h)

async def send_weekly_digest(to: str, name: str, week_label: str, jobs_found: int, jobs_applied: int, interviews: int, response_rate: float, top_companies: list, top_skills: list) -> None:
    s, h = build_weekly_digest_email(name, week_label, jobs_found, jobs_applied, interviews, response_rate, top_companies, top_skills); await send_email(to, s, h)

async def send_ai_agent_performance_report(to: str, name: str, week_label: str, jobs_analyzed: int, jobs_matched: int, jobs_applied: int, recruiter_replies: int, interviews: int, top_skills: list, recommended_actions: list) -> None:
    s, h = build_ai_agent_performance_report_email(name, week_label, jobs_analyzed, jobs_matched, jobs_applied, recruiter_replies, interviews, top_skills, recommended_actions); await send_email(to, s, h)

async def send_monthly_career_report(to: str, name: str, month_label: str, total_applied: int, total_interviews: int, total_offers: int, response_rate: float, days_active: int) -> None:
    s, h = build_monthly_career_report_email(name, month_label, total_applied, total_interviews, total_offers, response_rate, days_active); await send_email(to, s, h)

async def send_thirty_day_progress(to: str, name: str, total_applied: int, total_interviews: int, profile_score: int) -> None:
    s, h = build_thirty_day_progress_email(name, total_applied, total_interviews, profile_score); await send_email(to, s, h)

async def send_profile_strength(to: str, name: str, score: int, missing: list) -> None:
    s, h = build_profile_strength_email(name, score, missing); await send_email(to, s, h)

async def send_reengagement(to: str, name: str, days_inactive: int) -> None:
    s, h = build_reengagement_email(name, days_inactive); await send_email(to, s, h)

async def send_profile_incomplete(to: str, name: str, missing: list) -> None:
    s, h = build_profile_incomplete_email(name, missing); await send_email(to, s, h)
