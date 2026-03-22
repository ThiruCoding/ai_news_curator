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

    def _get_timestamps(self):
        """Returns a consistent timestamp dict used by both report methods."""
        est = ZoneInfo("America/New_York")
        now = datetime.datetime.now(tz=datetime.timezone.utc).astimezone(est)
        tz_abbr = now.strftime("%Z")
        return {
            'now': now,
            'date_str': now.strftime("%A, %-d %B %Y").upper(),
            'time_str': now.strftime("%-I:%M %p") + f" {tz_abbr}",
            'main_filename': f"AI_News_{now.strftime('%d%b%Y').upper()}.html",
            'insights_filename': f"AI_News_Insights_{now.strftime('%d%b%Y').upper()}.html",
            'year': now.year,
        }

    def generate_html_report(self, articles, insights_filename=None):
        ts = self._get_timestamps()
        date_str         = ts['date_str']
        time_str         = ts['time_str']
        filename         = ts['main_filename']
        insights_file    = insights_filename or ts['insights_filename']
        source_count     = len(config.RSS_FEEDS)
        source_label     = f"Curated from {source_count} sources"

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        full_path = os.path.join(self.target_folder, filename)

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
    .page {{
      max-width: 680px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 6rem;
    }}
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
    html[data-theme="dark"] .toggle-knob {{ transform: translateX(24px); }}
    .icon-sun, .icon-moon {{
      position: absolute;
      width: 12px;
      height: 12px;
      transition: opacity 0.25s;
    }}
    html[data-theme="light"] .icon-sun  {{ opacity: 0; }}
    html[data-theme="light"] .icon-moon {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-sun  {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-moon {{ opacity: 0; }}
    .nameplate {{
      text-align: center;
      padding: 1.8rem 0 1.2rem;
      border-bottom: 3px double var(--rule-heavy);
    }}
    /* Easter egg — looks like plain text, behaves like a link */
    .nameplate-link {{
      display: inline;
      color: inherit;
      text-decoration: none;
      cursor: pointer;
    }}
    .nameplate-link:hover,
    .nameplate-link:focus {{ color: inherit; text-decoration: none; outline: none; }}
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
    .articles {{ margin-top: 0; }}
    .article-item {{ border-bottom: 1px solid var(--rule); }}
    .article-item:first-of-type {{ border-top: 1px solid var(--rule); }}
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
    .article-header:focus-visible {{ outline: 2px solid var(--accent); outline-offset: 2px; }}
    .article-header:hover .hed {{ color: var(--accent); }}
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
    .article-item.open .toggle-icon {{ background: var(--ink); border-color: var(--ink); }}
    .article-item.open .toggle-icon svg {{ stroke: var(--paper); transform: rotate(45deg); }}
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
    .body-accent-rule {{ background: var(--accent); border-radius: 1px; }}
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
    @media (max-width: 520px) {{
      .page {{ padding: 1.5rem 1rem 4rem; }}
      .nameplate-title {{ font-size: 2.2rem; }}
      .dateline {{ flex-direction: column; gap: 0.25rem; text-align: center; }}
    }}
  </style>
</head>
<body>

  <div class="theme-toggle" id="theme-toggle" role="button" aria-label="Toggle theme" tabindex="0">
    <div class="toggle-track">
      <div class="toggle-knob">
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
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" stroke-width="2.5" stroke-linecap="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </div>
    </div>
  </div>

  <div class="page">

    <header class="nameplate">
      <h1 class="nameplate-title">
        <a class="nameplate-link" href="{insights_file}" target="_blank" rel="noopener noreferrer">The Inference</a>
      </h1>
      <div class="nameplate-rule"></div>
      <p class="nameplate-tagline">A curated daily briefing on artificial intelligence</p>
    </header>

    <div class="dateline">
      <span>{date_str}</span>
      <span class="center">· Synthesised at {time_str} ·</span>
      <span>{source_label}</span>
    </div>

    <span class="section-flag">Top Stories</span>

    <div class="articles">
"""

        for i, art in enumerate(articles, 1):
            domain = self._get_domain(art['link'])
            html_template += f"""
      <div class="article-item">
        <button class="article-header" aria-expanded="false">
          <div>
            <p class="hed">{art['title']}</p>
            <p class="source-line">{domain}</p>
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

        html_template += f"""
    </div>

    <footer class="report-footer">
      <span class="footer-brand">An agentic pipeline experiment by ThiruCoding</span>
      <span>All rights reserved · {ts['year']}</span>
    </footer>

  </div>

  <script>
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

    const root   = document.documentElement;
    const toggle = document.getElementById('theme-toggle');
    function applyTheme(mode) {{
      root.setAttribute('data-theme', mode);
      try {{ localStorage.setItem('the-inference-theme', mode); }} catch(e) {{}}
    }}
    const stored = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
    const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    applyTheme(stored || system);
    toggle.addEventListener('click', () => {{
      const current = root.getAttribute('data-theme') || 'light';
      applyTheme(current === 'light' ? 'dark' : 'light');
    }});
    toggle.addEventListener('keydown', e => {{
      if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle.click(); }}
    }});
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {{
      const saved = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
      if (!saved) applyTheme(e.matches ? 'dark' : 'light');
    }});
  </script>

</body>
</html>"""

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            return None

    # ─────────────────────────────────────────────────────────────────────────
    # INSIGHTS PAGE
    # ─────────────────────────────────────────────────────────────────────────

    def generate_insights_report(self, pipeline_data):
        """
        Generates the 'Inside the Machine' transparency page.

        pipeline_data = {
            'feed_stats':        { feed_name: { 'fetched': int, 'curated': int } },
            'all_curated':       [ ...full curated pool with all scores... ],
            'top_10':            [ ...top 10 articles with all scores... ],
        }
        """
        ts               = self._get_timestamps()
        date_str         = ts['date_str']
        time_str         = ts['time_str']
        filename         = ts['insights_filename']
        main_file        = ts['main_filename']

        feed_stats   = pipeline_data.get('feed_stats', {})
        all_curated  = pipeline_data.get('all_curated', [])
        top_10       = pipeline_data.get('top_10', [])

        # ── Analyst article — top ranked from final_reports ──────────────
        final_reports = pipeline_data.get('final_reports', [])
        if final_reports:
            analyst_art = final_reports[0]
        else:
            analyst_art = {
                'title':   'NVIDIA announces Blackwell Ultra GPU with 1.4 TB/s memory bandwidth',
                'link':    'https://arstechnica.com/hardware/2025/blackwell-ultra-announcement',
                'summary': 'The Blackwell Ultra architecture from NVIDIA marks a significant leap in memory bandwidth, targeting large-scale AI training workloads. The new GPU delivers 1.4 TB/s of memory bandwidth alongside a substantially enlarged context window for inference tasks. Industry analysts expect the release to accelerate adoption of next-generation foundation models among hyperscale cloud providers.',
                'source':  'ARS_TECHNICA',
            }
        # Sanitise for safe JS injection — no single quotes or backslashes
        def js_safe(s):
            return s.replace('\\', '').replace("'", '\u2019').replace('\n', ' ').strip()

        analyst_title   = js_safe(analyst_art.get('title', ''))[:80]
        analyst_domain  = self._get_domain(analyst_art.get('link', ''))
        analyst_summary = js_safe(analyst_art.get('summary', ''))[:400]
        # Approximate word count from summary length — real text is much longer
        analyst_words   = max(800, len(analyst_art.get('summary', '').split()) * 18)

        # ── Computed pipeline stats ───────────────────────────────────────
        total_fetched  = sum(v['fetched']  for v in feed_stats.values())
        total_curated  = sum(v['curated']  for v in feed_stats.values())
        pass_rate      = round((total_curated / total_fetched * 100), 1) if total_fetched else 0
        sources_active = sum(1 for v in feed_stats.values() if v['fetched'] > 0)
        sources_total  = len(config.RSS_FEEDS)

        # ── Constellation data as JSON for JS ────────────────────────────
        import json

        # Tier colour map (indices used in JS)
        tier_map = {
            name: (
                'S' if config.SOURCE_WEIGHTS.get(name, 1.0) >= 1.6 else
                'A' if config.SOURCE_WEIGHTS.get(name, 1.0) >= 1.4 else
                'B' if config.SOURCE_WEIGHTS.get(name, 1.0) >= 1.2 else
                'C'
            )
            for name in config.RSS_FEEDS.keys()
        }

        top_10_titles = {a['title'] for a in top_10}

        constellation_data = json.dumps([
            {
                'title':      a['title'][:80],
                'source':     a['source'],
                'tech':       float(a.get('relevance_score', 0)),
                'biz':        float(a.get('relevance_score', 0)),
                'noise':      float(a.get('noise_score', 0)),
                'priority':   float(a.get('priority_score', 0)),
                'tier':       tier_map.get(a['source'], 'C'),
                'selected':   a['title'] in top_10_titles,
            }
            for a in all_curated
        ])

        # ── Source bar chart data ─────────────────────────────────────────
        source_bars = json.dumps([
            {
                'name':      name,
                'fetched':   feed_stats.get(name, {}).get('fetched', 0),
                'curated':   feed_stats.get(name, {}).get('curated', 0),
                'tier':      tier_map.get(name, 'C'),
                'in_top10':  any(a['source'] == name for a in top_10),
            }
            for name in config.RSS_FEEDS.keys()
        ])

        # ── Article scoring cards data ────────────────────────────────────
        cards_data = json.dumps([
            {
                'rank':      i + 1,
                'title':     a['title'],
                'source':    a['source'],
                'domain':    self._get_domain(a.get('link', '')),
                'link':      a.get('link', '#'),
                'tech':      float(a.get('relevance_score', 0)),
                'biz':       float(a.get('relevance_score', 0)),
                'noise':     float(a.get('noise_score', 0)),
                'priority':  float(a.get('priority_score', 0)),
                'weight':    config.SOURCE_WEIGHTS.get(a['source'],
                             config.SOURCE_WEIGHTS.get('DEFAULT', 1.0)),
            }
            for i, a in enumerate(top_10)
        ])

        # ── Vector definitions from config ───────────────────────────────
        vec_tech    = config.USER_INTEREST.strip()
        vec_biz     = config.USER_INTEREST_BUSINESS.strip()
        vec_noise   = config.NEGATIVE_FILTER.strip()

        # ── Pipeline examples: worst / median / best + top rejected ──────
        all_rejected = pipeline_data.get('all_rejected', [])

        sorted_curated = sorted(all_curated, key=lambda a: a.get('priority_score', 0))
        ex_articles = []
        if sorted_curated:
            worst  = sorted_curated[0]
            best   = sorted_curated[-1]
            mid_i  = len(sorted_curated) // 2
            median = sorted_curated[mid_i]
            if all_rejected:
                top_rejected = sorted(all_rejected, key=lambda a: a.get('noise_score', 0), reverse=True)[0]
            else:
                top_rejected = None

            def make_ex(a, label):
                return {
                    'label':    label,
                    'title':    a['title'][:72],
                    'source':   a['source'],
                    'tech':     float(a.get('relevance_score', 0)),
                    'biz':      float(a.get('relevance_score', 0)),
                    'noise':    float(a.get('noise_score', 0)),
                    'priority': float(a.get('priority_score', 0)),
                    'weight':   float(config.SOURCE_WEIGHTS.get(
                                    a['source'],
                                    config.SOURCE_WEIGHTS.get('DEFAULT', 1.0))),
                    'passed':   True,
                }

            ex_articles = [
                make_ex(worst,  'LOWEST SCORER'),
                make_ex(median, 'MEDIAN SCORER'),
                make_ex(best,   'TOP SCORER'),
            ]
            if top_rejected:
                rej = {
                    'label':    'REJECTED',
                    'title':    top_rejected['title'][:72],
                    'source':   top_rejected['source'],
                    'tech':     float(top_rejected.get('relevance_score', 0)),
                    'biz':      float(top_rejected.get('relevance_score', 0)),
                    'noise':    float(top_rejected.get('noise_score', 0)),
                    'priority': 0.0,
                    'weight':   float(config.SOURCE_WEIGHTS.get(
                                    top_rejected['source'],
                                    config.SOURCE_WEIGHTS.get('DEFAULT', 1.0))),
                    'passed':   False,
                }
                ex_articles.insert(0, rej)

        pipeline_examples = json.dumps(ex_articles)

        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)

        full_path = os.path.join(self.target_folder, filename)

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>The Inference — Inside the Machine — {date_str}</title>
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

      /* Tier colours */
      --tier-s: #5c7a6e;
      --tier-a: #6e6a3a;
      --tier-b: #4a6278;
      --tier-c: #7a5c5c;

      /* Score bar colours */
      --bar-tech:  #4a6278;
      --bar-biz:   #6e6a3a;
      --bar-noise: #8b3a3a;
    }}
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
        --tier-s: #7aaa98;
        --tier-a: #a8a464;
        --tier-b: #6a92b0;
        --tier-c: #aa7a7a;
        --bar-tech:  #6a92b0;
        --bar-biz:   #a8a464;
        --bar-noise: #c97070;
      }}
    }}
    html[data-theme="light"] {{
      --ink:        #1a1410; --ink-mid:    #3d3530; --ink-light:  #6b625a;
      --ink-faint:  #a09890; --paper:      #f7f4ee; --paper-warm: #ede9e0;
      --rule:       #c8bfb0; --rule-heavy: #8c7e6e; --accent:     #8b1a1a;
      --tier-s: #5c7a6e; --tier-a: #6e6a3a; --tier-b: #4a6278; --tier-c: #7a5c5c;
      --bar-tech: #4a6278; --bar-biz: #6e6a3a; --bar-noise: #8b3a3a;
    }}
    html[data-theme="dark"] {{
      --ink:        #f0ece4; --ink-mid:    #cdc5bb; --ink-light:  #9d9288;
      --ink-faint:  #6b625a; --paper:      #16120e; --paper-warm: #1e1a15;
      --rule:       #2e2820; --rule-heavy: #4a4038; --accent:     #c9544e;
      --tier-s: #7aaa98; --tier-a: #a8a464; --tier-b: #6a92b0; --tier-c: #aa7a7a;
      --bar-tech: #6a92b0; --bar-biz: #a8a464; --bar-noise: #c97070;
    }}

    *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      font-family: 'Source Serif 4', Georgia, serif;
      background: var(--paper);
      color: var(--ink);
      transition: background 0.35s, color 0.35s;
      -webkit-font-smoothing: antialiased;
    }}

    /* ── Layout ── */
    .page {{ max-width: 780px; margin: 0 auto; padding: 2.5rem 1.5rem 6rem; }}

    /* ── Theme Toggle ── */
    .theme-toggle {{
      position: fixed; top: 1.2rem; right: 1.2rem; z-index: 99;
    }}
    .toggle-track {{
      width: 52px; height: 28px; background: var(--paper-warm);
      border: 1px solid var(--rule); border-radius: 14px;
      position: relative; cursor: pointer; transition: background 0.3s, border-color 0.3s;
    }}
    .toggle-knob {{
      position: absolute; top: 3px; left: 3px; width: 20px; height: 20px;
      border-radius: 50%; background: var(--ink);
      display: flex; align-items: center; justify-content: center;
      transition: transform 0.3s cubic-bezier(0.4,0,0.2,1), background 0.3s;
    }}
    html[data-theme="dark"] .toggle-knob {{ transform: translateX(24px); }}
    .icon-sun, .icon-moon {{ position: absolute; width: 12px; height: 12px; transition: opacity 0.25s; }}
    html[data-theme="light"] .icon-sun  {{ opacity: 0; }}
    html[data-theme="light"] .icon-moon {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-sun  {{ opacity: 1; }}
    html[data-theme="dark"]  .icon-moon {{ opacity: 0; }}

    /* ── Nameplate ── */
    .nameplate {{
      text-align: center; padding: 1.8rem 0 1.2rem;
      border-bottom: 3px double var(--rule-heavy);
    }}
    .nameplate-eyebrow {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px; letter-spacing: 0.28em; text-transform: uppercase;
      color: var(--accent); margin-bottom: 0.6rem;
    }}
    .nameplate-title {{
      font-family: 'Playfair Display', Georgia, serif;
      font-size: clamp(1.6rem, 4vw, 2.2rem);
      font-weight: 700; letter-spacing: -0.02em; color: var(--ink);
    }}
    .nameplate-sub {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(1rem, 2.5vw, 1.25rem);
      font-style: italic; font-weight: 400;
      color: var(--ink-light); margin-top: 0.3rem;
    }}
    .nameplate-rule {{ width: 48px; height: 1px; background: var(--accent); margin: 0.8rem auto; }}

    /* ── Dateline ── */
    .dateline {{
      display: flex; justify-content: space-between; align-items: center;
      padding: 0.55rem 0; border-bottom: 1px solid var(--rule);
      flex-wrap: wrap; gap: 0.25rem;
    }}
    .dateline span {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px; letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--ink-faint);
    }}
    .dateline .center {{ color: var(--rule-heavy); }}
    .back-link {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px; letter-spacing: 0.15em; text-transform: uppercase;
      color: var(--accent); text-decoration: none;
      border-bottom: 1px solid currentColor; padding-bottom: 1px;
      transition: opacity 0.15s;
    }}
    .back-link:hover {{ opacity: 0.65; }}

    /* ── Section Flag ── */
    .section-flag {{
      display: inline-block;
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px; font-weight: 500; letter-spacing: 0.22em; text-transform: uppercase;
      background: var(--ink); color: var(--paper);
      padding: 3px 9px 4px; margin: 2.2rem 0 1.2rem;
    }}

    /* ── Pipeline Health Banner ── */
    .health-banner {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      border: 1px solid var(--rule);
      margin-bottom: 0.5rem;
    }}
    .stat-block {{
      padding: 1.2rem 1rem;
      border-right: 1px solid var(--rule);
      text-align: center;
    }}
    .stat-block:last-child {{ border-right: none; }}
    .stat-number {{
      font-family: 'Playfair Display', serif;
      font-size: clamp(1.8rem, 4vw, 2.4rem);
      font-weight: 900; color: var(--ink); line-height: 1;
    }}
    .stat-label {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7.5px; letter-spacing: 0.18em; text-transform: uppercase;
      color: var(--ink-faint); margin-top: 0.4rem;
    }}
    .stat-accent {{ color: var(--accent); }}

    /* ── Prioritizer Animation ── */
    .prioritizer-wrap {{
      width: 100%;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      overflow: hidden;
    }}
    #prioritizer-canvas {{
      display: block;
      width: 100%;
      height: auto;
    }}

    /* ── Analyst Agent Animation ── */
    .analyst-wrap {{
      width: 100%;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      overflow: hidden;
    }}
    #analyst-canvas {{
      display: block;
      width: 100%;
      height: auto;
    }}

    /* ── Source Bar Chart ── */
    .source-chart {{ display: flex; flex-direction: column; gap: 0.5rem; }}
    .source-row {{
      display: grid;
      grid-template-columns: 130px 1fr auto;
      align-items: center;
      gap: 0.6rem;
    }}
    .source-name {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8px; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--ink-light); text-align: right;
      white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
    }}
    .bar-track {{
      height: 14px;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      position: relative;
      overflow: hidden;
    }}
    .bar-fill {{
      height: 100%;
      transition: width 0.8s cubic-bezier(0.4, 0, 0.2, 1);
    }}
    .bar-count {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8px; color: var(--ink-faint); min-width: 24px; text-align: right;
    }}
    .top10-badge {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7px; letter-spacing: 0.1em; text-transform: uppercase;
      background: var(--accent); color: var(--paper);
      padding: 1px 4px; border-radius: 2px; margin-left: 4px;
    }}

    /* ── Scoring Cards ── */
    .cards-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 1.2rem;
    }}
    .score-card {{
      border: 1px solid var(--rule);
      padding: 1.2rem 1.2rem 1rem;
      background: var(--paper-warm);
      position: relative;
    }}
    .card-rank {{
      font-family: 'Playfair Display', serif;
      font-size: 3rem; font-weight: 900; line-height: 1;
      color: var(--rule); position: absolute;
      top: 0.6rem; right: 0.8rem;
    }}
    .card-title {{
      font-family: 'Playfair Display', serif;
      font-size: 0.95rem; font-weight: 700; line-height: 1.35;
      color: var(--ink); margin-bottom: 0.3rem;
      padding-right: 2.5rem;
    }}
    .card-domain {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7.5px; letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--ink-faint); margin-bottom: 0.9rem;
    }}
    .score-bars {{ display: flex; flex-direction: column; gap: 0.4rem; margin-bottom: 0.9rem; }}
    .score-bar-row {{ display: grid; grid-template-columns: 52px 1fr 32px; align-items: center; gap: 0.4rem; }}
    .score-bar-label {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7px; letter-spacing: 0.1em; text-transform: uppercase;
      color: var(--ink-faint); text-align: right;
    }}
    .score-bar-track {{
      height: 6px; background: var(--rule); border-radius: 1px; overflow: hidden;
    }}
    .score-bar-fill {{ height: 100%; border-radius: 1px; }}
    .score-bar-val {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7px; color: var(--ink-light); text-align: right;
    }}
    .card-footer {{
      display: flex; justify-content: space-between; align-items: center;
      border-top: 1px solid var(--rule); padding-top: 0.6rem; margin-top: 0.3rem;
    }}
    .card-priority {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 9px; color: var(--ink);
    }}
    .card-priority strong {{ color: var(--accent); }}
    .card-weight {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 7.5px; letter-spacing: 0.08em;
      background: var(--rule); color: var(--ink-light);
      padding: 2px 5px; border-radius: 2px;
    }}
    .card-read {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8px; letter-spacing: 0.15em; text-transform: uppercase;
      color: var(--accent); text-decoration: none;
      border-bottom: 1px solid currentColor; padding-bottom: 1px;
      transition: opacity 0.15s;
    }}
    .card-read:hover {{ opacity: 0.65; }}

    /* ── Vector Definitions ── */
    .vector-blocks {{ display: flex; flex-direction: column; gap: 1.2rem; }}
    .vector-block {{
      display: grid;
      grid-template-columns: 3px 1fr;
      gap: 0 1.2rem;
    }}
    .vector-rule {{ border-radius: 1px; }}
    .vector-label {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px; letter-spacing: 0.2em; text-transform: uppercase;
      color: var(--ink-faint); margin-bottom: 0.35rem;
    }}
    .vector-text {{
      font-family: 'Source Serif 4', serif;
      font-size: 0.95rem; font-weight: 300; font-style: italic;
      line-height: 1.75; color: var(--ink-mid);
    }}

    /* ── Footer ── */
    .report-footer {{
      margin-top: 3.5rem; padding-top: 1rem;
      border-top: 3px double var(--rule-heavy);
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 0.5rem;
    }}
    .report-footer span {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8.5px; letter-spacing: 0.12em; text-transform: uppercase;
      color: var(--ink-faint);
    }}
    .footer-brand {{
      font-family: 'Playfair Display', serif;
      font-size: 11px; font-style: italic; font-weight: 400;
      letter-spacing: 0; text-transform: none;
    }}

    /* ── Vector Pull Animation ── */
    .vector-pull-wrap {{
      width: 100%;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      overflow: hidden;
      position: relative;
    }}
    #vector-pull-canvas {{
      display: block;
      width: 100%;
      height: auto;
    }}
    .anim-caption {{
      font-family: 'IBM Plex Mono', monospace;
      font-size: 8px; letter-spacing: 0.14em; text-transform: uppercase;
      color: var(--ink-faint); text-align: center;
      padding: 0.5rem 0 0.7rem;
      border-top: 1px solid var(--rule);
      background: var(--paper-warm);
    }}

    /* ── Filter Funnel Animation ── */
    .funnel-wrap {{
      width: 100%;
      background: var(--paper-warm);
      border: 1px solid var(--rule);
      overflow: hidden;
    }}
    #funnel-canvas {{
      display: block;
      width: 100%;
      height: auto;
    }}

    /* ── Responsive ── */
    @media (max-width: 600px) {{
      .health-banner {{ grid-template-columns: repeat(2, 1fr); }}
      .stat-block:nth-child(2) {{ border-right: none; }}
      .stat-block:nth-child(3) {{ border-top: 1px solid var(--rule); }}
      .stat-block:nth-child(4) {{ border-top: 1px solid var(--rule); border-right: none; }}
      .cards-grid {{ grid-template-columns: 1fr; }}
      .source-row {{ grid-template-columns: 90px 1fr auto; }}
      .page {{ padding: 1.5rem 1rem 4rem; }}
    }}
  </style>
