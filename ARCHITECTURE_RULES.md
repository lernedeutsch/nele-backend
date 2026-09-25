# OBOWIĄZKOWA GLOBALNA ZASADA ARCHITEKTURY NELE

Każdą zmianę w logice, mechanizmach nauczania, rozmowie, pamięci lub architekturze Nele projektuj przede wszystkim jako **rozwiązanie globalne, wielokrotnego użytku i przygotowane na przyszły rozwój projektu**.

Nie twórz mechanizmu tylko dla jednej konkretnej lekcji, jednego dialogu, jednego tematu, jednego słowa albo jednego przykładu, jeżeli problem może zostać rozwiązany na poziomie wspólnej architektury.

# 1. TRZY PODSTAWOWE WARSTWY

**Lekcja określa, CZEGO Nele uczy.**

**Teaching Engine określa, JAK Nele pomaga uczniowi się tego nauczyć.**

**Conversation Engine określa, JAK Nele prowadzi naturalną rozmowę.**

Te warstwy powinny współpracować, ale nie powinny niepotrzebnie duplikować swojej logiki.

# 2. TEACHING ENGINE — GLOBALNE NAUCZANIE

Wspólna architektura nauczania odpowiada m.in. za: rozumienie odpowiedzi, krótkie odpowiedzi, ocenę błędów, Adaptive Scaffolding, stopniowanie podpowiedzi, Response Expansion, decyzję o pełnym zdaniu, natural short answers, wygaszanie pomocy, pamięć błędów i sukcesów, inteligentne powtórki, następny krok, Learning Outcome Tracking, postęp i zapobieganie zapętleniom.

Lekcja powinna dostarczać przede wszystkim dane: cel, słownictwo, target sentences, pytania, accepted answers, natural short answers, dialogi, kontekst oraz cele komunikacyjne i gramatyczne.

Nie implementuj ponownie Teaching Engine wewnątrz każdej lekcji.

# 3. CONVERSATION ENGINE — GLOBALNA ROZMOWA

Conversation Engine powinien globalnie odpowiadać za pamiętanie kontekstu, rozumienie krótkich i niepełnych wypowiedzi, intencję, znaczenie zamiast samych słów-kluczy, utrzymanie i zmianę tematu, naturalne pytania uzupełniające, brak powtórzeń i pętli, długość wypowiedzi, poziom języka, delikatne poprawianie oraz rozszerzanie odpowiedzi tylko wtedy, gdy ma to wartość dydaktyczną.

Nie buduj go jako setek reguł `jeżeli X → odpowiedz Y`. Powinien rozumieć stan i znaczenie rozmowy.

# 4. TEMAT ROZMOWY TO DANE, NIE NOWY SILNIK

Nie twórz osobnych Conversation Engines dla pracy, pogody, jedzenia, rodziny, zakupów, hotelu, restauracji, podróży, czasu wolnego, zdrowia czy transportu.

Tematy dostarczają słownictwo, przykładowe pytania, intencje, kierunki rozmowy, konstrukcje i cele komunikacyjne. Wspólny Conversation Engine korzysta z tych danych.

# 5. KRÓTKIE ODPOWIEDZI MUSZĄ BYĆ ROZUMIANE GLOBALNIE

Odpowiedzi takie jak `gut`, `schlecht`, `Arbeit`, `Pizza`, `Polen`, `8`, `heute`, `ja`, `nein`, `müde` należy interpretować w kontekście aktualnego pytania. Krótka odpowiedź nie oznacza automatycznie błędu.

Analizuj: pytanie Nele → odpowiedź ucznia → znaczenie w kontekście → potrzebna pomoc → naturalna kontynuacja.

# 6. NIE POPRAWIAJ MECHANICZNIE KAŻDEJ ODPOWIEDZI

Rozróżniaj błąd utrudniający komunikację, błąd gramatyczny, drobną niedoskonałość, naturalną krótką odpowiedź, odpowiedź poprawną znaczeniowo i sytuację, w której warto nauczyć pełnego zdania.

# 7. ADAPTACYJNA POMOC MA BYĆ WSPÓLNA

Stosuj wspólną drabinę: samodzielna odpowiedź → prostsze pytanie → wybór → początek zdania → prosty model → powtórzenie modelu.

Nie ujawniaj pełnej odpowiedzi zbyt wcześnie. Po sukcesie natychmiast zmniejszaj poziom pomocy. Mechanizm ma działać również w przyszłych lekcjach i scenariuszach.

# 8. PAMIĘĆ MA BYĆ WSPÓLNA

Wspólny Learner Model powinien udostępniać odpowiednim modułom m.in. imię, poziom, poznane słownictwo, typowe błędy, trudne konstrukcje, sukcesy, historię powtórek, potrzebny poziom pomocy i postęp. Nie twórz niespójnych pamięci modułowych dla tych samych informacji.

