"""
Mock pipeline data for DEV_MODE.
Bypasses all RSS fetching, embedding, and Gemini API calls.
Swap config.DEV_MODE = False to restore full pipeline.
"""

import config

def get_mock_pipeline_data():
    """Returns a realistic pipeline_data dict for display agent testing."""

    feed_stats = {name: {'fetched': 0, 'curated': 0} for name in config.RSS_FEEDS.keys()}

    # Simulate realistic per-source fetch counts
    active_sources = [
        ('TECHCRUNCH_AI',   42, 8),
        ('VENTUREBEAT_AI',  38, 6),
        ('THE_VERGE_AI',    55, 4),
        ('HACKER_NEWS',     90, 11),
        ('ARS_TECHNICA',    30, 7),
        ('THE_DECODER',     18, 9),
        ('GUARDIAN_AI',     22, 3),
        ('WIRED_SCIENCE',   25, 4),
        ('ZDNET_AI',        33, 2),
        ('AXIOS_AI',        48, 5),
        ('SEMAFOR_TECH',    19, 3),
        ('404_MEDIA',       14, 4),
        ('MARKTECHPOST',    27, 6),
        ('INFOQ_AI_ML',     20, 5),
        ('SCMP_TECH',       16, 2),
    ]
    for name, fetched, curated in active_sources:
        if name in feed_stats:
            feed_stats[name]['fetched'] = fetched
            feed_stats[name]['curated'] = curated

    # Full curated pool — mix of tech and business signals, varying scores
    all_curated = [
        {
            'title':           'Anthropic releases Claude 4 with extended thinking and 200K context window',
            'source':          'TECHCRUNCH_AI',
            'link':            'https://techcrunch.com/mock/claude-4',
            'summary':         '',
            'relevance_score': 0.512,
            'noise_score':     0.141,
            'priority_score':  0.6144,
        },
        {
            'title':           'Google DeepMind publishes Gemini Ultra benchmark results surpassing GPT-4o on MMLU',
            'source':          'THE_DECODER',
            'link':            'https://the-decoder.com/mock/gemini-ultra',
            'summary':         '',
            'relevance_score': 0.487,
            'noise_score':     0.132,
            'priority_score':  0.6818,
        },
        {
            'title':           'OpenAI closes $6.5B funding round at $157B valuation led by Thrive Capital',
            'source':          'AXIOS_AI',
            'link':            'https://axios.com/mock/openai-funding',
            'summary':         '',
            'relevance_score': 0.461,
            'noise_score':     0.178,
            'priority_score':  0.5532,
        },
        {
            'title':           'NVIDIA announces Blackwell Ultra GPU architecture with 1.4TB/s memory bandwidth',
            'source':          'ARS_TECHNICA',
            'link':            'https://arstechnica.com/mock/blackwell-ultra',
            'summary':         '',
            'relevance_score': 0.534,
            'noise_score':     0.119,
            'priority_score':  0.7476,
        },
        {
            'title':           'Meta open-sources Llama 3.2 with multimodal capabilities and 128K context',
            'source':          'VENTUREBEAT_AI',
            'link':            'https://venturebeat.com/mock/llama-32',
            'summary':         '',
            'relevance_score': 0.498,
            'noise_score':     0.145,
            'priority_score':  0.5976,
        },
        {
            'title':           'EU AI Act enforcement begins: first compliance deadlines hit foundation model providers',
            'source':          'GUARDIAN_AI',
            'link':            'https://theguardian.com/mock/eu-ai-act',
            'summary':         '',
            'relevance_score': 0.443,
            'noise_score':     0.162,
            'priority_score':  0.5316,
        },
        {
            'title':           'Microsoft acquires Inflection AI talent in $650M licensing deal',
            'source':          'SEMAFOR_TECH',
            'link':            'https://semafor.com/mock/inflection',
            'summary':         '',
            'relevance_score': 0.429,
            'noise_score':     0.187,
            'priority_score':  0.5148,
        },
        {
            'title':           'Show HN: I built a distributed inference engine for running 70B models on consumer hardware',
            'source':          'HACKER_NEWS',
            'link':            'https://news.ycombinator.com/mock/inference-engine',
            'summary':         '',
            'relevance_score': 0.476,
            'noise_score':     0.134,
            'priority_score':  0.6664,
        },
        {
            'title':           'Mistral AI launches Le Chat Enterprise with on-premise deployment and GDPR compliance',
            'source':          'TECHCRUNCH_AI',
            'link':            'https://techcrunch.com/mock/mistral-enterprise',
            'summary':         '',
            'relevance_score': 0.412,
            'noise_score':     0.198,
            'priority_score':  0.4944,
        },
        {
            'title':           'xAI raises $6B Series B to accelerate Grok development and Memphis data centre',
            'source':          'VENTUREBEAT_AI',
            'link':            'https://venturebeat.com/mock/xai-series-b',
            'summary':         '',
            'relevance_score': 0.438,
            'noise_score':     0.171,
            'priority_score':  0.5256,
        },
        {
            'title':           'DeepSeek R2 technical report reveals MoE architecture with 671B total parameters',
            'source':          'THE_DECODER',
            'link':            'https://the-decoder.com/mock/deepseek-r2',
            'summary':         '',
            'relevance_score': 0.521,
            'noise_score':     0.128,
            'priority_score':  0.7294,
        },
        {
            'title':           'FTC opens investigation into AI chip market concentration and NVIDIA pricing',
            'source':          'GUARDIAN_AI',
            'link':            'https://theguardian.com/mock/ftc-nvidia',
            'summary':         '',
            'relevance_score': 0.407,
            'noise_score':     0.193,
            'priority_score':  0.4884,
        },
        {
            'title':           'Cohere releases Command R+ with 128K context targeting enterprise RAG pipelines',
            'source':          'MARKTECHPOST',
            'link':            'https://marktechpost.com/mock/cohere-command',
            'summary':         '',
            'relevance_score': 0.389,
            'noise_score':     0.201,
            'priority_score':  0.4668,
        },
        {
            'title':           'Apple M4 Ultra neural engine benchmarks show 38 TOPS for on-device LLM inference',
            'source':          'ARS_TECHNICA',
            'link':            'https://arstechnica.com/mock/m4-ultra',
            'summary':         '',
            'relevance_score': 0.463,
            'noise_score':     0.147,
            'priority_score':  0.6482,
        },
        {
            'title':           'Stability AI files for bankruptcy protection amid leadership turmoil and revenue shortfall',
            'source':          '404_MEDIA',
            'link':            'https://404media.co/mock/stability-bankruptcy',
            'summary':         '',
            'relevance_score': 0.418,
            'noise_score':     0.183,
            'priority_score':  0.5016,
        },
    ]

    # Top 10 — highest priority_score articles
    top_10 = sorted(all_curated, key=lambda a: a['priority_score'], reverse=True)[:10]

    # Rejected articles — didn't pass both gates (noise >= winning score)
    all_rejected = [
        {
            'title':           '10 best AI writing tools to boost your productivity in 2025',
            'source':          'ZDNET_AI',
            'link':            'https://zdnet.com/mock/ai-writing-tools',
            'summary':         '',
            'relevance_score': 0.298,
            'noise_score':     0.341,
            'priority_score':  0.0,
        },
        {
            'title':           'How to write better prompts for ChatGPT: a beginner\'s guide',
            'source':          'ZDNET_AI',
            'link':            'https://zdnet.com/mock/prompt-guide',
            'summary':         '',
            'relevance_score': 0.271,
            'noise_score':     0.389,
            'priority_score':  0.0,
        },
        {
            'title':           'AI stocks to watch this week as markets react to Fed rate decision',
            'source':          'AXIOS_AI',
            'link':            'https://axios.com/mock/ai-stocks',
            'summary':         '',
            'relevance_score': 0.242,
            'noise_score':     0.318,
            'priority_score':  0.0,
        },
        {
            'title':           'Top 15 AI tools for small businesses in 2025',
            'source':          'MARKTECHPOST',
            'link':            'https://marktechpost.com/mock/ai-tools-smb',
            'summary':         '',
            'relevance_score': 0.261,
            'noise_score':     0.402,
            'priority_score':  0.0,
        },
    ]

    # Mock final reports — give the top article a real summary for the analyst animation
    final_reports = [
        {
            'title':          a['title'],
            'source':         a['source'],
            'link':           a['link'],
            'summary':        (
                'The Blackwell Ultra architecture from NVIDIA marks a significant leap in '
                'memory bandwidth, targeting large-scale AI training workloads. The new GPU '
                'delivers 1.4 TB/s of memory bandwidth alongside a substantially enlarged '
                'context window for inference tasks. Industry analysts expect the release to '
                'accelerate adoption of next-generation foundation models among hyperscale '
                'cloud providers, with initial availability slated for Q3 2025.'
            ) if i == 0 else f"[DEV MODE] Mock summary for: {a['title'][:60]}...",
            'priority_score': a['priority_score'],
        }
        for i, a in enumerate(top_10)
    ]

    pipeline_data = {
        'feed_stats':    feed_stats,
        'all_curated':   all_curated,
        'top_10':        top_10,
        'all_rejected':  all_rejected,
        'final_reports': final_reports,
    }

    return final_reports, pipeline_data