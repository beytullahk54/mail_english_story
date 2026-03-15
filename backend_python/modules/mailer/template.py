def build_email_html(topic: str, level: str, story: str) -> str:
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
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
