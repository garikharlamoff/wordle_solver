# solver_selenium.py
import time
import urllib.request
from collections import Counter
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def load_words():
    url = "https://raw.githubusercontent.com/joric/wordle-solver/main/ru.txt"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            text = r.read().decode("utf-8")
            return sorted(set(w.strip().lower() for w in text.splitlines() if len(w.strip()) == 5))
    except:
        return ["океан", "парик", "месяц", "столб", "книга", "ветер"]

WORDS = load_words()
print(f"Словарь: {len(WORDS)} слов")

def matches(word, guesses):
    for guess, pattern in guesses:
        required = Counter()
        for g, p in zip(guess, pattern):
            if p in ("G", "Y"):
                required[g] += 1
        for i, (g, p) in enumerate(zip(guess, pattern)):
            if p == "G" and word[i] != g:
                return False
            if p == "Y" and (word[i] == g or g not in word):
                return False
        for i, (g, p) in enumerate(zip(guess, pattern)):
            if p == "B" and word.count(g) > required[g]:
                return False
    return True

def suggest(candidates):
    if len(candidates) <= 8:
        return candidates
    freq = Counter()
    for w in candidates:
        freq.update(set(w))
    return sorted(candidates, key=lambda w: sum(freq[c] for c in set(w)), reverse=True)[:10]

def parse_pattern(driver, row_index):
    tiles = driver.find_elements(By.CSS_SELECTOR, ".tile")
    start = row_index * 5
    pattern = ""
    for tile in tiles[start:start + 5]:
        aria = (tile.get_attribute("aria-label") or "").lower()
        if "правильной позиции" in aria or "на своём месте" in aria or "правильном месте" in aria:
            pattern += "G"
        elif "неправильной позиции" in aria or "другом месте" in aria:
            pattern += "Y"
        else:
            pattern += "B"
    return pattern

def type_word(driver, word):
    for letter in word:
        try:
            btn = driver.find_element(By.CSS_SELECTOR, f'button.key[aria-label="{letter}"]')
        except:
            btn = driver.find_element(By.XPATH, f'//button[contains(@class,"key") and normalize-space()="{letter}"]')
        btn.click()
        time.sleep(1)
    # Ввод
    enter = driver.find_element(By.XPATH, '//button[contains(translate(., "ВВОД", "ввод"), "ввод")]')
    enter.click()
    time.sleep(4.0)

def close_modals(driver):
    try:
        driver.find_element(By.XPATH, '//button[contains(text(),"×")]').click()
        time.sleep(1)
    except:
        pass
    try:
        driver.find_element(By.XPATH, '//button[contains(text(),"ДАЛЕЕ") or contains(text(),"Далее")]').click()
        time.sleep(1)
    except:
        pass

def main():
    options = Options()
    # options.add_argument("--headless")  # раскомментируй, если не хочешь видеть окно
    options.add_argument("--window-size=1280,900")

    driver = webdriver.Chrome(options=options)
    driver.get("https://wordle.belousov.one/")
    time.sleep(2)
    close_modals(driver)

    guesses = []
    candidates = WORDS[:]
    used = set()

    for attempt in range(6):
        if not candidates:
            print("Кандидатов не осталось")
            break

        suggestions = suggest(candidates)
        word = next((s for s in suggestions if s not in used), candidates[0])
        used.add(word)

        print(f"\nПопытка {attempt+1}: {word.upper()}  (осталось: {len(candidates)})")
        type_word(driver, word)

        pattern = parse_pattern(driver, attempt)
        print(f"Результат: {pattern}")

        if pattern == "GGGGG":
            print(f"\n>>> УГАДАНО: {word.upper()} <<<")
            break

        guesses.append((word, pattern))
        candidates = [w for w in candidates if matches(w, guesses)]
        print(f"После фильтрации: {len(candidates)}")
        if len(candidates) <= 15:
            print("Кандидаты:", ", ".join(candidates))

    print("\nБраузер закроется через 20 секунд...")
    time.sleep(20)
    driver.quit()

if __name__ == "__main__":
    main()