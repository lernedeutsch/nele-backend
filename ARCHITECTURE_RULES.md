# OBOWIĄZKOWA GLOBALNA ZASADA ARCHITEKTURY NELE

Każdą zmianę w logice, mechanizmach nauczania, rozmowie, pamięci lub architekturze Nele projektuj przede wszystkim jako **rozwiązanie globalne, wielokrotnego użytku i przygotowane na przyszły rozwój projektu**.

Nie twórz mechanizmu tylko dla jednej konkretnej lekcji, jednego dialogu, jednego tematu, jednego słowa albo jednego przykładu, jeżeli problem może zostać rozwiązany na poziomie wspólnej architektury.

# 1. TRZY PODSTAWOWE WARSTWY

Przyjmij zasadę:

**Lekcja określa, CZEGO Nele uczy.**

**Teaching Engine określa, JAK Nele pomaga uczniowi się tego nauczyć.**

**Conversation Engine określa, JAK Nele prowadzi naturalną rozmowę.**

Te warstwy powinny współpracować, ale nie powinny niepotrzebnie duplikować swojej logiki.

---

# 2. TEACHING ENGINE — GLOBALNE NAUCZANIE

Wspólna architektura nauczania powinna odpowiadać między innymi za:

- rozumienie odpowiedzi ucznia,
- rozpoznawanie krótkich odpowiedzi,
- ocenę błędów,
- Adaptive Scaffolding,
- stopniowanie podpowiedzi,
- Response Expansion,
- decyzję, kiedy poprosić o pełne zdanie,
- decyzję, kiedy zaakceptować naturalną krótką odpowiedź,
- wygaszanie pomocy po sukcesie,
- pamięć błędów i sukcesów,
- inteligentne powtórki,
- dobór następnego kroku nauki,
- Learning Outcome Tracking,
- kontrolę postępu,
- zapobieganie zapętleniom.

Lekcja powinna dostarczać przede wszystkim danych:

- celu,
- słownictwa,
- zdań docelowych,
- pytań,
- accepted answers,
- natural short answers,
- dialogów,
- kontekstu,
- celów komunikacyjnych,
- celów gramatycznych.

Nie implementuj ponownie Teaching Engine wewnątrz każdej lekcji.

---

# 3. CONVERSATION ENGINE — GLOBALNA ROZMOWA

Rozmowy Nele również muszą korzystać ze wspólnego mechanizmu.

Conversation Engine powinien globalnie odpowiadać za:

- pamiętanie kontekstu bieżącej rozmowy,
- rozumienie krótkich i niepełnych wypowiedzi,
- rozpoznawanie intencji ucznia,
- reagowanie na znaczenie wypowiedzi, a nie wyłącznie słowa-klucze,
- utrzymywanie aktualnego tematu,
- naturalne przechodzenie między tematami,
- reagowanie na odpowiedź ucznia przed zadaniem kolejnego pytania,
- unikanie powtarzania tego samego pytania,
- unikanie zapętleń,
- wykrywanie, że pytanie zostało już zadane,
- wykrywanie, że uczeń już udzielił odpowiedzi,
- rozpoznawanie zmiany tematu przez ucznia,
- zadawanie naturalnych pytań uzupełniających,
- kontrolowanie długości wypowiedzi Nele,
- dostosowanie języka do poziomu ucznia,
- delikatne poprawianie błędów,
- pomaganie w rozwijaniu krótkiej odpowiedzi w zdanie wtedy, gdy ma to wartość dydaktyczną,
- akceptowanie naturalnych krótkich odpowiedzi wtedy, gdy pełne zdanie nie jest potrzebne.

Conversation Engine nie może być zbiorem setek sztywnych dialogów:

`jeżeli uczeń mówi X → Nele odpowiada Y`.

Powinien rozumieć **stan i znaczenie rozmowy**.

---

# 4. TEMAT ROZMOWY TO DANE, NIE NOWY SILNIK

Nie twórz osobnego Conversation Engine dla:

- pracy,
- pogody,
- jedzenia,
- rodziny,
- zakupów,
- hotelu,
- restauracji,
- podróży,
- czasu wolnego,
- zdrowia,
- transportu itd.

Tematy powinny dostarczać przede wszystkim:

- słownictwo,
- przykładowe pytania,
- intencje,
- możliwe kierunki rozmowy,
- przydatne konstrukcje,
- cele komunikacyjne.

Wspólny Conversation Engine powinien umieć z tych danych korzystać.

