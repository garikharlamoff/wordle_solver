# wordle_solver_ru.py
# Решатель для https://wordle.belousov.one/

import urllib.request
from collections import Counter

# -------------------------------------------------
# Словарь (берём из открытого репозитория, совместимого с belousov)
# -------------------------------------------------
def load_words():
    url = "https://raw.githubusercontent.com/joric/wordle-solver/main/ru.txt"
    try:
        with urllib.request.urlopen(url) as response:
            text = response.read().decode("utf-8")
            words = [w.strip().lower() for w in text.splitlines() if len(w.strip()) == 5]
            return sorted(set(words))
    except Exception as e:
        print("Не удалось скачать словарь:", e)
        print("Используем встроенный минимальный набор...")
        return ["океан", "парик", "месяц", "столб", "книга", "ветер", "город",
                "маска", "речка", "почка", "точка", "бочка", "дочка", "мочка"]

WORDS = load_words()
print(f"Загружено слов: {len(WORDS)}")

# -------------------------------------------------
# Проверка, соответствует ли слово всем подсказкам
# -------------------------------------------------
def matches(word: str, guesses: list[tuple[str, str]]) -> bool:
    """
    guesses = [("слово", "GYBBG"), ...]
    G = зелёный, Y = жёлтый, B = серый (black/gray)
    """
    for guess, pattern in guesses:
        # Считаем, сколько раз каждая буква должна встретиться (G + Y)
        required = Counter()
        for g, p in zip(guess, pattern):
            if p in ("G", "Y"):
                required[g] += 1

        # Проверяем зелёные и жёлтые позиции
        for i, (g, p) in enumerate(zip(guess, pattern)):
            if p == "G":
                if word[i] != g:
                    return False
            elif p == "Y":
                if word[i] == g or g not in word:
                    return False

        # Проверяем серые буквы (с учётом уже найденных G/Y)
        for i, (g, p) in enumerate(zip(guess, pattern)):
            if p == "B":
                # Буква не должна встречаться больше, чем нужно по G+Y
                if word.count(g) > required[g]:
                    return False

    return True

# -------------------------------------------------
# Рекомендация следующего слова (простая эвристика)
# -------------------------------------------------
def suggest(candidates: list[str], guesses: list) -> list[str]:
    if not candidates:
        return []
    if len(candidates) <= 10:
        return candidates

    # Частотность букв среди оставшихся кандидатов
    freq = Counter()
    for w in candidates:
        freq.update(set(w))          # уникальные буквы

    def score(word):
        return sum(freq[c] for c in set(word))

    ranked = sorted(candidates, key=score, reverse=True)
    return ranked[:15]

# -------------------------------------------------
# Главный цикл
# -------------------------------------------------
def main():
    print("=" * 50)
    print("Решатель Вордли (wordle.belousov.one)")
    print("=" * 50)
    print("Хорошие стартовые слова: океан, парик, месяц, столб, крона")
    print()
    print("После каждого хода вводи:")
    print("  1. Слово (5 букв)")
    print("  2. Результат: G = зелёный, Y = жёлтый, B = серый")
    print("     Пример: GYBBG")
    print("Команды: 'q' — выход, 'r' — сброс")
    print()

    guesses = []          # список (слово, паттерн)
    candidates = WORDS[:]

    while True:
        if not candidates:
            print("Кандидатов не осталось. Проверь ввод.")
            break

        print(f"\nОсталось кандидатов: {len(candidates)}")
        if len(candidates) <= 20:
            print("Возможные слова:", ", ".join(candidates))
        else:
            suggestions = suggest(candidates, guesses)
            print("Рекомендую попробовать:", ", ".join(suggestions[:8]))

        word = input("\nВведи слово (или q/r): ").strip().lower()
        if word == "q":
            break
        if word == "r":
            guesses.clear()
            candidates = WORDS[:]
            print("Сброшено.")
            continue
        if len(word) != 5 or not word.isalpha():
            print("Нужно ровно 5 русских букв.")
            continue

        pattern = input("Результат (G/Y/B, например GYBBG): ").strip().upper()
        if len(pattern) != 5 or any(c not in "GYB" for c in pattern):
            print("Паттерн должен состоять из 5 символов G, Y или B.")
            continue

        guesses.append((word, pattern))
        candidates = [w for w in candidates if matches(w, guesses)]

        if len(candidates) == 1:
            print(f"\n>>> Ответ найден: {candidates[0].upper()} <<<")
            break
        if not candidates:
            print("Нет подходящих слов. Возможно, ошибка в вводе цветов.")

if __name__ == "__main__":
    main()