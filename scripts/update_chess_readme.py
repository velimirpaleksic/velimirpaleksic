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

def create_markdown(stats):
    blitz = stats.get('chess_blitz', {})
    bullet = stats.get('chess_bullet', {})
    rapid = stats.get('chess_rapid', {})
    daily = stats.get('chess_daily', {})
    tactics = stats.get('tactics', {})
    puzzle_rush = stats.get('puzzle_rush', {})

    md = []
    md.append("### ♟️ Chess.com Stats\n")
    md.append("| Variant | Rating | Best Game |")
    md.append("|---------|-------:|----------|")

    for name, data in [('Daily', daily), ('Rapid', rapid), ('Bullet', bullet), ('Blitz', blitz)]:
        rating = data.get('last', {}).get('rating', '—')
        best_game = data.get('best', {}).get('game', '')
        link = f"[Link]({best_game})" if best_game else "—"
        md.append(f"| {name} | {rating} | {link} |")

    puzzle_score = puzzle_rush.get('best', {}).get('score', '—')
    tactics_rating = tactics.get('highest', {}).get('rating', '—')

    md.append(f"\nPuzzle Rush Best Score: {puzzle_score}")
    md.append(f"Highest Tactics Rating: {tactics_rating}")

    return "\n".join(md) + "\n"

def update_readme(content):
    pattern = re.compile(re.escape(START) + ".*?" + re.escape(END), re.DOTALL)
    new_block = f"{START}\n{content}{END}"
    if pattern.search(content):
        return pattern.sub(new_block, content)
    else:
        # append if markers not present
        return content + "\n" + new_block

def main():
    try:
        stats = fetch_json(f"https://api.chess.com/pub/player/{USERNAME}/stats")
    except Exception as e:
        print("Failed to fetch stats:", e)
        stats = {}

    md_content = create_markdown(stats)

    if os.path.exists(README):
        with open(README, "r", encoding="utf-8") as f:
            readme_text = f.read()
    else:
        readme_text = f"{START}\n{END}\n"

    updated_text = update_readme(readme_text)

    with open(README, "w", encoding="utf-8") as f:
        f.write(updated_text)

    print("README.md updated with latest Chess.com stats!")

if __name__ == "__main__":
    main()
