STREAM_GENERAL_LOGS = "/home/alex-wsl/minecraft_related/streams/tiktok/main/test.log"

"""Ici on déclare les path Redis à appeler ainsi qu'une petite fonction
qui génère le markdown suivant:"""
ENDPOINT = "dada"

stream_data = {
    "general": {
        "duration": ENDPOINT,
        "max_viewers": ENDPOINT,
        "average_viewers": ENDPOINT,
        "new_followers": ENDPOINT,
    },
    "player": {
        "highest_score": ENDPOINT,
        "best_winstreak": ENDPOINT,
        "most_guesses": ENDPOINT,
        "most_correct_guesses": ENDPOINT,
        "most_incorrect_guesses": ENDPOINT,
        "most_recurrent": ENDPOINT,
    }
}

# We'll generate this format:
"""
Stream | info
----:  | :----
Cell   | Cell
Cell   | Cell
"""
# Out of the dictionnary.
md = ""
for category in stream_data:
    md += f"**{category.capitalize()}** | Info\n"
    md += ":----: | ----:\n"
    for info in stream_data[category]:
        md += f"{info.capitalize().replace('_', ' ')} | {stream_data[category][info]}\n"
    md += "\n"
    
STREAM_GENERAL_INFO = md

STREAM_GENERAL_INFO = \
"""\
**General** | info
----: | :----
Duration | 14h50
Max viewers | 7800
Average viewers | 4000
New followers | 1500

**Player** | info
----: | :----
Highest score | Maris.
Best winstreak | Maris bien sûr
Most guesses | Bourlingue
Most correct guesses | Jannninna
Most incorrect guesses | Paulinbe
Most recurrent | Maris
"""

import markdown
