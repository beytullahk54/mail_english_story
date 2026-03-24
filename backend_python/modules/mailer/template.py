def build_welcome_email_html(email: str, level: str, language: str, unsubscribe_url: str = "") -> str:
    level_colors = {
        "a1": "#34d399",
        "a2": "#34d399",
        "b1": "#60a5fa",
        "b2": "#60a5fa",
        "c1": "#f59e0b",
        "c2": "#f59e0b",
    }
    badge_color = level_colors.get(level.lower(), "#818cf8")

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Welcome to English Story</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <div style="display:inline-block;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:12px 20px;">
                <span style="font-size:1.4rem;font-weight:700;background:linear-gradient(to right,#818cf8,#c084fc);-webkit-background-clip:text;color:transparent;">
                  📖 English Story
                </span>
              </div>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:36px;box-shadow:0 8px 32px rgba(0,0,0,0.3);">

              <!-- Welcome Icon -->
              <div style="text-align:center;margin-bottom:24px;">
                <span style="font-size:3rem;">🎉</span>
              </div>

              <!-- Title -->
              <h1 style="margin:0 0 12px 0;font-size:24px;font-weight:700;color:#f1f5f9;text-align:center;">
                Welcome aboard!
              </h1>
              <p style="margin:0 0 28px 0;font-size:15px;color:#94a3b8;text-align:center;line-height:1.6;">
                Thank you for subscribing to <strong style="color:#c084fc;">English Story</strong>.<br/>
                You will receive daily English stories tailored to your level.
              </p>

              <!-- Divider -->
              <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0 0 24px 0;"/>

              <!-- Subscription Details -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="color:#64748b;font-size:13px;">📧 Email</span>
                  </td>
                  <td align="right" style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="color:#e2e8f0;font-size:13px;">{email}</span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="color:#64748b;font-size:13px;">📚 Level</span>
                  </td>
                  <td align="right" style="padding:10px 0;border-bottom:1px solid rgba(255,255,255,0.06);">
                    <span style="background:rgba(255,255,255,0.07);border:1px solid {badge_color}44;border-radius:50px;padding:3px 12px;font-size:13px;color:{badge_color};">
                      {level.upper()}
                    </span>
                  </td>
                </tr>
                <tr>
                  <td style="padding:10px 0;">
                    <span style="color:#64748b;font-size:13px;">🌍 Language</span>
                  </td>
                  <td align="right" style="padding:10px 0;">
                    <span style="color:#e2e8f0;font-size:13px;">{language}</span>
                  </td>
                </tr>
              </table>

              <!-- CTA Note -->
              <div style="background:rgba(129,140,248,0.08);border:1px solid rgba(129,140,248,0.2);border-radius:12px;padding:16px 20px;text-align:center;">
                <p style="margin:0;font-size:14px;color:#a5b4fc;line-height:1.6;">
                  ✨ Your first story is on its way!<br/>
                  <span style="color:#64748b;font-size:12px;">Stories are delivered daily to help you improve your English.</span>
                </p>
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top:28px;">
              <p style="margin:0;font-size:12px;color:#475569;">
                You received this email because you subscribed to English Story newsletter.<br/>
              </p>
              {f'<a href="{unsubscribe_url}" style="display:inline-block;margin-top:16px;padding:8px 20px;background:transparent;border:1px solid #475569;border-radius:8px;color:#64748b;font-size:12px;text-decoration:none;">Unsubscribe</a>' if unsubscribe_url else ''}
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def build_email_html(topic: str, level: str, story: str, unsubscribe_url: str = "") -> str:
    level_colors = {
        "beginner": "#34d399",
        "intermediate": "#60a5fa",
        "advanced": "#f59e0b",
    }
    badge_color = level_colors.get(level, "#818cf8")

    paragraphs = "".join(
        f"<p style='margin:0 0 1em 0;'>{line}</p>"
        for line in story.split("\n")
        if line.strip()
    )

    return f"""
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8"/>
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Your English Story</title>
</head>
<body style="margin:0;padding:0;background:#0f172a;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0f172a;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

          <!-- Header -->
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <div style="display:inline-block;background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:16px;padding:12px 20px;">
                <span style="font-size:1.4rem;font-weight:700;background:linear-gradient(to right,#818cf8,#c084fc);-webkit-background-clip:text;color:transparent;">
                  📖 English Story
                </span>
              </div>
            </td>
          </tr>

          <!-- Card -->
          <tr>
            <td style="background:rgba(255,255,255,0.05);border:1px solid rgba(255,255,255,0.1);border-radius:20px;padding:36px;box-shadow:0 8px 32px rgba(0,0,0,0.3);">

              <!-- Topic & Level -->
              <table width="100%" cellpadding="0" cellspacing="0" style="margin-bottom:24px;">
                <tr>
                  <td>
                    <span style="background:rgba(255,255,255,0.07);border:1px solid rgba(255,255,255,0.12);border-radius:50px;padding:4px 14px;font-size:13px;color:#94a3b8;">
                      🏷 {topic}
                    </span>
                  </td>
                  <td align="right">
                    <span style="background:rgba(255,255,255,0.07);border:1px solid {badge_color}44;border-radius:50px;padding:4px 14px;font-size:13px;color:{badge_color};">
                      {level.capitalize()}
                    </span>
                  </td>
                </tr>
              </table>

              <!-- Divider -->
              <hr style="border:none;border-top:1px solid rgba(255,255,255,0.08);margin:0 0 24px 0;"/>

              <!-- Story -->
              <div style="font-size:16px;line-height:1.9;color:#e2e8f0;">
                {paragraphs}
              </div>

            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td align="center" style="padding-top:28px;">
              <p style="margin:0;font-size:12px;color:#475569;">
                Bu e-postayı aldınız çünkü English Story bültenine abone oldunuz.<br/>
              </p>
              {f'<a href="{unsubscribe_url}" style="display:inline-block;margin-top:16px;padding:8px 20px;background:transparent;border:1px solid #475569;border-radius:8px;color:#64748b;font-size:12px;text-decoration:none;">Unsubscribe</a>' if unsubscribe_url else ''}
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