</head>
<body>

  <!-- Theme Toggle -->
  <div class="theme-toggle" id="theme-toggle" role="button" aria-label="Toggle theme" tabindex="0">
    <div class="toggle-track">
      <div class="toggle-knob">
        <svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" stroke-width="2.5" stroke-linecap="round">
          <circle cx="12" cy="12" r="4"/>
          <line x1="12" y1="2"  x2="12" y2="5"/><line x1="12" y1="19" x2="12" y2="22"/>
          <line x1="2"  y1="12" x2="5"  y2="12"/><line x1="19" y1="12" x2="22" y2="12"/>
          <line x1="4.22" y1="4.22" x2="6.34" y2="6.34"/><line x1="17.66" y1="17.66" x2="19.78" y2="19.78"/>
          <line x1="4.22" y1="19.78" x2="6.34" y2="17.66"/><line x1="17.66" y1="6.34" x2="19.78" y2="4.22"/>
        </svg>
        <svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="var(--paper)" stroke-width="2.5" stroke-linecap="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
      </div>
    </div>
  </div>

  <div class="page">

    <!-- Nameplate -->
    <header class="nameplate">
      <h1 class="nameplate-title">The Inference</h1>
      <p class="nameplate-sub">How today's briefing was assembled</p>
      <div class="nameplate-rule"></div>
    </header>

    <!-- Dateline -->
    <div class="dateline">
      <span>{date_str}</span>
      <span class="center">· Agentic Pipeline ran at {time_str} ·</span>
      <a href="{main_file}" class="back-link">← Back to briefing</a>
    </div>

    <!-- Section 1: Pipeline Health -->
    <span class="section-flag">Pipeline Health</span>
    <div class="health-banner">
      <div class="stat-block">
        <div class="stat-number">{total_fetched}</div>
        <div class="stat-label">Articles ingested</div>
      </div>
      <div class="stat-block">
        <div class="stat-number">{total_curated}</div>
        <div class="stat-label">Passed curation</div>
      </div>
      <div class="stat-block">
        <div class="stat-number stat-accent">{pass_rate}%</div>
        <div class="stat-label">Pass rate</div>
      </div>
      <div class="stat-block">
        <div class="stat-number">{sources_active}<span style="font-size:1.2rem;color:var(--ink-faint)">/{sources_total}</span></div>
        <div class="stat-label">Sources active</div>
      </div>
    </div>

    <!-- Section 2: Semantic Scoring -->
    <span class="section-flag">Semantic Scoring</span>
    <p style="font-family:'Source Serif 4',serif;font-size:0.88rem;font-style:italic;color:var(--ink-light);margin-bottom:0.8rem;line-height:1.6;">
      Each article title is converted into a 384-dimension vector and measured against three anchors using cosine similarity. The article is pulled toward whichever vector it most resembles.
    </p>
    <div class="vector-pull-wrap">
      <canvas id="vector-pull-canvas" style="display:block;width:100%;"></canvas>
      <div class="anim-caption">Three-vector cosine similarity pull — looping conceptual diagram</div>
    </div>

    <!-- Section 3: Curation Filter -->
    <span class="section-flag">Curation Filter</span>
    <p style="font-family:'Source Serif 4',serif;font-size:0.88rem;font-style:italic;color:var(--ink-light);margin-bottom:0.8rem;line-height:1.6;">
      Each article title is embedded by <strong style="font-style:normal;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:var(--ink-light);">SentenceTransformer · all-MiniLM-L6-v2</strong> into a 384-dimension vector, then scored against three anchors. Two sequential gates determine if it enters the curated pool. Cycling through four real articles from today's run.
    </p>
    <div class="funnel-wrap" style="position:relative;">
      <canvas id="funnel-canvas" style="display:block;width:100%;cursor:pointer;" title="Click to pause / resume"></canvas>
      <div class="anim-caption">Embedding → scoring → gate logic → priority — live worked examples</div>
    </div>

    <!-- Section 4: Curation Yield by Source -->
    <span class="section-flag">Curation Yield by Source</span>
    <div class="source-chart" id="source-chart"></div>

    <!-- Section 5: Prioritizer -->
    <span class="section-flag">Prioritizer</span>
    <p style="font-family:'Source Serif 4',serif;font-size:0.88rem;font-style:italic;color:var(--ink-light);margin-bottom:0.8rem;line-height:1.6;">
      The curated pool is ranked by priority score, then two filters are applied — a source diversity cap and a deduplication pass — before the top 10 are selected.
    </p>
    <div class="prioritizer-wrap">
      <canvas id="prioritizer-canvas" style="display:block;width:100%;"></canvas>
      <div class="anim-caption">Sort → diversity cap → deduplication → top 10 selection</div>
    </div>

    <!-- Section 6: Article Scoring -->
    <span class="section-flag">Article Scoring</span>
    <div class="cards-grid" id="cards-grid"></div>

    <!-- Section 7: Analyst Agent -->
    <span class="section-flag">Analyst Agent</span>
    <p style="font-family:'Source Serif 4',serif;font-size:0.88rem;font-style:italic;color:var(--ink-light);margin-bottom:0.8rem;line-height:1.6;">
      Each of the top 10 articles is fetched in full via <strong style="font-style:normal;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:var(--ink-light);">trafilatura</strong> a Python package designed to gather text on the web, then sent to <strong style="font-style:normal;font-family:'IBM Plex Mono',monospace;font-size:0.78rem;color:var(--ink-light);">gemma-3-12b-it</strong> model for grounded narrative synthesis.
    </p>
    <div class="analyst-wrap">
      <canvas id="analyst-canvas" style="display:block;width:100%;"></canvas>
      <div class="anim-caption">Fetch → extract → synthesise — illustrative pipeline diagram</div>
    </div>

    <!-- Section 7: Semantic Vectors -->
    <span class="section-flag">Semantic Vectors</span>
    <p style="font-family:'Source Serif 4',serif;font-size:0.88rem;font-style:italic;color:var(--ink-light);margin-bottom:1rem;line-height:1.6;">
      The three vector anchors that drive curation. Each article title is embedded and scored against all three using cosine similarity.
    </p>
    <div class="vector-blocks">
      <div class="vector-block">
        <div class="vector-rule" style="background:var(--bar-tech)"></div>
        <div>
          <div class="vector-label">Technical Interest Vector</div>
          <p class="vector-text">{vec_tech}</p>
        </div>
      </div>
      <div class="vector-block">
        <div class="vector-rule" style="background:var(--bar-biz)"></div>
        <div>
          <div class="vector-label">Business Interest Vector</div>
          <p class="vector-text">{vec_biz}</p>
        </div>
      </div>
      <div class="vector-block">
        <div class="vector-rule" style="background:var(--bar-noise)"></div>
        <div>
          <div class="vector-label">Negative Filter Vector</div>
          <p class="vector-text">{vec_noise}</p>
        </div>
      </div>
    </div>

    <footer class="report-footer">
      <span class="footer-brand">An agentic pipeline experiment by ThiruCoding</span>
      <span>All rights reserved · {ts['year']}</span>
    </footer>

  </div><!-- /page -->

  <script>
  // ── Data ─────────────────────────────────────────────────────────────────
  const CONSTELLATION      = {constellation_data};
  const SOURCE_BARS        = {source_bars};
  const CARDS              = {cards_data};
  const PIPELINE_EXAMPLES  = {pipeline_examples};

  // ── Theme helpers ────────────────────────────────────────────────────────
  const root   = document.documentElement;
  const toggle = document.getElementById('theme-toggle');

  function getCSSVar(name) {{
    return getComputedStyle(root).getPropertyValue(name).trim();
  }}

  function applyTheme(mode) {{
    root.setAttribute('data-theme', mode);
    try {{ localStorage.setItem('the-inference-theme', mode); }} catch(e) {{}}
    renderSourceChart();
    renderCards();
  }}

  const stored = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
  const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  // Apply theme silently on load without triggering rerender before DOM ready
  root.setAttribute('data-theme', stored || system);

  toggle.addEventListener('click', () => {{
    applyTheme(root.getAttribute('data-theme') === 'light' ? 'dark' : 'light');
  }});
  toggle.addEventListener('keydown', e => {{
    if (e.key === 'Enter' || e.key === ' ') {{ e.preventDefault(); toggle.click(); }}
  }});
  window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', e => {{
    const saved = (() => {{ try {{ return localStorage.getItem('the-inference-theme'); }} catch(e) {{ return null; }} }})();
    if (!saved) applyTheme(e.matches ? 'dark' : 'light');
  }});

  // ── Tier colour resolver ─────────────────────────────────────────────────
  function tierColor(tier) {{
    const map = {{ S: '--tier-s', A: '--tier-a', B: '--tier-b', C: '--tier-c' }};
    return getCSSVar(map[tier] || '--tier-c');
  }}

  // ── Section 4: Prioritizer Animation ────────────────────────────────────
  (function() {{
    const canvas = document.getElementById('prioritizer-canvas');
    if (!canvas || !CONSTELLATION.length) return;

    const DPR = window.devicePixelRatio || 1;
    let W, H, animId;

    // ── Phase durations — slower so labels are readable ─────────────────
    const PHASE_DUR = [1400, 1800, 900, 2800, 900, 2400, 900, 1600, 2200, 600];

    // ── Top padding constant — keeps dots clear of the phase label ────────
    const TOP_PAD = 0.14;  // 14% of H reserved for label area
    const TOTAL_PHASES = PHASE_DUR.length;

    let phase      = 0;
    let phaseStart = 0;
    let animFrame  = 0;

    // ── Easing ────────────────────────────────────────────────────────────
    function easeOut(t)   {{ return 1 - Math.pow(1 - t, 3); }}
    function easeInOut(t) {{ return t < 0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2; }}
    function lerp(a, b, t) {{ return a + (b - a) * t; }}

    // ── Build dot dataset from CONSTELLATION ─────────────────────────────
    // Sort by priority descending for the ranked order
    const sorted = [...CONSTELLATION].sort((a, b) => b.priority - a.priority);

    // Assign each dot a source-count tracker for diversity cap simulation
    const sourceCounts = {{}};
    const dotData = sorted.map((d, i) => {{
      sourceCounts[d.source] = (sourceCounts[d.source] || 0) + 1;
      const capFail  = sourceCounts[d.source] > 2;
      // Simple dedup: flag if title first 30 chars matches a higher-ranked dot
      const dedupFail = !capFail && sorted.slice(0, i).some(prev =>
        prev.title.slice(0, 30) === d.title.slice(0, 30)
      );
      const survives = !capFail && !dedupFail;
      const inTop10  = survives && sorted.filter(x => !x._capFail && !x._dedupFail).indexOf(d) < 10;
      return {{
        ...d,
        rankIdx:   i,
        capFail,
        dedupFail,
        survives,
        // positions set in setup()
        scatterX: 0, scatterY: 0,
        sortX: 0,    sortY: 0,
        fanX: 0,     fanY: 0,
        curX: 0,     curY: 0,
        opacity: 1,
        ejecting: false,
        ejectVX: 0,  ejectVY: 0,
      }};
    }});

    function setup() {{
      W = canvas.offsetWidth || 700;
      H = Math.round(W * 0.62);
      canvas.width  = W * DPR;
      canvas.height = H * DPR;
      canvas.style.height = H + 'px';

      const CX = W / 2;
      const colX   = Math.round(W * 0.38);
      const dotR   = Math.max(4, Math.round(W * 0.007));
      const dotAreaH = H * (1 - TOP_PAD - 0.08);
      const spacing  = Math.max(dotR * 2.8, Math.round(dotAreaH / dotData.length));

      dotData.forEach((d, i) => {{
        // Scatter: random positions below label area
        d.scatterX = Math.round(W * 0.08 + Math.random() * W * 0.80);
        d.scatterY = Math.round(H * (TOP_PAD + 0.02) + Math.random() * H * (1 - TOP_PAD - 0.10));
        // Sorted column: starts below label area
        d.sortX = colX;
        d.sortY = Math.round(H * (TOP_PAD + 0.02) + i * spacing);
        // Fan row: top 10 centred both horizontally and vertically in canvas
        const top10 = dotData.filter(x => x.survives).slice(0, 10);
        const t10i  = top10.indexOf(d);
        if (t10i >= 0) {{
          const rowW  = Math.min(W * 0.78, top10.length * dotR * 5);
          const rowX0 = CX - rowW / 2 + dotR * 2;
          d.fanX = Math.round(rowX0 + t10i * (rowW / (top10.length - 1 || 1)));
          d.fanY = Math.round(H * 0.52);  // vertically centred
        }}
        d.curX = d.scatterX;
        d.curY = d.scatterY;
        d.opacity = 1;
        d.ejecting = false;
      }});
    }}

    // ── Draw frame ────────────────────────────────────────────────────────
    function draw(ts) {{
      const ctx = canvas.getContext('2d');
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

      if (!phaseStart) phaseStart = ts;
      const elapsed = ts - phaseStart;
      const p = Math.min(elapsed / PHASE_DUR[phase], 1);

      if (elapsed >= PHASE_DUR[phase]) {{
        phaseStart = ts;
        phase = (phase + 1) % TOTAL_PHASES;
        if (phase === 0) setup(); // reset on loop
      }}

      const ep = easeOut(p);
      const eip = easeInOut(p);

      ctx.fillStyle = getCSSVar('--paper-warm');
      ctx.fillRect(0, 0, W, H);

      const dotR = Math.max(4, Math.round(W * 0.007));
      const CX   = W / 2;

      // ── Phase label — in-progress only, no completion messages ─────────
      const phaseLabels = [
        'UNSORTED CURATED POOL',
        'SORTING BY PRIORITY SCORE',
        '',
        'APPLYING SOURCE DIVERSITY CAP',
        '',
        'APPLYING DEDUPLICATION FILTER',
        '',
        'SELECTING TOP 10',
        '',
        '',
      ];
      const phaseLabel = phaseLabels[phase] || '';
      if (phaseLabel) {{
        ctx.font        = `500 ${{Math.round(11 * W/700)}}px 'IBM Plex Mono', monospace`;
        ctx.fillStyle   = getCSSVar('--ink-light');
        ctx.textAlign   = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(phaseLabel, CX, Math.round(H * 0.07));
      }}

      // ── Update dot positions per phase ───────────────────────────────
      dotData.forEach((d, i) => {{

        if (phase === 0) {{
          // Scatter — dots sit at scatter positions
          d.curX = d.scatterX;
          d.curY = d.scatterY;
          d.opacity = 1;
          d.ejecting = false;
        }}

        else if (phase === 1) {{
          // Sort — animate from scatter → sortY
          d.curX = lerp(d.scatterX, d.sortX, ep);
          d.curY = lerp(d.scatterY, d.sortY, ep);
          d.opacity = 1;
        }}

        else if (phase === 2) {{
          d.curX = d.sortX;
          d.curY = d.sortY;
        }}

        else if (phase === 3) {{
          const sweepY = H * TOP_PAD + (H * (1 - TOP_PAD - 0.06)) * p;
          if (d.capFail && d.sortY < sweepY && !d.ejecting) {{
            d.ejecting = true;
            d.ejectVX  = (Math.random() > 0.5 ? 1 : -1) * (2 + Math.random() * 2);
            d.ejectVY  = -0.5;
          }}
          if (d.ejecting) {{
            d.curX    += d.ejectVX;
            d.curY    += d.ejectVY;
            d.opacity  = Math.max(0, d.opacity - 0.025);
          }}
        }}

        else if (phase === 4) {{
          // Hold — culled dots stay invisible
          if (d.capFail) d.opacity = 0;
        }}

        else if (phase === 5) {{
          const sweepY = H * TOP_PAD + (H * (1 - TOP_PAD - 0.06)) * p;
          if (d.dedupFail && d.sortY < sweepY && !d.ejecting) {{
            d.ejecting = true;
            d.ejectVX  = (Math.random() > 0.5 ? 0.8 : -0.8);
            d.ejectVY  = -0.3;
          }}
          if (d.ejecting) {{
            d.curX    += d.ejectVX;
            d.curY    += d.ejectVY;
            d.opacity  = Math.max(0, d.opacity - 0.03);
          }}
        }}

        else if (phase === 6) {{
          if (d.capFail || d.dedupFail) d.opacity = 0;
        }}

        else if (phase === 7) {{
          // Fan out — only top 10 survivors with a fanX position are visible
          if (d.survives && d.fanX) {{
            d.curX = lerp(d.sortX, d.fanX, ep);
            d.curY = lerp(d.sortY, d.fanY, ep);
            d.opacity = 1;
          }} else {{
            // Everything else — non-survivors AND survivors without fanX — hidden
            d.opacity = 0;
          }}
        }}

        else if (phase === 8) {{
          // Hold at fan positions — same rule
          if (d.survives && d.fanX) {{
            d.curX = d.fanX;
            d.curY = d.fanY;
            d.opacity = 1;
          }} else {{
            d.opacity = 0;
          }}
        }}

        else if (phase === 9) {{
          // Instant hide — no fade, nothing visible at loop boundary
          d.opacity = 0;
        }}
      }});

      // ── Draw sweep line ──────────────────────────────────────────────
      if (phase === 3 || phase === 5) {{
        const sweepY   = H * TOP_PAD + (H * (1 - TOP_PAD - 0.06)) * p;
        const sweepCol = phase === 3 ? getCSSVar('--bar-biz') : getCSSVar('--bar-tech');
        const sweepLbl = phase === 3 ? 'SOURCE CAP · MAX 2 PER SOURCE' : 'DEDUP · FIRST 30 CHARS MATCH';
        ctx.strokeStyle = sweepCol;
        ctx.lineWidth   = 1;
        ctx.globalAlpha = 0.5;
        ctx.setLineDash([4, 4]);
        ctx.beginPath();
        ctx.moveTo(W * 0.06, sweepY);
        ctx.lineTo(W * 0.72, sweepY);
        ctx.stroke();
        ctx.setLineDash([]);
        ctx.globalAlpha = 1;
        ctx.font      = `500 ${{Math.round(9 * W/700)}}px 'IBM Plex Mono', monospace`;
        ctx.fillStyle = sweepCol;
        ctx.textAlign = 'left';
        ctx.textBaseline = 'bottom';
        ctx.fillText(sweepLbl, W * 0.06, sweepY - 4);
      }}

      // ── Draw priority score bars (phases 1-6) ────────────────────────
      if (phase >= 1 && phase <= 6) {{
        const barX   = Math.round(W * 0.42);
        const barMaxW = Math.round(W * 0.38);
        const maxP   = Math.max(...dotData.map(d => d.priority), 0.001);
        const barAlpha = phase <= 2 ? ep : (phase <= 6 ? 1 : 0);

        dotData.forEach(d => {{
          if (d.opacity <= 0) return;
          const barW = Math.round((d.priority / maxP) * barMaxW);
          const barH = Math.max(2, dotR - 1);
          const col  = tierColor(d.tier);
          ctx.fillStyle   = col;
          ctx.globalAlpha = d.opacity * 0.35 * barAlpha;
          ctx.fillRect(barX, d.curY - barH/2, barW, barH);
          ctx.globalAlpha = 1;

          // Score label — readable size and colour
          if (phase >= 2 && phase <= 6 && d.opacity > 0.3) {{
            ctx.font      = `500 ${{Math.round(9 * W/700)}}px 'IBM Plex Mono', monospace`;
            ctx.fillStyle = getCSSVar('--ink-light');
            ctx.textAlign = 'left';
            ctx.textBaseline = 'middle';
            ctx.globalAlpha = d.opacity * 0.85;
            ctx.fillText(d.priority.toFixed(3), barX + barW + 5, d.curY);
            ctx.globalAlpha = 1;
          }}
        }});
      }}

      // ── Draw rank numbers (phases 7-8) ──────────────────────────────
      if (phase === 7 || phase === 8) {{
        const top10  = dotData.filter(x => x.survives).slice(0, 10);
        const fadeIn = phase === 7 ? easeOut(p) : 1;
        top10.forEach((d, i) => {{
          if (d.opacity <= 0) return;
          ctx.font      = `500 ${{Math.round(10 * W/700)}}px 'IBM Plex Mono', monospace`;
          ctx.fillStyle = getCSSVar('--ink-light');
          ctx.textAlign = 'center';
          ctx.textBaseline = 'bottom';
          ctx.globalAlpha = d.opacity * fadeIn;
          ctx.fillText(`#${{i+1}}`, d.curX, d.curY - dotR - 3);
          ctx.globalAlpha = 1;
        }});
      }}

      // ── Draw column axis label (phases 2, 4, 6 only — not during sweeps) ──
      if (phase === 2 || phase === 4 || phase === 6) {{
        ctx.font      = `500 ${{Math.round(9 * W/700)}}px 'IBM Plex Mono', monospace`;
        ctx.fillStyle = getCSSVar('--ink-light');
        ctx.textAlign = 'center';
        ctx.textBaseline = 'bottom';
        ctx.globalAlpha = 0.8;
        ctx.fillText('PRIORITY SCORE →', Math.round(W * 0.60), H - 8);
        ctx.globalAlpha = 1;
      }}

      // ── Draw dots ────────────────────────────────────────────────────
      dotData.forEach(d => {{
        // In fan phases, only draw the top 10 survivors — hide everything else
        if ((phase === 7 || phase === 8) && !d.survives) return;
        if (d.opacity <= 0) return;
        const col = tierColor(d.tier);
        ctx.beginPath();
        ctx.arc(d.curX, d.curY, dotR, 0, Math.PI * 2);
        ctx.fillStyle   = col;
        ctx.globalAlpha = d.opacity * 0.85;
        ctx.fill();

        // Ring on top 10 in final phases
        if ((phase === 7 || phase === 8) && d.survives) {{
          ctx.beginPath();
          ctx.arc(d.curX, d.curY, dotR + 3, 0, Math.PI * 2);
          ctx.strokeStyle = col;
          ctx.lineWidth   = 1.5;
          ctx.globalAlpha = d.opacity * 0.6;
          ctx.stroke();
        }}
        ctx.globalAlpha = 1;
      }});

      animId = requestAnimationFrame(draw);
    }}

    function start() {{
      if (animId) cancelAnimationFrame(animId);
      phase = 0; phaseStart = 0;
      setup();
      animId = requestAnimationFrame(draw);
    }}

    window.addEventListener('resize', () => {{
      if (animId) cancelAnimationFrame(animId);
      clearTimeout(canvas._resizeTimer);
      canvas._resizeTimer = setTimeout(start, 120);
    }});

    start();
  }})();

  // Redraw on resize (legacy — kept for theme toggle rerender)
  let resizeTimer;
  window.addEventListener('resize', () => {{
    clearTimeout(resizeTimer);
  }});

  // ── Section 3: Source Bar Chart ──────────────────────────────────────────
  function renderSourceChart() {{
    const container = document.getElementById('source-chart');
    if (!container) return;
    container.innerHTML = '';

    const maxCurated = Math.max(...SOURCE_BARS.map(s => s.curated), 1);

    SOURCE_BARS.forEach(s => {{
      const pct  = (s.curated / maxCurated * 100).toFixed(1);
      const color = getCSSVar(
        s.tier === 'S' ? '--tier-s' :
        s.tier === 'A' ? '--tier-a' :
        s.tier === 'B' ? '--tier-b' : '--tier-c'
      );
      const badge = s.in_top10 ? '<span class="top10-badge">Top 10</span>' : '';

      container.innerHTML += `
        <div class="source-row">
          <div class="source-name">${{s.name.toLowerCase().replace(/_/g,' ')}}</div>
          <div class="bar-track">
            <div class="bar-fill" style="width:${{pct}}%;background:${{color}};opacity:0.8"></div>
          </div>
          <div class="bar-count">${{s.curated}}${{badge}}</div>
        </div>`;
    }});
  }}

  // ── Section 4: Scoring Cards ─────────────────────────────────────────────
  function renderCards() {{
    const grid = document.getElementById('cards-grid');
    if (!grid) return;
    grid.innerHTML = '';

    const techColor  = getCSSVar('--bar-tech');
    const bizColor   = getCSSVar('--bar-biz');
    const noiseColor = getCSSVar('--bar-noise');

    CARDS.forEach(c => {{
      const techPct  = (c.tech  * 100).toFixed(1);
      const bizPct   = (c.biz   * 100).toFixed(1);
      const noisePct = (c.noise * 100).toFixed(1);

      grid.innerHTML += `
        <div class="score-card">
          <div class="card-rank">${{String(c.rank).padStart(2,'0')}}</div>
          <div class="card-title">${{c.title}}</div>
          <div class="card-domain">${{c.domain}}</div>
          <div class="score-bars">
            <div class="score-bar-row">
              <div class="score-bar-label">Tech</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:${{techPct}}%;background:${{techColor}}"></div></div>
              <div class="score-bar-val">${{c.tech.toFixed(3)}}</div>
            </div>
            <div class="score-bar-row">
              <div class="score-bar-label">Biz</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:${{bizPct}}%;background:${{bizColor}}"></div></div>
              <div class="score-bar-val">${{c.biz.toFixed(3)}}</div>
            </div>
            <div class="score-bar-row">
              <div class="score-bar-label">Noise</div>
              <div class="score-bar-track"><div class="score-bar-fill" style="width:${{noisePct}}%;background:${{noiseColor}}"></div></div>
              <div class="score-bar-val">${{c.noise.toFixed(3)}}</div>
            </div>
          </div>
          <div class="card-footer">
            <div>
              <div class="card-priority">Score: <strong>${{c.priority.toFixed(4)}}</strong></div>
              <div class="card-weight">×${{c.weight}} authority</div>
            </div>
            <a href="${{c.link}}" class="card-read" target="_blank" rel="noopener noreferrer">Read →</a>
          </div>
        </div>`;
    }});
  }}

  // ── Vector Pull Animation ────────────────────────────────────────────────
  (function() {{
    const canvas = document.getElementById('vector-pull-canvas');
    if (!canvas) return;

    const DPR = window.devicePixelRatio || 1;
    let W, H, cx, cy, animId;

    // Three anchor vectors: Tech, Biz, Noise
    const ANCHORS = [
      {{ label: 'TECH',     angle: -Math.PI / 2,         color: '--bar-tech'  }},
      {{ label: 'BUSINESS', angle: -Math.PI / 2 + (2 * Math.PI / 3),  color: '--bar-biz'   }},
      {{ label: 'NOISE',    angle: -Math.PI / 2 + (4 * Math.PI / 3),  color: '--bar-noise' }},
    ];

    // Article node state
    const node = {{ x: 0, y: 0, vx: 0, vy: 0 }};
    // Simulated scores that oscillate over time
    let t = 0;

    function setup() {{
      W = canvas.offsetWidth || 560;
      H = Math.round(W * 0.52);
      canvas.width  = W * DPR;
      canvas.height = H * DPR;
      canvas.style.height = H + 'px';
      cx = W / 2;
      cy = H / 2;
      node.x = cx;
      node.y = cy;
    }}

    function getAnchorPos(anchor, radius) {{
      return {{
        x: cx + Math.cos(anchor.angle) * radius,
        y: cy + Math.sin(anchor.angle) * radius,
      }};
    }}

    function draw() {{
      const ctx = canvas.getContext('2d');
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

      // Background
      ctx.fillStyle = getCSSVar('--paper-warm');
      ctx.fillRect(0, 0, W, H);

      const radius = Math.min(W, H) * 0.34;

      // Oscillating scores — Tech and Biz compete, Noise stays lower
      const techScore = 0.38 + 0.28 * Math.sin(t * 0.7);
      const bizScore  = 0.32 + 0.24 * Math.sin(t * 0.5 + 1.2);
      const noiseScore = 0.18 + 0.10 * Math.sin(t * 0.9 + 2.4);
      const scores = [techScore, bizScore, noiseScore];

      // Compute target position as weighted sum of anchor positions
      const totalScore = techScore + bizScore + noiseScore;
      let tx = 0, ty = 0;
      ANCHORS.forEach((a, i) => {{
        const pos = getAnchorPos(a, radius * 0.72);
        tx += pos.x * (scores[i] / totalScore);
        ty += pos.y * (scores[i] / totalScore);
      }});

      // Spring physics toward target
      const spring = 0.06, damp = 0.78;
      node.vx = (node.vx + (tx - node.x) * spring) * damp;
      node.vy = (node.vy + (ty - node.y) * spring) * damp;
      node.x += node.vx;
      node.y += node.vy;

      // Draw tension lines from node to each anchor
      ANCHORS.forEach((a, i) => {{
        const pos = getAnchorPos(a, radius);
        const score = scores[i];
        const col = getCSSVar(a.color);

        // Line thickness proportional to score
        ctx.beginPath();
        ctx.moveTo(node.x, node.y);
        ctx.lineTo(pos.x, pos.y);
        ctx.strokeStyle = col;
        ctx.lineWidth   = 1 + score * 5;
        ctx.globalAlpha = 0.25 + score * 0.55;
        ctx.stroke();
        ctx.globalAlpha = 1;

        // Anchor well circle
        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 22, 0, Math.PI * 2);
        ctx.fillStyle = col;
        ctx.globalAlpha = 0.12;
        ctx.fill();
        ctx.globalAlpha = 1;

        ctx.beginPath();
        ctx.arc(pos.x, pos.y, 22, 0, Math.PI * 2);
        ctx.strokeStyle = col;
        ctx.lineWidth = 1.5;
        ctx.globalAlpha = 0.6;
        ctx.stroke();
        ctx.globalAlpha = 1;

        // Score value inside well
        ctx.fillStyle = getCSSVar('--ink-light');
        ctx.font = `500 9px 'IBM Plex Mono', monospace`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(score.toFixed(2), pos.x, pos.y + 14);

        // Anchor label above well
        ctx.fillStyle = getCSSVar('--ink-faint');
        ctx.font = `500 8px 'IBM Plex Mono', monospace`;
        ctx.letterSpacing = '0.14em';
        const labelOff = a.angle < -Math.PI * 0.9 ? -30 : (a.angle > 0 ? 30 : 30);
        ctx.fillText(a.label, pos.x, pos.y - 30);
      }});

      // Article node
      const winning = scores.indexOf(Math.max(...scores));
      const nodeColor = getCSSVar(ANCHORS[winning].color);

      ctx.beginPath();
      ctx.arc(node.x, node.y, 9, 0, Math.PI * 2);
      ctx.fillStyle = nodeColor;
      ctx.globalAlpha = 0.9;
      ctx.fill();
      ctx.globalAlpha = 1;

      ctx.beginPath();
      ctx.arc(node.x, node.y, 13, 0, Math.PI * 2);
      ctx.strokeStyle = nodeColor;
      ctx.lineWidth = 1;
      ctx.globalAlpha = 0.35;
      ctx.stroke();
      ctx.globalAlpha = 1;

      // "ARTICLE" label below node
      ctx.fillStyle = getCSSVar('--ink-faint');
      ctx.font = `500 7px 'IBM Plex Mono', monospace`;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'top';
      ctx.fillText('ARTICLE', node.x, node.y + 16);

      t += 0.018;
      animId = requestAnimationFrame(draw);
    }}

    function start() {{
      if (animId) cancelAnimationFrame(animId);
      setup();
      draw();
    }}

    window.addEventListener('resize', () => {{
      if (animId) cancelAnimationFrame(animId);
      clearTimeout(canvas._resizeTimer);
      canvas._resizeTimer = setTimeout(start, 120);
    }});

    start();
  }})();

  // ── Curation Filter: Option D — Cycling Pipeline Diagram ───────────────
  (function() {{
    const canvas = document.getElementById('funnel-canvas');
    if (!canvas || !PIPELINE_EXAMPLES.length) return;

    const DPR = window.devicePixelRatio || 1;
    let W, H, animId;
    let paused = false;

    // ── Canvas click toggles pause ────────────────────────────────────────
    canvas.addEventListener('click', () => {{
      paused = !paused;
      if (paused) {{
        canvas._pausedAt = performance.now();
      }} else {{
        const pausedDuration = performance.now() - canvas._pausedAt;
        stageStart += pausedDuration;
      }}
    }});
    // ── Animation state machine ──────────────────────────────────────────
    // Stages per article (ms each):
    // 0: title appears          800ms
    // 1: embedding pulse        900ms
    // 2: score bars animate    1200ms
    // 3: gate 1 decision        700ms
    // 4: gate 2 decision        700ms  (skipped if failed gate 1)
    // 5: priority calc          900ms  (skipped if failed)
    // 6: hold                  1400ms
    // 7: fade out               600ms

    const STAGE_DUR = [800, 900, 1200, 700, 700, 900, 1400, 600];
    const TOTAL_STAGES = STAGE_DUR.length;

    let articleIdx  = 0;
    let stage       = 0;
    let stageStart  = 0;
    let globalAlpha = 1;

    function totalDur(ex) {{
      // If rejected: skip stages 5 (priority)
      // If failed gate 1: skip stages 4 and 5
      return STAGE_DUR.reduce((s, d) => s + d, 0);
    }}

    function setup() {{
      W = canvas.offsetWidth || 680;
      H = Math.round(W * 0.88);
      canvas.width  = W * DPR;
      canvas.height = H * DPR;
      canvas.style.height = H + 'px';
    }}

    // ── Layout constants (computed from W/H) ────────────────────────────
    function layout() {{
      const PAD   = Math.round(W * 0.05);
      const CX    = W / 2;
      const ROW_TITLE   = Math.round(H * 0.13);
      const ROW_EMBED   = Math.round(H * 0.24);
      const ROW_SCORES  = Math.round(H * 0.40);
      const ROW_GATES   = Math.round(H * 0.63);
      const ROW_PRIORITY= Math.round(H * 0.82);
      const BAR_W       = Math.round(W * 0.46);
      const BAR_H       = Math.round(H * 0.028);
      const BAR_X       = CX - BAR_W / 2;
      return {{ PAD, CX, ROW_TITLE, ROW_EMBED, ROW_SCORES, ROW_GATES, ROW_PRIORITY, BAR_W, BAR_H, BAR_X }};
    }}

    // ── Easing ──────────────────────────────────────────────────────────
    function easeOut(t) {{ return 1 - Math.pow(1 - t, 3); }}
    function easeInOut(t) {{ return t < 0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2; }}

    // ── Draw helpers ────────────────────────────────────────────────────
    function mono(ctx, size) {{
      ctx.font = `500 ${{Math.round(size * Math.min(W/680, 1))}}px 'IBM Plex Mono', monospace`;
    }}
    function serif(ctx, size, weight) {{
      ctx.font = `${{weight||400}} ${{Math.round(size * Math.min(W/680, 1))}}px 'Source Serif 4', serif`;
    }}

    function drawConnector(ctx, x1, y1, x2, y2, progress, color) {{
      ctx.save();
      ctx.strokeStyle = color;
      ctx.lineWidth   = 1;
      ctx.globalAlpha = 0.35;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(x1, y1);
      const ex = x1 + (x2 - x1) * progress;
      const ey = y1 + (y2 - y1) * progress;
      ctx.lineTo(ex, ey);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.restore();
    }}

    function drawScoreBar(ctx, x, y, w, h, value, color, label, alpha) {{
      ctx.save();
      ctx.globalAlpha = alpha;
      // Track
      ctx.fillStyle = getCSSVar('--rule');
      ctx.fillRect(x, y, w, h);
      // Fill
      ctx.fillStyle = color;
      ctx.fillRect(x, y, w * Math.min(value / 0.6, 1), h);
      // Threshold line at 0.22/0.6
      const tx = x + w * (0.22 / 0.6);
      ctx.strokeStyle = getCSSVar('--ink-faint');
      ctx.lineWidth   = 1;
      ctx.setLineDash([2, 2]);
      ctx.beginPath(); ctx.moveTo(tx, y - 2); ctx.lineTo(tx, y + h + 2); ctx.stroke();
      ctx.setLineDash([]);
      // Label — ink-mid so it reads clearly
      mono(ctx, 9);
      ctx.fillStyle    = getCSSVar('--ink-mid');
      ctx.textAlign    = 'right';
      ctx.textBaseline = 'middle';
      ctx.fillText(label, x - 6, y + h / 2);
      // Value — ink-mid
      ctx.fillStyle  = getCSSVar('--ink-mid');
      ctx.textAlign  = 'left';
      ctx.fillText(value.toFixed(3), x + w + 6, y + h / 2);
      ctx.restore();
    }}

    function drawDecision(ctx, cx, y, passed, gateNum, condition, alpha) {{
      ctx.save();
      ctx.globalAlpha = alpha;
      const col = passed ? getCSSVar('--bar-tech') : getCSSVar('--bar-noise');
      const lbl = passed ? '✓ PASS' : '✗ FAIL';
      const bw  = Math.round(W * 0.52);
      const bx  = cx - bw / 2;

      // Horizontal rule only — no box
      ctx.strokeStyle = getCSSVar('--rule');
      ctx.lineWidth   = 1;
      ctx.beginPath();
      ctx.moveTo(bx, y);
      ctx.lineTo(bx + bw, y);
      ctx.stroke();

      // Gate label left — ink-mid for readability
      mono(ctx, 9);
      ctx.fillStyle    = getCSSVar('--ink-mid');
      ctx.textAlign    = 'left';
      ctx.textBaseline = 'middle';
      ctx.fillText(`GATE ${{gateNum}} · ${{condition}}`, bx, y + Math.round(H * 0.022));

      // Decision right — coloured
      mono(ctx, 10);
      ctx.fillStyle  = col;
      ctx.textAlign  = 'right';
      ctx.fillText(lbl, bx + bw, y + Math.round(H * 0.022));
      ctx.restore();
    }}

    // ── Main draw loop ───────────────────────────────────────────────────
    function draw(ts) {{
      const ctx = canvas.getContext('2d');
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

      // Background
      ctx.fillStyle = getCSSVar('--paper-warm');
      ctx.fillRect(0, 0, W, H);

      const ex  = PIPELINE_EXAMPLES[articleIdx];
      const L   = layout();

      // Advance stage only when not paused
      if (!paused) {{
        if (!stageStart) stageStart = ts;
        const elapsed = ts - stageStart;
        if (elapsed >= STAGE_DUR[stage]) {{
          stageStart = ts;
          stage++;
          if (stage >= TOTAL_STAGES) {{
            stage       = 0;
            articleIdx  = (articleIdx + 1) % PIPELINE_EXAMPLES.length;
          }}
        }}
      }}

      const elapsed = stageStart ? ts - stageStart : 0;
      const stageP = paused ? 1 : Math.min(elapsed / STAGE_DUR[stage], 1);

      // Overall card fade
      const cardAlpha = stage === TOTAL_STAGES - 1 ? 1 - easeInOut(stageP) : 1;

      ctx.save();
      ctx.globalAlpha = cardAlpha;

      // ── Article label badge ──────────────────────────────────────────
      const labelCol =
        ex.label === 'REJECTED'      ? getCSSVar('--bar-noise') :
        ex.label === 'TOP SCORER'    ? getCSSVar('--bar-tech')  :
        ex.label === 'MEDIAN SCORER' ? getCSSVar('--bar-biz')   :
                                       getCSSVar('--ink-faint');

      const badgeY = L.ROW_TITLE - Math.round(H * 0.090);
      mono(ctx, 14);
      ctx.textAlign    = 'center';
      ctx.textBaseline = 'middle';
      const badgeText  = ex.label;
      const badgeW     = ctx.measureText(badgeText).width + 32;
      const badgeH     = Math.round(H * 0.052);
      ctx.fillStyle   = labelCol;
      ctx.globalAlpha = cardAlpha * 0.18;
      ctx.beginPath();
      ctx.roundRect(L.CX - badgeW/2, badgeY - badgeH/2, badgeW, badgeH, badgeH/2);
      ctx.fill();
      ctx.globalAlpha = cardAlpha;
      ctx.strokeStyle = labelCol;
      ctx.lineWidth   = 1.5;
      ctx.globalAlpha = cardAlpha * 0.5;
      ctx.beginPath();
      ctx.roundRect(L.CX - badgeW/2, badgeY - badgeH/2, badgeW, badgeH, badgeH/2);
      ctx.stroke();
      ctx.globalAlpha = cardAlpha;
      ctx.fillStyle = labelCol;
      ctx.fillText(badgeText, L.CX, badgeY);

      // ── Stage 0+: Article title ──────────────────────────────────────
      if (stage >= 0) {{
        const a = stage === 0 ? easeOut(stageP) : 1;
        ctx.save();
        ctx.globalAlpha *= a;
        serif(ctx, 13, 700);
        ctx.fillStyle    = getCSSVar('--ink');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        const maxW = W * 0.82;
        const words = ex.title.split(' ');
        let line1 = '', line2 = '';
        let building = '';
        for (const w of words) {{
          const test = building ? building + ' ' + w : w;
          ctx.font = `700 ${{Math.round(13 * Math.min(W/680,1))}}px 'Source Serif 4', serif`;
          if (ctx.measureText(test).width > maxW && building) {{
            if (!line1) {{ line1 = building; building = w; }}
            else {{ line2 = building + (building ? ' ' : '') + words.slice(words.indexOf(w)).join(' '); break; }}
          }} else {{ building = test; }}
        }}
        if (!line1) {{ line1 = building; }} else if (!line2) {{ line2 = building; }}
        const lineH = Math.round(H * 0.042);
        ctx.fillText(line1, L.CX, L.ROW_TITLE - (line2 ? lineH/2 : 0));
        if (line2) ctx.fillText(line2, L.CX, L.ROW_TITLE + lineH/2);

        // Source — larger and ink-mid so it reads clearly
        mono(ctx, 10);
        ctx.fillStyle = getCSSVar('--ink-mid');
        ctx.fillText(ex.source.toLowerCase().replace(/_/g,' '), L.CX, L.ROW_TITLE + lineH + 6);
        ctx.restore();
      }}

      // ── Connector: title → embedding ────────────────────────────────
      if (stage >= 1) {{
        const p = stage === 1 ? easeOut(stageP * 0.5) : 1;
        drawConnector(ctx, L.CX, L.ROW_TITLE + Math.round(H*0.04), L.CX, L.ROW_EMBED - Math.round(H*0.04), p, getCSSVar('--rule-heavy'));
      }}

      // ── Stage 1+: Embedding block — no box, just model name + cells ──
      if (stage >= 1) {{
        const a  = stage === 1 ? easeOut(stageP) : 1;
        const bw = Math.round(W * 0.62);
        const bh = Math.round(H * 0.072);
        const bx = L.CX - bw / 2;
        const by = L.ROW_EMBED - bh / 2;

        ctx.save();
        ctx.globalAlpha *= a;

        // Pulse glow on the model name text when stage === 1
        if (stage === 1) {{
          const pulse = 0.5 + 0.5 * Math.sin(stageP * Math.PI * 4);
          ctx.shadowColor = getCSSVar('--bar-biz');
          ctx.shadowBlur  = 6 * pulse;
        }}

        // Model name — larger and ink colour so it reads clearly
        mono(ctx, 11);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('SentenceTransformer · all-MiniLM-L6-v2', L.CX, by + bh * 0.30);
        ctx.shadowBlur = 0;

        // Vector cells below model name
        const cells = 32;
        const cellW = Math.round(bw * 0.72 / cells);
        const cellH = Math.round(bh * 0.28);
        const cellsX = L.CX - (cells * (cellW + 1)) / 2;
        const cellsY = by + bh * 0.58;
        for (let i = 0; i < cells; i++) {{
          const v = Math.abs(Math.sin(i * 2.3 + articleIdx));
          ctx.fillStyle   = getCSSVar('--bar-biz');
          ctx.globalAlpha = cardAlpha * a * (0.2 + v * 0.6);
          ctx.fillRect(cellsX + i * (cellW + 1), cellsY, cellW, cellH);
        }}
        ctx.globalAlpha = cardAlpha * a;

        // "384-dim vector" label below cells — centred, readable
        mono(ctx, 9);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText('384-dim vector', L.CX, cellsY + cellH + 5);

        ctx.restore();
      }}

      // ── Connector: embedding → scores ───────────────────────────────
      if (stage >= 2) {{
        const p = stage === 2 ? easeOut(stageP * 0.4) : 1;
        drawConnector(ctx, L.CX, L.ROW_EMBED + Math.round(H*0.04), L.CX, L.ROW_SCORES - Math.round(H*0.03), p, getCSSVar('--rule-heavy'));
      }}

      // ── Stage 2+: Score bars ─────────────────────────────────────────
      if (stage >= 2) {{
        const a   = stage === 2 ? easeOut(stageP) : 1;
        const gap = Math.round(H * 0.048);
        const bh  = L.BAR_H;

        const bars = [
          {{ label: 'TECH',  value: ex.tech,  color: getCSSVar('--bar-tech')  }},
          {{ label: 'BIZ',   value: ex.biz,   color: getCSSVar('--bar-biz')   }},
          {{ label: 'NOISE', value: ex.noise, color: getCSSVar('--bar-noise') }},
        ];

        bars.forEach((b, i) => {{
          const animVal = stage === 2 ? b.value * easeOut(Math.max(0, stageP - i * 0.2)) : b.value;
          drawScoreBar(ctx,
            L.BAR_X, L.ROW_SCORES - bh/2 + i * (bh + gap),
            L.BAR_W, bh,
            animVal, b.color, b.label, a
          );
        }});
      }}

      // ── Connector: scores → gates ────────────────────────────────────
      if (stage >= 3) {{
        const p = stage === 3 ? easeOut(stageP * 0.5) : 1;
        drawConnector(ctx, L.CX, L.ROW_SCORES + Math.round(H*0.07), L.CX, L.ROW_GATES - Math.round(H*0.04), p, getCSSVar('--rule-heavy'));
      }}

      // ── Stage 3+: Gate 1 decision ────────────────────────────────────
      if (stage >= 3) {{
        const a         = stage === 3 ? easeOut(stageP) : 1;
        const gate1pass = ex.tech >= 0.22 || ex.biz >= 0.22;
        drawDecision(ctx, L.CX, L.ROW_GATES - Math.round(H*0.055),
          gate1pass, 1, 'Score ≥ 0.22 on Tech or Biz', a);
      }}

      // ── Stage 4+: Gate 2 decision ────────────────────────────────────
      if (stage >= 4) {{
        const a         = stage === 4 ? easeOut(stageP) : 1;
        const gate1pass = ex.tech >= 0.22 || ex.biz >= 0.22;
        const gate2pass = gate1pass && (Math.max(ex.tech, ex.biz) > ex.noise);
        drawDecision(ctx, L.CX, L.ROW_GATES + Math.round(H*0.03),
          gate2pass, 2, 'Winning score > Noise score', a);
      }}

      // ── Connector: gates → priority (only if passed) ─────────────────
      const gate1pass = ex.tech >= 0.22 || ex.biz >= 0.22;
      const gate2pass = gate1pass && (Math.max(ex.tech, ex.biz) > ex.noise);

      if (stage >= 5 && gate2pass) {{
        const p = stage === 5 ? easeOut(stageP * 0.5) : 1;
        drawConnector(ctx, L.CX, L.ROW_GATES + Math.round(H*0.06), L.CX, L.ROW_PRIORITY - Math.round(H*0.045), p, getCSSVar('--bar-tech'));
      }}

      // ── Stage 5+: Priority score (only if passed both gates) ─────────
      if (stage >= 5 && gate2pass) {{
        const a   = stage === 5 ? easeOut(stageP) : 1;
        const bw  = Math.round(W * 0.56);
        const bh  = Math.round(H * 0.082);
        const bx  = L.CX - bw / 2;
        const by  = L.ROW_PRIORITY - bh / 2;

        ctx.save();
        ctx.globalAlpha *= a;

        ctx.fillStyle   = getCSSVar('--bar-tech');
        ctx.globalAlpha *= 0.1;
        ctx.fillRect(bx, by, bw, bh);
        ctx.globalAlpha = a * cardAlpha;
        ctx.strokeStyle = getCSSVar('--bar-tech');
        ctx.lineWidth   = 1.5;
        ctx.strokeRect(bx, by, bw, bh);

        // "PRIORITY SCORE" label — centred at top of box, readable colour
        mono(ctx, 8);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'top';
        ctx.fillText('PRIORITY SCORE', L.CX, by + 6);

        // Full equation as one centred string — no offset, no gap
        const relevance  = Math.max(ex.tech, ex.biz).toFixed(4);
        const fullEq     = `${{relevance}} × ${{ex.weight}} (authority) = ${{ex.priority.toFixed(4)}}`;

        // Measure where the = sign ends so we can colour the value differently
        mono(ctx, 10);
        const eqLeft  = `${{relevance}} × ${{ex.weight}} (authority) = `;
        const leftW   = ctx.measureText(eqLeft).width;
        mono(ctx, 13);
        const valW    = ctx.measureText(ex.priority.toFixed(4)).width;
        const totalW  = leftW + valW;
        const startX  = L.CX - totalW / 2;

        mono(ctx, 10);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'left';
        ctx.textBaseline = 'middle';
        ctx.fillText(eqLeft, startX, by + bh * 0.65);

        mono(ctx, 13);
        ctx.fillStyle = getCSSVar('--bar-tech');
        ctx.fillText(ex.priority.toFixed(4), startX + leftW, by + bh * 0.65);

        ctx.restore();
      }}

      // ── If failed — show rejection label ─────────────────────────────
      if (stage >= 4 && !gate2pass) {{
        const a = stage === 4 ? easeOut(stageP) : 1;
        ctx.save();
        ctx.globalAlpha *= a * 0.6;
        mono(ctx, 8);
        ctx.fillStyle    = getCSSVar('--bar-noise');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('ARTICLE REJECTED — NOT ENTERED INTO CURATED POOL', L.CX, L.ROW_PRIORITY);
        ctx.restore();
      }}

      // ── Progress dots + pause icon ───────────────────────────────────
      const dotCount   = PIPELINE_EXAMPLES.length;
      const dotSpacing = 16;
      const dotY       = H - Math.round(H * 0.028);
      const dotsX      = L.CX - ((dotCount - 1) * dotSpacing) / 2;

      for (let i = 0; i < dotCount; i++) {{
        ctx.beginPath();
        ctx.arc(dotsX + i * dotSpacing, dotY, 3, 0, Math.PI * 2);
        ctx.fillStyle   = getCSSVar(i === articleIdx ? '--ink-light' : '--rule');
        ctx.globalAlpha = 1;
        ctx.fill();
      }}

      // Pause/play icon — drawn to the right of the dots
      const iconX  = dotsX + (dotCount - 1) * dotSpacing + 20;
      const iconY  = dotY;
      const iconR  = 9;
      const iconCol = getCSSVar(paused ? '--accent' : '--ink-faint');

      // Circle
      ctx.beginPath();
      ctx.arc(iconX, iconY, iconR, 0, Math.PI * 2);
      ctx.strokeStyle = iconCol;
      ctx.lineWidth   = 1;
      ctx.globalAlpha = 0.7;
      ctx.stroke();
      ctx.globalAlpha = 1;

      ctx.fillStyle = iconCol;
      if (paused) {{
        // Play triangle
        ctx.beginPath();
        ctx.moveTo(iconX - 2.5, iconY - 4);
        ctx.lineTo(iconX + 5,   iconY);
        ctx.lineTo(iconX - 2.5, iconY + 4);
        ctx.closePath();
        ctx.fill();
      }} else {{
        // Pause bars
        const bw = 2.5, bh = 7, gap = 2;
        ctx.fillRect(iconX - gap - bw, iconY - bh/2, bw, bh);
        ctx.fillRect(iconX + gap,      iconY - bh/2, bw, bh);
      }}

      ctx.restore();

      animId = requestAnimationFrame(draw);
    }}

    function start() {{
      if (animId) cancelAnimationFrame(animId);
      stage = 0; stageStart = 0; articleIdx = 0;
      setup();
      animId = requestAnimationFrame(draw);
    }}

    window.addEventListener('resize', () => {{
      if (animId) cancelAnimationFrame(animId);
      clearTimeout(canvas._resizeTimer);
      canvas._resizeTimer = setTimeout(start, 120);
    }});

    start();
  }})();

  // ── Init ─────────────────────────────────────────────────────────────────
  // ── Analyst Agent Animation ─────────────────────────────────────────────
  (function() {{
    const canvas = document.getElementById('analyst-canvas');
    if (!canvas) return;

    const DPR = window.devicePixelRatio || 1;
    let W, H, animId;

    // ── Phases ────────────────────────────────────────────────────────────
    // 0: idle/intro        800ms   article title fades in
    // 1: fetch-scan       2400ms   scan line sweeps, text lines appear, word count ticks
    // 2: fetch-hold        600ms   full doc visible
    // 3: gemini-feed      1800ms   text lines flow into gemini block
    // 4: gemini-think     1000ms   model block pulses
    // 5: summary-type     2200ms   summary types out word by word
    // 6: hold             1400ms   full card visible
    // 7: fade              500ms   fade out, loop
    const PHASE_DUR = [800, 2400, 600, 1800, 1000, 2200, 1400, 500];
    const TOTAL_PHASES = PHASE_DUR.length;

    let phase      = 0;
    let phaseStart = 0;

    function easeOut(t)   {{ return 1 - Math.pow(1 - t, 3); }}
    function easeInOut(t) {{ return t < 0.5 ? 2*t*t : 1-Math.pow(-2*t+2,2)/2; }}
    function lerp(a, b, t) {{ return a + (b-a) * t; }}

    function mono(ctx, size) {{
      ctx.font = `500 ${{Math.round(size * Math.min(W/700,1))}}px 'IBM Plex Mono', monospace`;
    }}
    function serif(ctx, size, weight) {{
      ctx.font = `${{weight||400}} ${{Math.round(size * Math.min(W/700,1))}}px 'Source Serif 4', serif`;
    }}

    // ── Article data — top ranked from today's run ───────────────────────
    const ARTICLE_TITLE = '{analyst_title}';
    const ARTICLE_URL   = '{analyst_domain}';
    const SUMMARY_TEXT  = '{analyst_summary}';
    const WORD_COUNT    = {analyst_words};
    const LINE_COUNT    = 28;

    function setup() {{
      W = canvas.offsetWidth || 700;
      H = Math.round(W * 0.72);
      canvas.width  = W * DPR;
      canvas.height = H * DPR;
      canvas.style.height = H + 'px';
    }}

    function draw(ts) {{
      const ctx = canvas.getContext('2d');
      ctx.setTransform(DPR, 0, 0, DPR, 0, 0);

      if (!phaseStart) phaseStart = ts;
      const elapsed = ts - phaseStart;
      const p  = Math.min(elapsed / PHASE_DUR[phase], 1);
      const ep = easeOut(p);

      if (elapsed >= PHASE_DUR[phase]) {{
        phaseStart = ts;
        phase = (phase + 1) % TOTAL_PHASES;
        if (phase === 0) setup();
      }}

      // ── Background ───────────────────────────────────────────────────
      ctx.fillStyle = getCSSVar('--paper-warm');
      ctx.fillRect(0, 0, W, H);

      const CX      = W / 2;
      const cardPad = Math.round(W * 0.06);
      const cardW   = W - cardPad * 2;
      const docTop  = Math.round(H * 0.22);
      const docH    = Math.round(H * 0.52);
      const docX    = cardPad;

      // Global fade for phase 7
      const globalA = phase === 7 ? Math.max(0, 1 - p / 0.6) : 1;
      ctx.save();
      ctx.globalAlpha = globalA;

      // ── Article title (phases 0+) ─────────────────────────────────
      if (phase >= 0) {{
        const a = phase === 0 ? easeOut(p) : 1;
        ctx.save();
        ctx.globalAlpha *= a;
        serif(ctx, 13, 700);
        ctx.fillStyle    = getCSSVar('--ink');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        // Simple single-line truncation
        const maxTitleW = cardW * 0.9;
        let title = ARTICLE_TITLE;
        mono(ctx, 13);
        ctx.font = `700 ${{Math.round(13 * Math.min(W/700,1))}}px 'Source Serif 4', serif`;
        while (ctx.measureText(title).width > maxTitleW && title.length > 20) {{
          title = title.slice(0, -4) + '...';
        }}
        ctx.fillText(title, CX, Math.round(H * 0.10));

        mono(ctx, 8);
        ctx.fillStyle = getCSSVar('--ink-faint');
        ctx.fillText(ARTICLE_URL, CX, Math.round(H * 0.16));
        ctx.restore();
      }}

      // ── Document frame ────────────────────────────────────────────
      if (phase >= 1) {{
        const a = phase === 1 ? easeOut(p) : 1;
        ctx.save();
        ctx.globalAlpha *= a * 0.6;
        ctx.strokeStyle = getCSSVar('--rule');
        ctx.lineWidth   = 1;
        ctx.strokeRect(docX, docTop, cardW, docH);
        ctx.restore();
      }}

      // ── Phase 1: Scan line + text lines appearing ─────────────────
      if (phase >= 1 && phase <= 2) {{
        const scanProgress = phase === 1 ? ep : 1;
        const scanY = docTop + docH * scanProgress;

        // Text lines appearing behind scan
        const lineH    = Math.round(docH / (LINE_COUNT + 2));
        const lineMaxW = cardW * 0.82;
        const lineX    = docX + cardW * 0.06;
        const linesVisible = Math.floor(scanProgress * LINE_COUNT);

        for (let i = 0; i < linesVisible; i++) {{
          const ly     = docTop + lineH * (i + 1);
          // Vary line widths for realism
          const seed   = (i * 7919) % 100;
          const lw     = lineMaxW * (0.55 + (seed / 100) * 0.45);
          const lastLine = i === linesVisible - 1;
          ctx.fillStyle   = getCSSVar('--rule');
          ctx.globalAlpha = globalA * (lastLine ? 0.4 : 0.7);
          ctx.fillRect(lineX, ly, lastLine ? lw * 0.4 : lw, Math.max(2, lineH - 3));
        }}

        // Scan line
        if (phase === 1) {{
          ctx.strokeStyle = getCSSVar('--bar-biz');
          ctx.lineWidth   = 1.5;
          ctx.globalAlpha = globalA * 0.7;
          ctx.beginPath();
          ctx.moveTo(docX + 2, scanY);
          ctx.lineTo(docX + cardW - 2, scanY);
          ctx.stroke();

          // TRAFILATURA label riding the scan line
          mono(ctx, 8);
          ctx.fillStyle    = getCSSVar('--bar-biz');
          ctx.textAlign    = 'right';
          ctx.textBaseline = 'bottom';
          ctx.globalAlpha  = globalA * 0.9;
          ctx.fillText('TRAFILATURA · FETCHING', docX + cardW - 6, scanY - 3);
        }}

        // Word count ticking up
        const wordsExtracted = Math.round(scanProgress * WORD_COUNT);
        mono(ctx, 9);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'right';
        ctx.textBaseline = 'bottom';
        ctx.globalAlpha  = globalA;
        ctx.fillText(`${{wordsExtracted.toLocaleString()}} words extracted`, docX + cardW - 6, docTop + docH + 16);
      }}

      // ── Phase 3: Text lines flow into Gemini block ────────────────
      if (phase === 3) {{
        const gemW  = Math.round(W * 0.38);
        const gemH  = Math.round(H * 0.10);
        const gemX  = CX - gemW / 2;
        const gemY  = docTop + (docH - gemH) / 2;

        // Remaining text lines shrink toward gemini block
        const lineH    = Math.round(docH / (LINE_COUNT + 2));
        const lineMaxW = cardW * 0.82;
        const lineX    = docX + cardW * 0.06;

        for (let i = 0; i < LINE_COUNT; i++) {{
          const ly0   = docTop + lineH * (i + 1);
          const ly    = lerp(ly0, gemY + gemH / 2, ep);
          const seed  = (i * 7919) % 100;
          const lw0   = lineMaxW * (0.55 + (seed / 100) * 0.45);
          const lw    = lw0 * (1 - ep * 0.85);
          const lx    = lerp(lineX, CX - lw / 2, ep);
          ctx.fillStyle   = getCSSVar('--rule');
          ctx.globalAlpha = globalA * (1 - ep * 0.8);
          ctx.fillRect(lx, ly, lw, Math.max(1, lineH - 3));
        }}

        // Gemini block fades in
        ctx.save();
        ctx.globalAlpha = globalA * ep;
        ctx.fillStyle   = getCSSVar('--bar-biz');
        ctx.globalAlpha *= 0.1;
        ctx.fillRect(gemX, gemY, gemW, gemH);
        ctx.globalAlpha = globalA * ep;
        ctx.strokeStyle = getCSSVar('--bar-biz');
        ctx.lineWidth   = 1.5;
        ctx.strokeRect(gemX, gemY, gemW, gemH);

        mono(ctx, 9);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('gemma-3-12b-it', CX, gemY + gemH / 2);
        ctx.restore();
      }}

      // ── Phase 4: Gemini block pulses ──────────────────────────────
      if (phase === 4) {{
        const gemW  = Math.round(W * 0.38);
        const gemH  = Math.round(H * 0.10);
        const gemX  = CX - gemW / 2;
        const gemY  = docTop + (docH - gemH) / 2;
        const pulse = 0.5 + 0.5 * Math.sin(p * Math.PI * 5);

        ctx.save();
        ctx.shadowColor = getCSSVar('--bar-biz');
        ctx.shadowBlur  = 10 * pulse;
        ctx.fillStyle   = getCSSVar('--bar-biz');
        ctx.globalAlpha = globalA * 0.12;
        ctx.fillRect(gemX, gemY, gemW, gemH);
        ctx.globalAlpha = globalA;
        ctx.strokeStyle = getCSSVar('--bar-biz');
        ctx.lineWidth   = 1.5;
        ctx.strokeRect(gemX, gemY, gemW, gemH);
        ctx.shadowBlur  = 0;

        mono(ctx, 9);
        ctx.fillStyle    = getCSSVar('--ink-light');
        ctx.textAlign    = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('gemma-3-12b-it', CX, gemY + gemH * 0.35);

        mono(ctx, 7);
        ctx.fillStyle    = getCSSVar('--bar-biz');
        ctx.globalAlpha  = globalA * (0.4 + pulse * 0.6);
        ctx.fillText('SYNTHESISING ···', CX, gemY + gemH * 0.68);
        ctx.restore();
      }}

      // ── Phase 5: Summary types out ────────────────────────────────
      if (phase >= 5) {{
        const words       = SUMMARY_TEXT.split(' ');
        const wordsShown  = phase === 5
          ? Math.floor(ep * words.length)
          : words.length;
        const visibleText = words.slice(0, wordsShown).join(' ');

        // Summary text area
        const summaryX   = docX + cardW * 0.06;
        const summaryW   = cardW * 0.88;
        const summaryTop = docTop + Math.round(docH * 0.1);
        const lineHeight = Math.round(H * 0.048);
        const maxLines   = 5;

        ctx.save();
        ctx.globalAlpha *= phase === 5 ? easeOut(p) : 1;

        // Wrap text manually
        serif(ctx, 12, 300);
        ctx.fillStyle    = getCSSVar('--ink-mid');
        ctx.textAlign    = 'left';
        ctx.textBaseline = 'top';
        ctx.font = `300 italic ${{Math.round(12 * Math.min(W/700,1))}}px 'Source Serif 4', serif`;

        const wds = visibleText.split(' ');
        let lines = [], cur = '';
        for (const w of wds) {{
          const test = cur ? cur + ' ' + w : w;
          if (ctx.measureText(test).width > summaryW && cur) {{
            lines.push(cur); cur = w;
            if (lines.length >= maxLines) break;
          }} else {{ cur = test; }}
        }}
        if (lines.length < maxLines && cur) lines.push(cur);

        lines.forEach((line, i) => {{
          ctx.fillText(line, summaryX, summaryTop + i * lineHeight);
        }});

        // Gemini model attribution
        mono(ctx, 8);
        ctx.fillStyle    = getCSSVar('--ink-faint');
        ctx.textAlign    = 'right';
        ctx.textBaseline = 'bottom';
        ctx.fillText('gemma-3-12b-it · grounded synthesis', docX + cardW - 6, docTop + docH - 6);

        ctx.restore();
      }}

      ctx.restore(); // global alpha
      animId = requestAnimationFrame(draw);
    }}

    function start() {{
      if (animId) cancelAnimationFrame(animId);
      phase = 0; phaseStart = 0;
      setup();
      animId = requestAnimationFrame(draw);
    }}

    window.addEventListener('resize', () => {{
      if (animId) cancelAnimationFrame(animId);
      clearTimeout(canvas._resizeTimer);
      canvas._resizeTimer = setTimeout(start, 120);
    }});

    start();
  }})();

  // ── Init ─────────────────────────────────────────────────────────────────
  window.addEventListener('DOMContentLoaded', () => {{
    renderSourceChart();
    renderCards();
  }});
  </script>

</body>
</html>"""

        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html)
            return filename
        except Exception as e:
            print(f"[ERROR] Failed to generate insights report: {e}")
            return None