# -*- coding: utf-8 -*-
"""
Picks a random, longer Persian fact and splits it into a few slides
(chunks) that will be shown one after another over the course of the
video — this keeps viewers watching to the end instead of reading
everything in the first two seconds.

Static curated list (no external API call) for reliability.
"""

import os
import json
import random
import textwrap

FACTS = [
    "عسل هرگز فاسد نمی‌شود. باستان‌شناسان در مقبره‌های مصر باستان عسلی سه‌هزار ساله پیدا کرده‌اند که هنوز قابل خوردن بود، چون ترکیب طبیعی آن اجازه‌ی رشد باکتری را نمی‌دهد.",
    "اختاپوس سه قلب دارد. دو تا از این قلب‌ها فقط خون را به آبشش‌ها می‌رسانند و وقتی اختاپوس شنا می‌کند، از تپش می‌ایستند، به همین دلیل اختاپوس‌ها ترجیح می‌دهند بیشتر وقتشان را با خزیدن بگذرانند تا شنا کردن.",
    "یک روز در سیاره‌ی زهره از یک سال آن طولانی‌تر است. زهره آنقدر آهسته دور خودش می‌چرخد که چرخش کامل آن حدود دویست و چهل و سه روز زمینی طول می‌کشد، در حالی که یک دور کامل به دور خورشید فقط دویست و بیست و پنج روز طول می‌کشد.",
    "کوسه‌ها قبل از درخت‌ها روی زمین ظاهر شدند. فسیل‌های کوسه به حدود چهارصد میلیون سال پیش برمی‌گردد، در حالی که قدیمی‌ترین درخت‌های شناخته‌شده حدود سیصد و پنجاه میلیون سال قدمت دارند.",
    "سمور دریایی هنگام خواب دست‌های یکدیگر را می‌گیرد تا در آب از هم دور نشوند. این رفتار بین مادر و بچه‌ها هم دیده می‌شود تا در طول شب گروه از هم پراکنده نشود.",
    "برج ایفل در تابستان حدود پانزده سانتی‌متر بلندتر می‌شود. فلز آهنی که بدنه‌ی برج را ساخته در گرما منبسط می‌شود و همین باعث افزایش موقت ارتفاع آن می‌شود.",
    "مغز انسان حدود بیست درصد از کل انرژی بدن را مصرف می‌کند، در حالی که تنها حدود دو درصد از وزن بدن را تشکیل می‌دهد. به همین دلیل فکر کردن زیاد واقعاً می‌تواند خسته‌کننده باشد.",
    "پروانه‌ها با پاهایشان مزه را تشخیص می‌دهند. گیرنده‌های شیمیایی روی پاهای آن‌ها به آن‌ها کمک می‌کند بفهمند آیا برگی که روی آن نشسته‌اند برای تخم‌گذاری مناسب است یا نه.",
]

NUM_SLIDES = 4
OUTPUT_PATH = "output/slides.json"


def split_into_slides(text: str, num_slides: int) -> list:
    target_len = max(len(text) // num_slides, 1)
    chunks = textwrap.wrap(text, width=target_len, break_long_words=False)

    # textwrap can produce more/fewer chunks than requested; merge extras
    # into the last slide so we end up with exactly num_slides pieces.
    while len(chunks) > num_slides:
        chunks[-2] = chunks[-2] + " " + chunks[-1]
        chunks.pop()

    return chunks


def main():
    os.makedirs("output", exist_ok=True)
    fact = random.choice(FACTS)
    slides = split_into_slides(fact, NUM_SLIDES)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(slides, f, ensure_ascii=False)

    print(f"Selected fact ({len(slides)} slides): {fact}")


if __name__ == "__main__":
    main()
