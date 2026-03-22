import datetime
import os
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import config

class DisplayAgent:
    def __init__(self, target_folder="newsreports"):
        self.target_folder = target_folder

    def _get_domain(self, url):
        """Extracts the root domain for the source badge."""
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "source link"

    def _estimate_read_time(self, text):
        """Rough read-time estimate based on word count (250 wpm)."""
        words = len(text.split())
        minutes = max(1, round(words / 250))
        return f"{minutes} min read"

    def generate_html_report(self, articles):
        # Convert UTC → US/Eastern (handles EST/EDT automatically)
        est = ZoneInfo("America/New_York")
        now = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(est)

        # Timezone abbreviation: EST or EDT
        tz_abbr = now.strftime("%Z")

        date_str      = now.strftime("%A, %-d %B %Y").upper()
        time_str      = now.strftime("%-I:%M %p") + f" {tz_abbr}"
        filename      = f"AI_News_{now.strftime('%d%b%Y').upper()}.html"
        source_count  = len(config.RSS_FEEDS)
        source_label  = f"Curated from {source_count} sources"

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        full_path = os.path.join(self.target_folder, filename)

        # ── 1. Head & Design System ──────────────────────────────────────────
        html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Inference — {date_str}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,400;1,700&family=Source+Serif+4:ital,opsz,wght@0,8..60,300;0,8..60,400;1,8..60,300;1,8..60,400&family=IBM+Plex+Mono:wght@400;500&display=swap" rel="stylesheet">
  <style>
    /* ── Token System ── */
    :root {{
      --ink:        #1a1410;
      --ink-mid:    #3d3530;
      --ink-light:  #6b625a;
      --ink-faint:  #a09890;
      --paper:      #f7f4ee;
      --paper-warm: #ede9e0;
      --rule:       #c8bfb0;
      --rule-heavy: #8c7e6e;
      --accent:     #8b1a1a;
    }}

    /* ── Dark Mode (system preference) ── */
    @media (prefers-color-scheme: dark) {{
      :root {{
        --ink:        #f0ece4;
        --ink-mid:    #cdc5bb;
        --ink-light:  #9d9288;
        --ink-faint:  #6b625a;
        --paper:      #16120e;
        --paper-warm: #1e1a15;
        --rule:       #2e2820;
        --rule-heavy: #4a4038;
        --accent:     #c9544e;
      }}
    }}

    /* ── Manual toggle overrides ── */
    html[data-theme="light"] {{
      --ink:        #1a1410;
      --ink-mid:    #3d3530;
      --ink-light:  #6b625a;
      --ink-faint:  #a09890;
      --paper:      #f7f4ee;
      --paper-warm: #ede9e0;
      --rule:       #c8bfb0;
      --rule-heavy: #8c7e6e;
      --accent:     #8b1a1a;
    }}
    html[data-theme="dark"] {{
      --ink:        #f0ece4;
      --ink-mid:    #cdc5bb;
      --ink-light:  #9d9288;
      --ink-faint:  #6b625a;
      --paper:      #16120e;
      --paper-warm: #1e1a15;
      --rule:       #2e2820;
      --rule-heavy: #4a4038;
      --accent:     #c9544e;
    }}

    /* ── Reset ── */
    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}

    body {{
      font-family: 'Source Serif 4', Georgia, 'Times New Roman', serif;
      background: var(--paper);
      color: var(--ink);
      transition: background 0.35s, color 0.35s;
      -webkit-font-smoothing: antialiased;
      -moz-osx-font-smoothing: grayscale;
    }}

    /* ── Layout ── */
    .page {{
      max-width: 680px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 6rem;
    }}

    /* ── Sun/Moon Sliding Toggle ── */
    .theme-toggle {{
      position: fixed;
      top: 1.2rem;
      right: 1.2rem;
      z-index: 99;
    }}
    .toggle-track {{
      width: 52px;
      height: 28px;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      border-radius: 14px;
      position: relative;
      cursor: pointer;
      transition: background 0.3s, border-color 0.3s;
    }}
    .toggle-knob {{
      position: absolute;
      top: 3px;
      left: 3px;
      width: 20px;
      height: 20px;
      border-radius: 50%;
      background: var(--ink);
      display: flex;
      align-items: center;
      justify-content: center;
      transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), background 0.3s;
    }}
    html[data-theme="dark"] .toggle-knob {{
      transform: translateX(24px);
    }}
    .icon-sun, .icon-moon {{
      position: absolute;
      width: 12px;
      height: 12px;
      transition: opacity 0.25s;
    }}
    /* Sun visible in dark mode (click to go light), moon visible in light mode */
    html[data-theme="light"] .icon-sun  {{ opacity: 0; }}
    html[data-theme="light"] .icon-moon {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-sun  {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-moon {{ opacity: 0; }}

    /* ── Nameplate ── */
    .nameplate {{
      text-align: center;
      padding: 1.8rem 0 1.2rem;
      border-bottom: 3px double var(--rule-heavy);
    }}
    .nameplate-title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(2.4rem, 6vw, 3.2rem);
      font-weight: 900;
      letter-spacing: -0.025em;
      line-height: 0.95;
      color: var(--ink);
    }}
    .nameplate-rule {{
      width: 48px;
      height: 1px;
      background: var(--accent);
      margin: 0.8rem auto;
    }}
    .nameplate-tagline {{
      font-size: 12px;
      font-style: italic;
      color: var(--ink-light);
      letter-spacing: 0.04em;
    }}

    /* ── Dateline bar ── */
    .dateline {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 0.55rem 0;
      border-bottom: 1px solid var(--rule);
    }}
    .dateline span {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--ink-faint);
    }}
    .dateline .center {{ color: var(--rule-heavy); }}

    /* ── Section Flag ── */
    .section-flag {{
      display: inline-block;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px;
      font-weight: 500;
      letter-spacing: 0.22em;
      text-transform: uppercase;
      background: var(--ink);
      color: var(--paper);
      padding: 3px 9px 4px;
      margin: 1.8rem 0 0;
    }}

    /* ── Article List ── */
    .articles {{ margin-top: 0; }}
    .article-item {{ border-bottom: 1px solid var(--rule); }}
    .article-item:first-of-type {{ border-top: 1px solid var(--rule); }}

    /* ── Article Header Button ── */
    .article-header {{
      width: 100%;
      background: none;
      border: none;
      padding: 1.15rem 0;
      text-align: left;
      cursor: pointer;
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 1rem;
      align-items: start;
      color: var(--ink);
    }}
    .article-header:focus-visible {{
      outline: 2px solid var(--accent);
      outline-offset: 2px;
    }}
    .article-header:hover .hed {{ color: var(--accent); }}

    .dispatch-meta {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--ink-faint);
      margin-bottom: 0.4rem;
    }}
    .hed {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: 1.15rem;
      font-weight: 700;
      line-height: 1.3;
      color: var(--ink);
      transition: color 0.2s;
    }}
    .source-line {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--ink-faint);
      margin-top: 0.4rem;
    }}

    /* ── Article expand Plus/Cross icon ── */
    .toggle-icon {{
      width: 22px;
      height: 22px;
      border-radius: 50%;
      border: 1px solid var(--rule);
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      margin-top: 0.25rem;
      transition: background 0.2s, border-color 0.2s;
    }}
    .toggle-icon svg {{
      stroke: var(--ink-light);
      transition: transform 0.32s cubic-bezier(0.4, 0, 0.2, 1), stroke 0.2s;
    }}
    .article-item.open .toggle-icon {{
      background: var(--ink);
      border-color: var(--ink);
    }}
    .article-item.open .toggle-icon svg {{
      stroke: var(--paper);
      transform: rotate(45deg);
    }}

    /* ── Expandable Body ── */
    .article-body {{
      max-height: 0;
      overflow: hidden;
      transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .article-body-inner {{
      display: grid;
      grid-template-columns: 3px 1fr;
      gap: 0 1.2rem;
      padding-bottom: 1.8rem;
    }}
    .body-accent-rule {{
      background: var(--accent);
      border-radius: 1px;
    }}
    .summary {{
      font-family: 'Source Serif 4', Georgia, serif;
      font-size: 1rem;
      font-weight: 300;
      font-style: italic;
      line-height: 1.8;
      color: var(--ink-mid);
      margin-bottom: 1rem;
    }}
    .read-more {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px;
      letter-spacing: 0.18em;
      text-transform: uppercase;
      color: var(--accent);
      text-decoration: none;
      border-bottom: 1px solid currentColor;
      padding-bottom: 1px;
      display: inline-flex;
      align-items: center;
      gap: 0.4rem;
      transition: opacity 0.15s;
    }}
    .read-more:hover {{ opacity: 0.65; }}

    /* ── Footer ── */
    .report-footer {{
      margin-top: 3.5rem;
      padding-top: 1rem;
      border-top: 3px double var(--rule-heavy);
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 0.5rem;
    }}
    .report-footer span {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px;
      letter-spacing: 0.12em;
      text-transform: uppercase;
      color: var(--ink-faint);
    }}
    .footer-brand {{
      font-family: 'Playfair Display', serif;
      font-size: 11px;
      font-style: italic;
      font-weight: 400;
      letter-spacing: 0;
      text-transform: none;
    }}

    /* ── Responsive ── */
    @media (max-width: 520px) {{
      .page {{ padding: 1.5rem 1rem 4rem; }}
      .nameplate-title {{ font-size: 2.2rem; }}
      .dateline {{ flex-direction: column; gap: 0.25rem; text-align: center; }}
    }}
  </style>
