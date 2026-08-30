"""
Picks a random interesting fact and saves it as plain text, to be drawn
onto the background image by draw_text.py.

Kept as a static curated list (no external API call) for reliability —
this is one less thing that can break or change out from under the
pipeline. Add your own facts freely; keep them short (under ~140 chars)
so they fit comfortably on a vertical video without shrinking too much.
"""

import os
import random

FACTS = [
    "Honey never spoils — archaeologists have found 3,000-year-old honey in Egyptian tombs that's still edible.",
    "Octopuses have three hearts, and two of them stop beating when they swim.",
    "A day on Venus is longer than its year — it rotates slower than it orbits the Sun.",
    "Bananas are berries, but strawberries aren't.",
    "The Eiffel Tower grows about 6 inches taller in summer due to heat expansion.",
    "Sharks existed before trees — they're older than the first trees by about 50 million years.",
    "Wombat poop is cube-shaped, which keeps it from rolling away and marks their territory.",
    "There are more possible chess games than atoms in the observable universe.",
    "Sea otters hold hands while sleeping so they don't drift apart.",
    "The shortest war in history lasted about 38 minutes, between Britain and Zanzibar in 1896.",
    "A single cloud can weigh more than a million pounds.",
    "Octopuses can taste with their arms — every sucker has chemoreceptors.",
    "The inventor of the Pringles can is buried in one.",
    "Some turtles can breathe through their butts.",
    "Hot water can freeze faster than cold water under certain conditions — it's called the Mpemba effect.",
    "The human brain uses about 20% of the body's total energy despite being only 2% of its weight.",
    "Butterflies taste with their feet.",
    "A group of flamingos is called a 'flamboyance'.",
    "The Great Wall of China is not visible from space with the naked eye — that's a myth.",
    "Cows have best friends and get stressed when separated from them.",
]

OUTPUT_PATH = "output/fact.txt"


def main():
    os.makedirs("output", exist_ok=True)
    fact = random.choice(FACTS)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(fact)

    print(f"Selected fact: {fact}")


if __name__ == "__main__":
    main()
