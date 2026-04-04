#!/usr/bin/env python3
"""German Vocabulary Quiz - A2 Level"""

import random
import os
import sys


# ANSI color codes (disabled if not a TTY)
class C:
    GREEN  = '\033[92m'
    RED    = '\033[91m'
    YELLOW = '\033[93m'
    BLUE   = '\033[94m'
    CYAN   = '\033[96m'
    BOLD   = '\033[1m'
    RESET  = '\033[0m'

USE_COLOR = sys.stdout.isatty()


def clr(text, *codes):
    if not USE_COLOR:
        return text
    return ''.join(codes) + text + C.RESET


def clear():
    os.system('cls' if os.name == 'nt' else 'clear')


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_vocabulary(filename='vocabulary.txt'):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filepath = os.path.join(script_dir, filename)

    words = []
    with open(filepath, encoding='utf-8') as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('|')
            if len(parts) != 5:
                print(f"Warning: skipping malformed line {lineno}: {line!r}")
                continue
            word, article, english, example_de, example_en = (p.strip() for p in parts)
            words.append({
                'word':       word,
                'article':    article,
                'english':    english,
                'example_de': example_de,
                'example_en': example_en,
            })
    return words


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

SIMPLE_ARTICLES = {'der', 'die', 'das'}


def display(entry):
    """Return 'der/die/das Word' or just 'word' for verbs/adjectives."""
    a = entry['article']
    if a in SIMPLE_ARTICLES:
        return f"{a} {entry['word']}"
    return entry['word']


def show_example(entry):
    print(f"\n  {clr('Example:', C.CYAN)}")
    print(f"  DE: {entry['example_de']}")
    print(f"  EN: {entry['example_en']}")


def show_result(correct, msg_ok, msg_wrong):
    if correct:
        print(clr(f"  Correct!  {msg_ok}", C.GREEN))
    else:
        print(clr(f"  Wrong!    {msg_wrong}", C.RED))


def ask_choice(options):
    """Present a numbered list and return the chosen index (0-based)."""
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        raw = input(f"\n  Your answer (1-{len(options)}): ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return int(raw) - 1
        print(f"  Please enter a number between 1 and {len(options)}.")


def pick_distractors(pool, exclude, n=3):
    """Return n random items from pool that are not in exclude."""
    candidates = [w for w in pool if w not in exclude]
    return random.sample(candidates, min(n, len(candidates)))


def run_quiz(questions, question_fn):
    """Generic quiz runner. question_fn(entry, pool) -> (is_correct: bool)."""
    score = 0
    total = len(questions)
    pool = questions  # for distractor picking; could be full vocab

    for i, entry in enumerate(questions, 1):
        print(f"\n{clr(f'Question {i}/{total}', C.BOLD)}")
        correct = question_fn(entry, pool)
        if correct:
            score += 1
        show_example(entry)
        try:
            input("\n  Press Enter to continue...")
        except KeyboardInterrupt:
            print()
            return score, i
    return score, total


# ---------------------------------------------------------------------------
# Quiz modes
# ---------------------------------------------------------------------------

def q_article(entry, pool):
    """Given a noun, choose the correct article."""
    if entry['article'] not in SIMPLE_ARTICLES:
        return True  # skip non-nouns silently (shouldn't happen after filtering)

    print(f"  What is the article for:  {clr(entry['word'], C.BOLD, C.YELLOW)}")
    print(f"  ({entry['english']})\n")

    correct = entry['article']
    options = list(SIMPLE_ARTICLES)
    random.shuffle(options)
    chosen_idx = ask_choice(options)
    chosen = options[chosen_idx]

    show_result(
        chosen == correct,
        f"{correct} {entry['word']}",
        f"It is  {clr(correct, C.BOLD)} {entry['word']}  (not '{chosen}')",
    )
    return chosen == correct


def q_de_to_en(entry, pool):
    """Given German word (with article), choose English meaning."""
    print(f"  Translate to English:  {clr(display(entry), C.BOLD, C.YELLOW)}\n")

    correct_en = entry['english'].split('/')[0].strip()
    distractors = [w['english'].split('/')[0].strip() for w in pick_distractors(pool, [entry])]
    options = [correct_en] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_en)

    chosen_idx = ask_choice(options)

    show_result(
        chosen_idx == correct_idx,
        f"{display(entry)} = {entry['english']}",
        f"Correct answer: {clr(entry['english'], C.BOLD)}",
    )
    return chosen_idx == correct_idx


def q_en_to_de(entry, pool):
    """Given English meaning, choose German word."""
    hint = entry['english'].split('/')[0].strip()
    print(f"  Translate to German:  {clr(hint, C.BOLD, C.YELLOW)}\n")

    correct_de = display(entry)
    distractors = [display(w) for w in pick_distractors(pool, [entry])]
    options = [correct_de] + distractors
    random.shuffle(options)
    correct_idx = options.index(correct_de)

    chosen_idx = ask_choice(options)

    show_result(
        chosen_idx == correct_idx,
        f"{hint} = {correct_de}",
        f"Correct answer: {clr(correct_de, C.BOLD)}",
    )
    return chosen_idx == correct_idx