</head>
<body>

  <!-- Sun/Moon sliding theme toggle -->
  <div class="theme-toggle" id="theme-toggle" role="button" aria-label="Toggle theme" tabindex="0">
    <div class="toggle-track">
      <div class="toggle-knob">
        <!-- Sun icon (shown in dark mode) -->
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" stroke-width="2.5" stroke-linecap="round">
          <circle cx="12" cy="12" r="4"/>
          <line x1="12" y1="2"  x2="12" y2="5"/>
          <line x1="12" y1="19" x2="12" y2="22"/>
          <line x1="2"  y1="12" x2="5"  y2="12"/>
          <line x1="19" y1="12" x2="22" y2="12"/>
          <line x1="4.22"  y1="4.22"  x2="6.34"  y2="6.34"/>
          <line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/>
          <line x1="4.22"  y1="19.78" x2="6.34"  y2="17.66"/>
          <line x1="17.66" y1="6.34"  x2="19.78" y2="4.22"/>
        </svg>
        <!-- Moon icon (shown in light mode) -->
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" stroke-width="2.5" stroke-linecap="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </div>
    </div>
  </div>

  <div class="page">

    <!-- Nameplate — no kicker -->
    <header class="nameplate">
      <h1 class="nameplate-title">The Inference</h1>
      <div class="nameplate-rule"></div>
      <p class="nameplate-tagline">A curated daily briefing on artificial intelligence</p>
    </header>

    <!-- Dateline -->
    <div class="dateline">
      <span>{date_str}</span>
      <span class="center">· Synthesised at {time_str} ·</span>
      <span>{source_label}</span>
    </div>

    <span class="section-flag">Top Stories</span>

    <div class="articles">
