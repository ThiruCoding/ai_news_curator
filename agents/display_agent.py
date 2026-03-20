import datetime
import os
from urllib.parse import urlparse

class DisplayAgent:
    def __init__(self, target_folder="newsreports"):
        self.target_folder = target_folder

    def _get_domain(self, url):
        """Extracts the root domain for a cleaner modern look."""
        try:
            domain = urlparse(url).netloc
            return domain.replace('www.', '')
        except:
            return "source link"

    def generate_html_report(self, articles):
        now = datetime.datetime.now()
        date_str = now.strftime("%d %B %Y").upper() # Expanded for the new header style
        filename = f"AI_News_{now.strftime('%d%b%Y').upper()}.html"
        
        if not os.path.exists(self.target_folder):
            os.makedirs(self.target_folder)
            
        full_path = os.path.join(self.target_folder, filename)
        timestamp = now.strftime("%H:%M %p")

        # 1. Full 2026 Design System with Light/Dark Variables
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en" data-theme="dark">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>AI NEWS OF THE DAY - {date_str}</title>
            <style>
                :root[data-theme="dark"] {{
                    --bg: #0b0f1a;
                    --surface: #161b2c;
                    --accent: #38bdf8;
                    --text-p: #f1f5f9;
                    --text-s: #94a3b8;
                    --border: rgba(255, 255, 255, 0.08);
                    --toggle-bg: rgba(255, 255, 255, 0.05);
                }}

                :root[data-theme="light"] {{
                    --bg: #f8fafc;
                    --surface: #ffffff;
                    --accent: #0284c7;
                    --text-p: #0f172a;
                    --text-s: #475569;
                    --border: rgba(15, 23, 42, 0.08);
                    --toggle-bg: rgba(15, 23, 42, 0.05);
                }}

                * {{ box-sizing: border-box; transition: background-color 0.4s ease, color 0.4s ease; }}

                body {{ 
                    font-family: 'Inter', system-ui, -apple-system, sans-serif; 
                    background-color: var(--bg); 
                    color: var(--text-p); 
                    margin: 0; 
                    padding: 4rem 1.25rem;
                    display: flex;
                    justify-content: center;
                    -webkit-font-smoothing: antialiased;
                }}

                .container {{ width: 100%; max-width: 650px; position: relative; }}

                /* Theme Toggle Pill */
                .theme-toggle {{
                    position: fixed;
                    top: 1.5rem;
                    right: 1.5rem;
                    background: var(--toggle-bg);
                    backdrop-filter: blur(12px);
                    -webkit-backdrop-filter: blur(12px);
                    border: 1px solid var(--border);
                    padding: 0.4rem;
                    border-radius: 2rem;
                    cursor: pointer;
                    display: flex;
                    gap: 0.2rem;
                    z-index: 100;
                }}

                .theme-btn {{
                    border: none;
                    background: none;
                    font-size: 0.65rem;
                    font-weight: 800;
                    color: var(--text-s);
                    padding: 0.5rem 0.9rem;
                    border-radius: 1.5rem;
                    cursor: pointer;
                    text-transform: uppercase;
                    letter-spacing: 0.05rem;
                }}

                .active-theme {{ background: var(--accent); color: white !important; }}

                /* Updated Header Hierarchy */
                header {{ margin-bottom: 4rem; text-align: left; }}
                
                .kicker {{ 
                    font-size: 0.75rem; 
                    font-weight: 800; 
                    letter-spacing: 0.2rem; 
                    color: var(--accent); 
                    text-transform: uppercase; 
                    margin-bottom: 0.6rem;
                }}

                .date-title {{ 
                    font-size: 2.2rem; 
                    font-weight: 800; 
                    margin: 0; 
                    letter-spacing: -0.03em;
                    line-height: 1;
                }}

                .meta-info {{ 
                    color: var(--text-s); 
                    font-size: 0.7rem; 
                    font-family: ui-monospace, monospace; 
                    margin-top: 0.8rem;
                }}

                /* Minimalist Accordion */
                .accordion-item {{ border-bottom: 1px solid var(--border); }}

                .headline-btn {{
                    width: 100%;
                    padding: 1.5rem 0;
                    background: none;
                    border: none;
                    text-align: left;
                    font-size: 1.05rem;
                    font-weight: 500;
                    line-height: 1.4;
                    color: var(--text-p);
                    cursor: pointer;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    outline: none;
                }}

                .headline-btn span {{ padding-right: 1.5rem; }}
                .headline-btn:hover {{ color: var(--accent); }}

                .chevron {{ 
                    width: 18px; 
                    height: 18px; 
                    stroke: var(--text-s); 
                    stroke-width: 2.5; 
                    fill: none; 
                    flex-shrink: 0;
                    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1); 
                }}

                .active .chevron {{ transform: rotate(180deg); stroke: var(--accent); }}

                .content {{ 
                    max-height: 0; 
                    overflow: hidden; 
                    transition: max-height 0.4s cubic-bezier(0.4, 0, 0.2, 1); 
                }}

                .summary-text {{ 
                    color: var(--text-s); 
                    font-size: 0.95rem; 
                    line-height: 1.8; 
                    margin: 0 0 1.5rem 0; 
                }}

                .source-link {{
                    font-size: 0.75rem;
                    color: var(--accent);
                    text-decoration: none;
                    font-weight: 700;
                    text-transform: lowercase;
                    display: inline-flex;
                    align-items: center;
                }}

                .source-link::before {{ content: '→'; margin-right: 0.5rem; }}
                .source-link:hover {{ text-decoration: underline; }}

                footer {{ 
                    margin-top: 8rem; 
                    padding-top: 2rem; 
                    border-top: 1px solid var(--border); 
                    color: var(--text-s); 
                    font-size: 0.65rem; 
                    letter-spacing: 0.15rem; 
                    text-transform: uppercase; 
                }}

                /* Mobile Adjustments */
                @media (max-width: 600px) {{
                    .date-title {{ font-size: 1.8rem; }}
                    body {{ padding-top: 6rem; }}
                }}
            </style>
        </head>
        <body>
            <div class="theme-toggle" id="theme-switcher">
                <button class="theme-btn" data-mode="light">Light</button>
                <button class="theme-btn active-theme" data-mode="dark">Dark</button>
            </div>

            <div class="container">
                <header>
                    <div class="kicker">AI NEWS OF THE DAY</div>
                    <h1 class="date-title">{date_str}</h1>
                    <div class="meta-info">SYNTHESIZED AT {timestamp}</div>
                </header>

                <div id="accordion-group">
        """

        # 2. Dynamic Content Injection
        for art in articles:
            domain = self._get_domain(art['link'])
            html_template += f"""
                <div class="accordion-item">
                    <button class="headline-btn">
                        <span>{art['title']}</span>
                        <svg class="chevron" viewBox="0 0 24 24"><path d="M6 9l6 6 6-6" /></svg>
                    </button>
                    <div class="content">
                        <div style="padding-bottom: 2.5rem;">
                            <p class="summary-text">{art['summary']}</p>
                            <a href="{art['link']}" class="source-link" target="_blank">{domain}</a>
                        </div>
                    </div>
                </div>
            """

        # 3. Responsive Scripts
        html_template += """
                </div>
                <footer>Prepared by Agentic AI services</footer>
            </div>

            <script>
                // Exclusive Accordion Interaction
                document.querySelectorAll('.headline-btn').forEach(btn => {
                    btn.addEventListener('click', () => {
                        const content = btn.nextElementSibling;
                        const parent = btn.parentElement;
                        const isOpen = content.style.maxHeight;

                        document.querySelectorAll('.content').forEach(c => {
                            c.style.maxHeight = null;
                            c.parentElement.classList.remove('active');
                        });

                        if (!isOpen) {
                            content.style.maxHeight = content.scrollHeight + "px";
                            parent.classList.add('active');
                        }
                    });
                });

                // Smart Theme Management
                const themeBtns = document.querySelectorAll('.theme-btn');
                const root = document.documentElement;

                const savedTheme = localStorage.getItem('ai-news-pref') || 'dark';
                applyTheme(savedTheme);

                themeBtns.forEach(btn => {
                    btn.addEventListener('click', () => {
                        const mode = btn.getAttribute('data-mode');
                        applyTheme(mode);
                    });
                });

                function applyTheme(mode) {
                    root.setAttribute('data-theme', mode);
                    localStorage.setItem('ai-news-pref', mode);
                    themeBtns.forEach(b => {
                        b.classList.toggle('active-theme', b.getAttribute('data-mode') === mode);
                    });
                }
            </script>
        </body>
        </html>
        """

        # 4. Final I/O and Return
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(html_template)
            return filename 
        except Exception as e:
            print(f"[ERROR] Failed to generate report: {e}")
            return None