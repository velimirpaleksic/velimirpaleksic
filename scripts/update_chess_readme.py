# scripts/update_chess_readme.py
import requests, re, os

USERNAME = "velimirpaleksic"
README = "README.md"
START = "<!--chess-stats-start-->"
END = "<!--chess-stats-end-->"

def fetch_json(url):
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return r.json()

def safe_rating(stats, key):
    if key not in stats:
        return None
    node = stats[key]
    for sub in ('last','recent','best','highest'):
        if isinstance(node.get(sub), dict) and node[sub].get('rating') is not None:
            return node[sub]['rating']
    return node.get('rating')

try:
    stats = fetch_json(f"https://api.chess.com/pub/player/{USERNAME}/stats")
except Exception as e:
    print("Failed to fetch stats:", e)
    stats = {}

blitz  = safe_rating(stats, 'chess_blitz')
rapid  = safe_rating(stats, 'chess_rapid')
bullet = safe_rating(stats, 'chess_bullet')
daily  = safe_rating(stats, 'chess_daily')

md = []
md.append("### ♟️ Chess.com")
md.append(f"**{USERNAME}** — live ratings (via Chess.com API)\n")
md.append("| Variant | Rating |")
md.append("|---:|:---:|")
md.append(f"| Blitz | {blitz or '—'} |")
md.append(f"| Rapid | {rapid or '—'} |")
md.append(f"| Bullet | {bullet or '—'} |")
md.append(f"| Daily | {daily or '—'} |")
new_block = "\n".join(md) + "\n"

# replace in README
if os.path.exists(README):
    with open(README, "r", encoding="utf-8") as f:
        content = f.read()
else:
    content = f"{START}\n{END}\n"

pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.DOTALL)
replacement = f"{START}\n{new_block}{END}"
if pattern.search(content):
    content = pattern.sub(replacement, content)
else:
    # append if markers not present
    content = content + "\n" + replacement

with open(README, "w", encoding="utf-8") as f:
    f.write(content)

print("README updated.")