"""

        # ── 2. Dynamic Content Injection ─────────────────────────────────────
        for i, art in enumerate(articles, 1):
            domain    = self._get_domain(art['link'])
            read_time = self._estimate_read_time(art.get('summary', ''))
            source    = art.get('source', domain).replace('_', ' ').title()
            ordinal   = f"Dispatch {i:02d}"

            html_template += f"""
      <div class="article-item">
        <button class="article-header" aria-expanded="false">
          <div>
            <p class="dispatch-meta">{ordinal} · {source}</p>
            <p class="hed">{art['title']}</p>
            <p class="source-line">{domain} · {read_time}</p>
          </div>
          <div class="toggle-icon" aria-hidden="true">
            <svg width="10" height="10" viewBox="0 0 10 10" fill="none" stroke-width="1.5" stroke-linecap="round">
              <line x1="5" y1="1" x2="5" y2="9"/>
              <line x1="1" y1="5" x2="9" y2="5"/>
            </svg>
          </div>
        </button>
        <div class="article-body" role="region">
          <div class="article-body-inner">
            <div class="body-accent-rule"></div>
            <div>
              <p class="summary">{art['summary']}</p>
              <a href="{art['link']}" class="read-more" target="_blank" rel="noopener noreferrer">
                Continue reading at {domain} →
              </a>
            </div>
          </div>
        </div>
      </div>
"""

        # ── 3. Close + Scripts ───────────────────────────────────────────────
        html_template += f"""
    </div><!-- /articles -->

    <footer class="report-footer">
      <span class="footer-brand">An agentic pipeline experiment by ThiruCoding</span>
      <span>All rights reserved · {now.year}</span>
    </footer>

  </div><!-- /page -->

  <script>
    // ── Exclusive accordion ──────────────────────────────────────────────
    document.querySelectorAll('.article-header').forEach(btn => {{
      btn.addEventListener('click', () => {{
        const item   = btn.closest('.article-item');
        const body   = item.querySelector('.article-body');
        const isOpen = item.classList.contains('open');

        document.querySelectorAll('.article-item.open').forEach(el => {{
          el.classList.remove('open');
          el.querySelector('.article-body').style.maxHeight = null;
          el.querySelector('.article-header').setAttribute('aria-expanded', 'false');
        }});

        if (!isOpen) {{
          item.classList.add('open');
          body.style.maxHeight = body.scrollHeight + 'px';
          btn.setAttribute('aria-expanded', 'true');
        }}
      }});
    }});

    // ── Sun/Moon sliding theme toggle ────────────────────────────────────
    const root    = document.documentElement;
    const toggle  = document.getElementById('theme-toggle');

    function applyTheme(mode) {{
      root.setAttribute('data-theme', mode);
      try {{ localStorage.setItem('the-inference-theme', mode); }} catch(e) {{}}
    }}

    // Init: stored → system → light
    const stored = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
    const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(stored || system);

    toggle.addEventListener('click', () => {{
      const current = root.getAttribute('data-theme') || 'light';
      applyTheme(current === 'light' ? 'dark' : 'light');
    }});

    toggle.addEventListener('keydown', e => {{
      if (e.key === 'Enter' || e.key === ' ') {{
        e.preventDefault();
        toggle.click();
      }}
    }});

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {{
      const saved = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
      if (!saved) applyTheme(e.matches ? 'dark' : 'light');
    }});
  </script>

</body>
</html>"""

        # ── 4. Write & Return ────────────────────────────────────────────────
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            return None