Dzięki temu przyszły temat, którego jeszcze nie stworzyliśmy, powinien móc korzystać z istniejącej inteligencji rozmowy.

---

# 5. KRÓTKIE ODPOWIEDZI MUSZĄ BYĆ ROZUMIANE GLOBALNIE

Nele powinna rozumieć wypowiedzi takie jak:

`gut`

`schlecht`

`Arbeit`

`Pizza`

`Polen`

`8`

`heute`

`ja`

`nein`

`müde`

w kontekście aktualnego pytania.

Krótka odpowiedź nie oznacza automatycznie błędu.

System powinien ustalić:

**Co Nele zapytała? → Co uczeń odpowiedział? → Co ta odpowiedź znaczy w aktualnym kontekście? → Czy potrzebna jest pomoc językowa? → Jak naturalnie kontynuować?**

---

# 6. NIE POPRAWIAJ MECHANICZNIE KAŻDEJ ODPOWIEDZI

Nele jest nauczycielką, ale rozmowa nie może wyglądać jak ciągły test.

System powinien rozróżniać:

- błąd utrudniający komunikację,
- błąd gramatyczny,
- drobną niedoskonałość,
- naturalną krótką odpowiedź,
- odpowiedź poprawną znaczeniowo,
- sytuację, w której warto nauczyć pełnego zdania.

Nie każda krótka odpowiedź wymaga:

`Du kannst sagen: ...`

Pomoc ma pojawiać się wtedy, kiedy rzeczywiście pomaga uczniowi zrobić kolejny krok.

---

# 7. ADAPTACYJNA POMOC MA BYĆ WSPÓLNA

Jeżeli uczeń potrzebuje pomocy, korzystaj ze wspólnego mechanizmu:

**samodzielna odpowiedź**

→ prostsze pytanie

→ wybór

→ początek zdania

→ prosty model

→ powtórzenie modelu.

Nie ujawniaj pełnej odpowiedzi zbyt wcześnie.

Jeżeli uczeń zaczyna odpowiadać poprawnie, **natychmiast zmniejszaj poziom pomocy**.

Ten mechanizm powinien działać również w przyszłych lekcjach i przyszłych scenariuszach.

---

# 8. PAMIĘĆ MA BYĆ WSPÓLNA

Jeżeli Nele nauczy się czegoś istotnego o uczniu lub jego nauce, inne odpowiednie części systemu powinny móc z tego skorzystać.

Dotyczy to między innymi:

- imienia,
- poziomu,
- poznanego słownictwa,
- typowych błędów,
- trudnych konstrukcji,
- sukcesów,
- historii powtórek,
- potrzebnego poziomu pomocy,
- postępu.

Nie twórz oddzielnych, niespójnych pamięci dla każdego modułu, jeżeli informacja należy do wspólnego Learner Model.

---

# 9. PRZYSZŁE LEKCJE I ROZMOWY MUSZĄ DZIEDZICZYĆ INTELIGENCJĘ

Każdy nowy mechanizm projektuj tak, aby mogły z niego korzystać:

- istniejące lekcje A1,
- kolejne lekcje A1,
- przyszłe A2,
- przyszłe poziomy,
- dialogi,
- scenariusze sytuacyjne,
- nowe tematy rozmów,
- przyszłe funkcje Nele.

Nie zakładaj konkretnego numeru lekcji ani konkretnego tematu.

---

# 10. ZERO NIEPOTRZEBNEGO HARDCODINGU

Unikaj rozwiązań:

`if lesson == 2`

`if answer == "Polen"`

`if topic == "weather"`

`if user == "Pizza": response = ...`

jeżeli można zastosować:

- wspólną logikę,
- konfigurację,
- metadane,
- stan rozmowy,
- dane lekcji,
- dane tematu,
- Learner Model.

Hardcoding jest dopuszczalny tylko wtedy, gdy istnieje rzeczywiście wyjątkowa sytuacja dydaktyczna lub językowa.

---

# 11. NAJPIERW SPRAWDŹ ISTNIEJĄCĄ ARCHITEKTURĘ

Przed stworzeniem nowego modułu:

1. sprawdź istniejące silniki,
2. znajdź mechanizm odpowiedzialny za tę funkcję,
3. sprawdź, czy można go rozszerzyć,
4. nie twórz równoległego silnika wykonującego tę samą pracę.

Jeżeli istnieje wspólna warstwa — **rozszerz ją**.

Nie kopiuj jej do konkretnej lekcji lub dialogu.

---

# 12. OBOWIĄZKOWY TEST PRZYSZŁEGO PRZYPADKU

