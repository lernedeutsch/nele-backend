# NELE — lekkie zasady rozwoju

Celem jest szybki rozwój Nele bez powracających regresji. Nie dokładamy ciężkiego procesu tam, gdzie nie jest potrzebny.

## 1. Bugfix = test regresyjny
Jeżeli naprawiamy konkretny błąd, dodajemy możliwie mały test, który odtwarza problem i potwierdza naprawę.

## 2. Jeden PR = jeden temat
Nie mieszamy niezależnych zmian (np. Conversation Engine, TTS i wellbeing) w jednym PR. Mały zakres ułatwia testowanie, review i bezpieczne cofnięcie zmiany.

## 3. Testuj proporcjonalnie do ryzyka
- PR/push: istniejący szybki zestaw unit + walidacja treści.
- Zmiana wpływająca na rozmowę: odpowiedni test rozmowy/regresyjny.
- Po merge do main: istniejący Nele Live smoke test.
- Ciężkie E2E: okresowo lub ręcznie przy większej zmianie.

Nie wymagamy ciężkiego E2E dla każdej małej zmiany.

## 4. Nowa regresja blokuje daną zmianę
Znane, niezwiązane problemy nie powinny zatrzymywać całego rozwoju. Nowa regresja spowodowana bieżącą zmianą powinna zostać naprawiona przed merge.

## 5. Conversation Engine ma jeden kierunek przepływu
Docelowy przepływ:
UNDERSTAND → CONTEXT → RETRIEVE → DECIDE → RESPOND → LEARN

Zmiany powinny zachowywać jasne odpowiedzialności między etapami i nie tworzyć drugiego równoległego silnika rozmowy.

## 6. Automaty: równoległa analiza, sekwencyjne zmiany
Automaty mogą równolegle analizować wyniki i testy, ale nie powinny jednocześnie modyfikować tego samego obszaru kodu, scalać konkurencyjnych zmian ani wdrażać sprzecznych poprawek.

Jeśli inny PR/automat dotyka tych samych plików lub tej samej odpowiedzialności Conversation Engine:
1. sprawdź jego stan,
2. oprzyj kolejną zmianę na aktualnym main,
3. wykonaj małą zmianę,
4. uruchom właściwe testy,
5. dopiero potem przejdź do następnej zmiany.

## Zasada nadrzędna
Szybki rozwój → mała zmiana → szybki test → bezpieczny merge → Nele Live → następna zmiana.