# ---------------------------------------------------------------------------
# Vocabulary browser
# ---------------------------------------------------------------------------

def browse(words):
    PAGE = 20
    page = 0
    total_pages = (len(words) + PAGE - 1) // PAGE

    while True:
        clear()
        print(clr("=== VOCABULARY BROWSER ===", C.BOLD, C.BLUE))
        print(f"Page {page + 1}/{total_pages}  |  {len(words)} words total\n")

        start = page * PAGE
        for entry in words[start:start + PAGE]:
            label = clr(f"{display(entry):<38}", C.YELLOW)
            print(f"  {label} {entry['english']}")

        print(f"\n  [n] Next    [p] Previous    [e] Show example    [q] Back to menu")
        cmd = input("  Command: ").strip().lower()

        if cmd == 'n':
            page = min(page + 1, total_pages - 1)
        elif cmd == 'p':
            page = max(page - 1, 0)
        elif cmd == 'e':
            raw = input("  Word number on this page (1-20): ").strip()
            if raw.isdigit():
                idx = start + int(raw) - 1
                if 0 <= idx < len(words):
                    show_example(words[idx])
                    input("  Press Enter...")
        elif cmd == 'q':
            break


# ---------------------------------------------------------------------------
# Score display
# ---------------------------------------------------------------------------

def show_score(score, total):
    pct = score / total * 100 if total else 0
    print(f"\n{clr('=== RESULTS ===', C.BOLD, C.BLUE)}")
    print(f"  Score: {clr(f'{score}/{total}', C.BOLD)}  ({pct:.0f}%)\n")
    if pct >= 90:
        print(clr("  Excellent!  Ausgezeichnet!", C.GREEN))
    elif pct >= 70:
        print(clr("  Good job!  Gut gemacht!", C.CYAN))
    elif pct >= 50:
        print(clr("  Not bad!  Weiter so!", C.YELLOW))
    else:
        print(clr("  Keep practising!  Übe weiter!", C.RED))


# ---------------------------------------------------------------------------
# Main menu
# ---------------------------------------------------------------------------

def ask_num_questions(default=10):
    raw = input(f"  How many questions? (default {default}): ").strip()
    try:
        return max(1, int(raw)) if raw else default
    except ValueError:
        return default


def main():
    clear()
    print(clr("=" * 52, C.BLUE))
    print(clr("     GERMAN VOCABULARY QUIZ  –  A2 Level", C.BOLD, C.BLUE))
    print(clr("=" * 52, C.BLUE))

    try:
        words = load_vocabulary()
    except FileNotFoundError:
        print("Error: vocabulary.txt not found next to quiz.py!")
        sys.exit(1)

    nouns = [w for w in words if w['article'] in SIMPLE_ARTICLES]
    print(f"\n  Loaded {clr(str(len(words)), C.BOLD)} words  ({len(nouns)} nouns with articles)\n")

    MENU = [
        ("Article quiz      – Choose der / die / das",      nouns,  q_article),
        ("German → English  – Choose the English meaning",  words,  q_de_to_en),
        ("English → German  – Choose the German word",      words,  q_en_to_de),
        ("Browse vocabulary",                                None,   None),
        ("Quit",                                            None,   None),
    ]

    while True:
        print(clr("\nMAIN MENU", C.BOLD))
        for i, (label, _, _) in enumerate(MENU, 1):
            print(f"  {i}. {label}")

        choice = input("\n  Select (1-5): ").strip()
        if not choice.isdigit() or not 1 <= int(choice) <= len(MENU):
            print("  Invalid choice.")
            continue

        idx = int(choice) - 1
        label, pool, question_fn = MENU[idx]

        if idx == 3:           # Browse
            browse(words)
        elif idx == 4:         # Quit
            print(clr("\n  Tschüss! Auf Wiedersehen!\n", C.CYAN))
            break
        else:
            clear()
            print(clr(f"=== {label.upper()} ===", C.BOLD, C.BLUE))
            n = ask_num_questions()
            if len(pool) < 4:
                print("  Not enough words for a quiz.")
                continue
            questions = random.sample(pool, min(n, len(pool)))

            # Pass the full pool for distractor generation
            full_pool_fn = lambda e, _pool, fn=question_fn: fn(e, words)

            try:
                score, total = run_quiz(questions, full_pool_fn)
            except KeyboardInterrupt:
                print(clr("\n  Quiz interrupted.", C.YELLOW))
                score, total = 0, 0

            if total > 0:
                show_score(score, total)

        input("\n  Press Enter to return to menu...")
        clear()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(clr("\n\nAuf Wiedersehen!\n", C.CYAN))