Każdy nowy globalny mechanizm musi zostać przetestowany również na przykładzie, którego nie użyto podczas jego implementacji.

Przykład:

Jeżeli mechanizm powstał dla:

`Polen → Ich komme aus Polen.`

przetestuj:

`Kaffee → Ich möchte einen Kaffee.`

oraz np.:

`Berlin → Ich fahre morgen nach Berlin.`

Dla Conversation Engine analogicznie:

Jeżeli mechanizm powstał podczas rozmowy o pracy, przetestuj go również na niepowiązanym temacie, np. jedzeniu lub czasie wolnym.

Mechanizm, który działa wyłącznie dla przykładu wykorzystanego podczas implementacji, **nie jest jeszcze mechanizmem globalnym**.

---

# 13. TESTUJ DŁUŻSZĄ ROZMOWĘ

Nie testuj wyłącznie pojedynczych odpowiedzi.

Sprawdź również dłuższą sesję:

**Nele → uczeń → Nele → uczeń → Nele → uczeń...**

Test powinien wykrywać:

- powtarzanie pytań,
- utratę kontekstu,
- zapętlenia,
- niepotrzebne poprawianie,
- zbyt szybkie zmiany tematów,
- zbyt długie wypowiedzi Nele,
- niewłaściwy poziom języka,
- brak reakcji na wcześniejszą odpowiedź ucznia.

---

# 14. ZACHOWAJ ROZDZIELENIE TRYBÓW

Globalna architektura może być współdzielona, ale różne tryby Nele mogą mieć różne cele.

Przykładowo:

**📚 Mit dem Kurs üben**

większy nacisk na cel dydaktyczny, konstrukcję docelową, ćwiczenie i postęp.

**☕ Frei sprechen**

większy nacisk na naturalną rozmowę, płynność, kontekst i swobodną komunikację.

Nie kopiuj całych silników między trybami.

Współdzielaj podstawowe możliwości, ale pozwól polityce danego trybu zdecydować, jak z nich korzystać.

---

# 15. WYJĄTKI LOKALNE

Logika lokalna jest dozwolona, gdy wynika z rzeczywiście wyjątkowego celu lekcji lub scenariusza.

W takim przypadku:

- wyjaśnij, dlaczego globalny mechanizm nie wystarcza,
- ogranicz wyjątek do minimum,
- nie kopiuj całego globalnego mechanizmu,
- sprawdź, czy wyjątek nie powinien jednak zostać przedstawiony jako konfiguracja.

---

# 16. KRYTERIUM ZAKOŃCZENIA PRZEBUDOWY

Nie uznawaj przebudowy za zakończoną tylko dlatego, że aktualny przykład działa.

Przed zakończeniem sprawdź:

1. Czy mechanizm znajduje się we właściwej wspólnej warstwie?
2. Czy nie powstała druga implementacja tej samej funkcji?
3. Czy nie zależy niepotrzebnie od konkretnej lekcji?
4. Czy nie zależy niepotrzebnie od konkretnego tematu rozmowy?
5. Czy przyszłe lekcje mogą z niego korzystać?
6. Czy przyszłe dialogi i tematy mogą z niego korzystać?
7. Czy działa na nowym, niehardcodowanym przykładzie?
8. Czy działa w dłuższej rozmowie?
9. Czy pamięta kontekst?
10. Czy nie powoduje zapętleń?
11. Czy pomoc zmniejsza się po sukcesie?
12. Czy istniejące funkcje nadal działają?
13. Czy testy jednostkowe, regresyjne i E2E przechodzą?

Jeżeli któryś z istotnych punktów nie jest spełniony, najpierw sprawdź, czy architekturę można jeszcze uogólnić.

---

# 17. ZASADA KOŃCOWA

Każda większa przebudowa Nele powinna pozostawić po sobie **nową zdolność całego systemu**, a nie wyłącznie poprawiony pojedynczy przykład.

Po zakończeniu pracy powinno być możliwe powiedzenie:

**„Od teraz Nele potrafi X globalnie.”**

zamiast:

**„Od teraz Nele potrafi X tylko w Lektion 2.”**

# CEL

Nele ma rozwijać się jako jeden spójny system:

**Learner Model + Teaching Engine + Conversation Engine + pamięć + treści lekcji i tematów.**

Nowe lekcje, dialogi i tematy, które powstaną w przyszłości, powinny automatycznie korzystać z wcześniej zbudowanej inteligencji Nele albo wymagać jedynie prostej konfiguracji — **bez ponownego programowania tych samych zachowań.**
