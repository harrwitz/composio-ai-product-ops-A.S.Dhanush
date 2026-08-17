"""
Pattern Analysis Script for Composio Toolkit Research
Computes aggregate metrics, auth distribution, self-serve percentages, top blockers,
existing MCP counts, easy wins, and outreach targets from data/apps_final.jsonl.
Dynamically calculates all headline insight percentages from the dataset.
"""

import json
import os
from collections import Counter, defaultdict

def analyze_patterns(filepath="data/apps_final.jsonl"):
    if not os.path.exists(filepath):
        print(f"Error: {filepath} not found.")
        return

    apps = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                apps.append(json.loads(line))

    total_apps = len(apps)

    # 1. Auth method distribution overall and per category
    overall_auth = Counter()
    category_auth = defaultdict(Counter)

    # 2. Self-serve % by category
    category_total = Counter()
    category_self_serve = Counter()
    category_gated = Counter()
    category_partial = Counter()

    # 3. Blockers
    blockers = Counter()

    # 4. Existing MCP count
    existing_mcp_count = 0

    # 5. Easy Wins & Needs Outreach lists
    easy_wins = []
    needs_outreach = []

    for app in apps:
        cat = app['category']
        category_total[cat] += 1

        # Auth
        for auth in app['auth_methods']:
            overall_auth[auth] += 1
            category_auth[cat][auth] += 1

        # Self-serve
        ss = app['self_serve']
        if ss == 'self-serve':
            category_self_serve[cat] += 1
        elif ss == 'gated':
            category_gated[cat] += 1
        elif ss == 'partial':
            category_partial[cat] += 1

        # Blockers
        if app['buildability_verdict'] == 'blocked' and app.get('main_blocker'):
            blockers[app['main_blocker']] += 1

        # Existing MCP
        if app.get('existing_mcp'):
            existing_mcp_count += 1

        # Easy wins condition: self-serve + broad REST/GraphQL + no existing MCP
        if app['self_serve'] == 'self-serve' and app['api_breadth'] == 'broad' and not app.get('existing_mcp'):
            easy_wins.append({
                "app": app['app'],
                "category": cat,
                "api_surface": app['api_surface'],
                "auth_methods": app['auth_methods']
            })

        # Needs outreach condition: gated or partial partner gate
        if app['self_serve'] in ['gated', 'partial']:
            needs_outreach.append({
                "app": app['app'],
                "category": cat,
                "self_serve": app['self_serve'],
                "main_blocker": app.get('main_blocker')
            })

    # Self serve % per category
    self_serve_pct_by_cat = {}
    gated_partial_pct_by_cat = {}
    for cat, total in category_total.items():
        ss_cnt = category_self_serve[cat]
        gp_cnt = category_gated[cat] + category_partial[cat]
        self_serve_pct_by_cat[cat] = round((ss_cnt / total) * 100, 1)
        gated_partial_pct_by_cat[cat] = round((gp_cnt / total) * 100, 1)

    # Dynamic Computation of Headline Statistics
    crm_mktg_apps = [a for a in apps if a['category'] in ['CRM and Sales', 'Marketing, Ads, Email and Social']]
    crm_mktg_oauth = sum(1 for a in crm_mktg_apps if 'OAuth2' in a['auth_methods'])
    crm_mktg_oauth_pct = round((crm_mktg_oauth / len(crm_mktg_apps)) * 100) if crm_mktg_apps else 0

    dev_data_apps = [a for a in apps if a['category'] in ['Developer, Infra and Data platforms', 'Data, SEO and Scraping']]
    dev_data_apikey = sum(1 for a in dev_data_apps if 'API Key' in a['auth_methods'])
    dev_data_apikey_pct = round((dev_data_apikey / len(dev_data_apps)) * 100) if dev_data_apps else 0

    top_ss_cat = max(self_serve_pct_by_cat, key=self_serve_pct_by_cat.get)
    top_ss_pct = int(self_serve_pct_by_cat[top_ss_cat])

    top_gp_cat = max(gated_partial_pct_by_cat, key=gated_partial_pct_by_cat.get)
    top_gp_pct = int(gated_partial_pct_by_cat[top_gp_cat])

    # Top 3 Dynamically Computed Headline Patterns
    headline_patterns = [
        f"OAuth2 dominates enterprise CRM & Marketing tools ({crm_mktg_oauth_pct}% of category apps), while Developer & Data platforms lean heavily on API Keys ({dev_data_apikey_pct}%).",
        f"{top_ss_cat} leads self-serve accessibility ({top_ss_pct}% self-serve), whereas {top_gp_cat} tools have the highest partner gating ({top_gp_pct}% gated/partial).",
        f"High-Value Unclaimed Opportunity: Found {len(easy_wins)} 'Easy Win' apps with broad public REST/GraphQL APIs and zero existing MCP servers ready for instant toolkit generation."
    ]

    results = {
        "total_apps": total_apps,
        "overall_auth_distribution": dict(overall_auth),
        "category_auth_distribution": {k: dict(v) for k, v in category_auth.items()},
        "self_serve_pct_by_category": self_serve_pct_by_cat,
        "most_common_blockers": blockers.most_common(5),
        "existing_mcp_count": existing_mcp_count,
        "easy_wins_count": len(easy_wins),
        "easy_wins": easy_wins,
        "needs_outreach_count": len(needs_outreach),
        "needs_outreach": needs_outreach,
        "headline_patterns": headline_patterns
    }

    print("=== PATTERN ANALYSIS RESULTS ===")
    print(f"Total Apps: {total_apps}")
    print(f"Existing MCPs: {existing_mcp_count}")
    print(f"Easy Wins Count: {len(easy_wins)}")
    print(f"Needs Outreach Count: {len(needs_outreach)}")
    print("\n--- Headline Insights ---")
    for i, h in enumerate(headline_patterns, 1):
        print(f"{i}. {h}")

    return results

if __name__ == "__main__":
    analyze_patterns()
