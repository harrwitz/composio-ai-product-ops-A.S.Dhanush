import json

with open('data/apps_final.jsonl', encoding='utf-8') as f:
    rows = [json.loads(l) for l in f if l.strip()]

print('Total rows:', len(rows))
print('Existing MCPs:', sum(1 for r in rows if r['existing_mcp']))

for name in ['Coda', 'Amazon Selling Partner', 'Zoho Cliq', 'LinkedIn Ads']:
    r = next(x for x in rows if x['app'] == name)
    print(f"\n{name}")
    print(' URL:', r['evidence_url'])
    print(' Notes:', r['verification_notes'])