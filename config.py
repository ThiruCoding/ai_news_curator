# Centralized Configuration for AI News Curator

# RSS Feed Registry
RSS_FEEDS = {
    # Journalism & Industry Analysis
    "NYT_TECH": "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml",
    "WIRED_SCIENCE": "https://www.wired.com/feed/category/science/latest/rss",
    "ARS_TECHNICA": "https://feeds.arstechnica.com/arstechnica/index",
    "TECHCRUNCH_AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    #"THE_VERGE_AI": "https://www.theverge.com/ai-artificial-intelligence/rss/index.xml",
    #"IEEE_SPECTRUM_AI": "https://spectrum.ieee.org/rss/robotics/artificial-intelligence/fulltext",
    "VENTUREBEAT_AI": "https://venturebeat.com/category/ai/feed/",
    "ZDNET_AI": "https://www.zdnet.com/topic/artificial-intelligence/rss.xml",
    #"COMPUTER_WEEKLY_AI": "https://www.computerweekly.com/rss/Schooled-in-AI-Podcast-Feed.xml",
    
    # Pure Research & Foundational Science (High Signal-to-Noise)
    #"ARXIV_AI_RESEARCH": "https://export.arxiv.org/rss/cs.AI",
    #"ARXIV_MACHINE_LEARNING": "https://export.arxiv.org/rss/cs.LG",
    #"NATURE_MACHINE_INTEL": "https://www.nature.com/natmachintell.rss",
    #"MIT_AI_NEWS": "https://news.mit.edu/topic/mitartificial-intelligence-rss-feed",
    #"SCIENCE_DAILY_AI": "https://www.sciencedaily.com/rss/computers_math/artificial_intelligence.xml",
    #"OPENAI_BLOG": "https://openai.com/news/rss.xml",
    #"GOOGLE_RESEARCH_BLOG": "https://research.google/blog/rss/",
    #"DEEPMIND_BLOG": "https://deepmind.google/blog/rss.xml",
    
    # Engineering & Developer Platforms
    "HACKER_NEWS": "https://news.ycombinator.com/rss",
    "INFOQ_AI_ML": "https://feed.infoq.com/ai-ml-data-eng/news/",
    "THE_STACK": "https://thestack.technology/rss/",
    "MARKTECHPOST": "https://www.marktechpost.com/feed/",
    "MACHINE_LEARNING_MASTERY": "https://machinelearningmastery.com/feed/",
    
    # Financial & Macro Tech Context
    #"WSJ_TECH": "https://feeds.a.dj.com/rss/RSSWSJTechnology.xml",
    #"SEMICONDUCTOR_DIGEST": "https://www.semiconductor-digest.com/feed/",
    "MARKETWATCH_TECH": "https://www.marketwatch.com/rss/topstories"
}

SOURCE_WEIGHTS = {
    # --- LEVEL 1: PRIMARY RESEARCH & HARDWARE INFRASTRUCTURE (Tier S: 1.6) ---
    "ARXIV_AI_RESEARCH": 1.6,
    "ARXIV_MACHINE_LEARNING": 1.6,
    "SEMICONDUCTOR_DIGEST": 1.6,
    "NATURE_MACHINE_INTEL": 1.6,
    "OPENAI_BLOG": 1.6,
    "DEEPMIND_BLOG": 1.6,
    "GOOGLE_RESEARCH_BLOG": 1.6,

    # --- LEVEL 2: ENGINEERING AGGREGATORS & DEEP TECH (Tier A: 1.4) ---
    "HACKER_NEWS": 1.4,
    "INFOQ_AI_ML": 1.4,
    "MIT_AI_NEWS": 1.4,
    "MARKTECHPOST": 1.4,
    "IEEE_SPECTRUM_AI": 1.4,
    "ARS_TECHNICA": 1.4,
    "MACHINE_LEARNING_MASTERY": 1.4,

    # --- LEVEL 3: SPECIALIZED INDUSTRY & STARTUP NEWS (Tier B: 1.2) ---
    "TECHCRUNCH_AI": 1.2,
    "VENTUREBEAT_AI": 1.2,
    "THE_STACK": 1.2,
    "WIRED_SCIENCE": 1.2,
    "SCIENCE_DAILY_AI": 1.2,

    # --- LEVEL 4: GENERAL TECH & MACRO CONTEXT (Tier C: 1.0) ---
    "NYT_TECH": 1.0,
    "WSJ_TECH": 1.0,
    "ZDNET_AI": 1.0,
    "MARKETWATCH_TECH": 1.0,
    "THE_VERGE_AI": 1.0,
    "COMPUTER_WEEKLY_AI": 1.0,
    
    "DEFAULT": 1.0
}

# Agent Settings

# High-Density Positive Gold Standard
USER_INTEREST = (
    "New AI model architectures, significant research breakthroughs, "
    "GPU/infrastructure hardware developments, foundational model updates, "
    "and large-scale industry implementations of machine learning."
)

# Your Specified Negative Gold Standard
NEGATIVE_FILTER = (
    "Generic corporate PR, marketing-heavy announcements, AI-washing, "
    "chatbot integration into old products, beginner tutorials, how-to guides, "
    "prompt engineering tips, listicles like Top 10 AI tools, daily stock "
    "market price movements, seed funding under $10M, and speculative "
    "philosophical op-eds without current real-world events."
)

# DECAY_SETTINGS: Controls how quickly "freshness" score drops.
# Uses a half-life formula: Score drops by 50% every 24 hours.
HALFLIFE_HOURS = 24
WEIGHT_RELEVANCE = 0.7  # 70% weight on semantic match
WEIGHT_AUTHORITY = 0.2  # 20% weight on source reputation
WEIGHT_FRESHNESS = 0.1  # 10% weight on recency

DEFAULT_THRESHOLD = 0.35

# Model Settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# config.py
GEMINI_API_KEY = "REDACTED"