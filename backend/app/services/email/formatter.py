from typing import Dict, Any, Optional, List

class EmailHtmlFormatter:
    """
    Renders clean, modern, responsive HTML emails with embedded audit scorecards,
    typography, and document attachment callouts.
    """

    @staticmethod
    def format_html_email(
        body_text: str,
        subject: str,
        company_name: Optional[str] = None,
        recipient_name: Optional[str] = None,
        scores: Optional[Dict[str, Any]] = None,
        observed_issue: Optional[str] = None,
        recommended_service: Optional[str] = None,
        attached_report_name: Optional[str] = None,
        report_url: Optional[str] = None
    ) -> str:
        # Convert plain text newlines to clean HTML paragraphs/breaks
        paragraphs = [p.strip() for p in body_text.split("\n\n") if p.strip()]
        formatted_paragraphs = ""
        for p in paragraphs:
            if p.startswith("•") or p.startswith("-") or p.startswith("*"):
                lines = p.split("\n")
                list_items = "".join([f"<li style='margin-bottom: 6px; color: #334155;'>{line.lstrip('•-* ')}</li>" for line in lines if line.strip()])
                formatted_paragraphs += f"<ul style='margin: 14px 0; padding-left: 20px;'>{list_items}</ul>"
            else:
                formatted_paragraphs += f"<p style='margin: 0 0 16px 0; line-height: 1.65; color: #334155; font-size: 15px;'>{p.replace(chr(10), '<br/>')}</p>"

        # Scorecard widget HTML if scores are provided
        scorecard_html = ""
        if scores:
            overall = scores.get("overall_score", 0)
            mobile = scores.get("mobile_score", 0)
            speed = scores.get("performance_score", 0)
            seo = scores.get("seo_score", 0)
            security = scores.get("security_score", 0)

            scorecard_html = f"""
            <div style="margin: 24px 0; padding: 20px; background-color: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; border-bottom: 1px solid #e2e8f0; padding-bottom: 10px;">
                    <div>
                        <span style="font-size: 11px; font-weight: 700; text-transform: uppercase; color: #64748b; letter-spacing: 0.5px;">Technical Website Audit Summary</span>
                        <div style="font-size: 16px; font-weight: 700; color: #0f172a; margin-top: 2px;">{company_name or 'Web Audit'}</div>
                    </div>
                    <div style="text-align: right;">
                        <span style="display: inline-block; background-color: {'#dbeafe' if overall > 50 else '#fee2e2'}; color: {'#1e40af' if overall > 50 else '#991b1b'}; padding: 4px 10px; border-radius: 20px; font-weight: 700; font-size: 13px;">
                            Health Score: {overall}/100
                        </span>
                    </div>
                </div>

                <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom: 14px;">
                    <tr>
                        <td width="25%" style="text-align: center; padding: 10px 6px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;">
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">Mobile UX</div>
                            <div style="font-size: 16px; font-weight: 800; color: {'#dc2626' if mobile < 60 else '#16a34a'}; margin-top: 2px;">{mobile}/100</div>
                        </td>
                        <td width="5%"></td>
                        <td width="25%" style="text-align: center; padding: 10px 6px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;">
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">Speed / CWV</div>
                            <div style="font-size: 16px; font-weight: 800; color: {'#d97706' if speed < 60 else '#16a34a'}; margin-top: 2px;">{speed}/100</div>
                        </td>
                        <td width="5%"></td>
                        <td width="25%" style="text-align: center; padding: 10px 6px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;">
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">SEO Structure</div>
                            <div style="font-size: 16px; font-weight: 800; color: #334155; margin-top: 2px;">{seo}/100</div>
                        </td>
                        <td width="5%"></td>
                        <td width="25%" style="text-align: center; padding: 10px 6px; background-color: #ffffff; border: 1px solid #e2e8f0; border-radius: 6px;">
                            <div style="font-size: 11px; color: #64748b; font-weight: 600;">Security & SSL</div>
                            <div style="font-size: 16px; font-weight: 800; color: {'#16a34a' if security > 70 else '#dc2626'}; margin-top: 2px;">{security}/100</div>
                        </td>
                    </tr>
                </table>

                {f'''
                <div style="background-color: #eff6ff; border-left: 4px solid #2563eb; padding: 10px 14px; border-radius: 4px; margin-top: 10px;">
                    <div style="font-size: 11px; font-weight: 700; color: #1e40af; text-transform: uppercase;">Observed Technical Defect:</div>
                    <div style="font-size: 13px; color: #1e3a8a; margin-top: 2px;">{observed_issue}</div>
                </div>
                ''' if observed_issue else ''}
            </div>
            """

        # Attachment badge block
        attachment_html = ""
        if attached_report_name:
            attachment_html = f"""
            <div style="margin: 20px 0; padding: 14px 18px; background-color: #f1f5f9; border-radius: 8px; border: 1px dashed #cbd5e1; display: flex; align-items: center; justify-content: space-between;">
                <div>
                    <span style="font-size: 11px; font-weight: 700; color: #475569; text-transform: uppercase;">📎 Attached R&D Report Document</span>
                    <div style="font-size: 14px; font-weight: 600; color: #0f172a; margin-top: 2px;">{attached_report_name}</div>
                    <div style="font-size: 12px; color: #64748b;">Full breakdown of core web vitals, observable defects & strategic modernization blueprint.</div>
                </div>
                {f'<div style="text-align: right; margin-top: 8px;"><a href="{report_url}" target="_blank" style="display: inline-block; padding: 6px 14px; background-color: #2563eb; color: #ffffff; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600;">View Online Report &rarr;</a></div>' if report_url else ''}
            </div>
            """

        html_template = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{subject}</title>
</head>
<body style="margin: 0; padding: 24px; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="max-width: 620px; margin: 0 auto; background-color: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; overflow: hidden; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <!-- Branded Header -->
        <tr>
            <td style="padding: 24px 32px; background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); color: #ffffff;">
                <table width="100%" cellpadding="0" cellspacing="0">
                    <tr>
                        <td>
                            <div style="font-size: 18px; font-weight: 800; letter-spacing: -0.5px; color: #ffffff;">Acme Growth & Engineering</div>
                            <div style="font-size: 12px; color: #94a3b8; margin-top: 2px;">B2B Technical Website Intelligence & Modernization</div>
                        </td>
                        <td style="text-align: right;">
                            <span style="font-size: 11px; font-weight: 700; background-color: rgba(59, 130, 246, 0.2); color: #60a5fa; padding: 4px 10px; border-radius: 20px; border: 1px solid rgba(59, 130, 246, 0.3);">
                                R&D AUDIT BRIEF
                            </span>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>

        <!-- Main Body -->
        <tr>
            <td style="padding: 32px;">
                {formatted_paragraphs}

                {scorecard_html}

                {attachment_html}

                <!-- Footer Signoff -->
                <div style="margin-top: 32px; padding-top: 20px; border-top: 1px solid #e2e8f0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                    <div>This message was sent with an attached Technical R&D Audit Report prepared exclusively for {company_name or 'your business'}.</div>
                    <div style="margin-top: 4px;">To opt out of future updates, simply reply "Unsubscribe" to this email.</div>
                </div>
            </td>
        </tr>
    </table>
</body>
</html>"""
        return html_template

email_formatter = EmailHtmlFormatter()