# 9. PRZYSZŁE LEKCJE I ROZMOWY MUSZĄ DZIEDZICZYĆ INTELIGENCJĘ

Każdy nowy mechanizm projektuj dla istniejących i przyszłych A1/A2 i kolejnych poziomów, dialogów, scenariuszy sytuacyjnych, nowych tematów i przyszłych funkcji. Nie zakładaj konkretnego numeru lekcji ani tematu.

# 10. ZERO NIEPOTRZEBNEGO HARDCODINGU

Unikaj `if lesson == 2`, `if answer == "Polen"`, `if topic == "weather"`, `if user == "Pizza": response = ...`, jeżeli można użyć wspólnej logiki, konfiguracji, metadanych, stanu rozmowy, danych lekcji/tematu lub Learner Model.

# 11. NAJPIERW SPRAWDŹ ISTNIEJĄCĄ ARCHITEKTURĘ

Przed nowym modułem sprawdź istniejące silniki, znajdź odpowiedzialną warstwę, spróbuj ją rozszerzyć i nie twórz równoległego silnika wykonującego tę samą pracę.

# 12. OBOWIĄZKOWY TEST PRZYSZŁEGO PRZYPADKU

Każdy nowy globalny mechanizm testuj również na przykładzie nieużytym podczas implementacji. Jeśli powstał dla `Polen → Ich komme aus Polen.`, przetestuj np. `Kaffee → Ich möchte einen Kaffee.` oraz `Berlin → Ich fahre morgen nach Berlin.`.

Dla Conversation Engine mechanizm zbudowany przy rozmowie o pracy przetestuj również na niepowiązanym temacie.

# 13. TESTUJ DŁUŻSZĄ ROZMOWĘ

Testuj pełną sesję Nele → uczeń → Nele → uczeń… i wykrywaj powtarzanie pytań, utratę kontekstu, pętle, nadmierne poprawianie, zbyt szybkie zmiany tematów, zbyt długie wypowiedzi, niewłaściwy poziom i brak reakcji na wcześniejszą odpowiedź.

# 14. ZACHOWAJ ROZDZIELENIE TRYBÓW

📚 Mit dem Kurs üben: większy nacisk na cel dydaktyczny, konstrukcję docelową, ćwiczenie i postęp.

☕ Frei sprechen: większy nacisk na naturalną rozmowę, płynność, kontekst i swobodną komunikację.

Współdzielaj podstawowe możliwości, ale pozwól polityce trybu decydować, jak z nich korzystać. Nie kopiuj całych silników między trybami.

# 15. WYJĄTKI LOKALNE

Są dozwolone tylko dla rzeczywiście wyjątkowego celu lekcji/scenariusza. Wyjaśnij, dlaczego globalny mechanizm nie wystarcza, ogranicz wyjątek do minimum, nie kopiuj całego silnika i sprawdź, czy wyjątek może być konfiguracją.

# 16. KRYTERIUM ZAKOŃCZENIA PRZEBUDOWY

Przed zakończeniem sprawdź:
1. Czy mechanizm jest we właściwej wspólnej warstwie?
2. Czy nie powstała druga implementacja tej samej funkcji?
3. Czy nie zależy niepotrzebnie od konkretnej lekcji?
4. Czy nie zależy niepotrzebnie od konkretnego tematu?
5. Czy przyszłe lekcje mogą z niego korzystać?
6. Czy przyszłe dialogi i tematy mogą z niego korzystać?
7. Czy działa na nowym, niehardcodowanym przykładzie?
8. Czy działa w dłuższej rozmowie?
9. Czy pamięta kontekst?
10. Czy nie powoduje zapętleń?
11. Czy pomoc zmniejsza się po sukcesie?
12. Czy istniejące funkcje nadal działają?
13. Czy testy jednostkowe, regresyjne i E2E przechodzą?

# 17. ZASADA KOŃCOWA

Każda większa przebudowa Nele powinna pozostawić po sobie **nową zdolność całego systemu**, a nie wyłącznie poprawiony pojedynczy przykład.

Po zakończeniu powinno być możliwe powiedzenie: **„Od teraz Nele potrafi X globalnie.”**, a nie: **„Od teraz Nele potrafi X tylko w Lektion 2.”**

# CEL

Nele ma rozwijać się jako jeden spójny system:

**Learner Model + Teaching Engine + Conversation Engine + pamięć + treści lekcji i tematów.**

Nowe lekcje, dialogi i tematy powinny automatycznie korzystać z wcześniej zbudowanej inteligencji Nele albo wymagać jedynie prostej konfiguracji — bez ponownego programowania tych samych zachowań.
