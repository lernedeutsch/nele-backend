"""LEGACY local CLI orchestration.

Not used by the production Flask application. Production lives in server/app.py.
Kept only for historical/local experiments.
"""

from brain.personality import Personality
from brain.rules import Rules
from brain.brain import Brain
from brain.teacher import Teacher
from memory.student_memory import StudentMemory
from speech.speaker import Speaker
from speech.listener import Listener


def start():
    print("=" * 50)

    nele = Personality()
    nele.introduce()

    print()

    rules = Rules()
    rules.show()

    brain = Brain()
    memory = StudentMemory()
    teacher = Teacher()
    speaker = Speaker()
    listener = Listener()

    fragen = teacher.lesson()

    print()
    print("Brain aktiv.")
    print()

    speaker.speak("Hallo!")
    speaker.speak(memory.summary())
    speaker.speak("Heute machen wir ein kurzes Gespräch.")
    speaker.speak("Zum Beenden schreiben Sie: Ende")

    while True:
        print()
        frage = brain.wybierz_pytanie(fragen)
        speaker.speak(frage)

        tekst = listener.listen()

        antwort = brain.odpowiedz_na_tekst(tekst, memory)

        if antwort == "ENDE":
            speaker.speak("Auf Wiedersehen!")
            break

        speaker.speak(antwort)

    print()
    speaker.speak("Nele erinnert sich:")
    speaker.speak(memory.summary())

    print("=" * 50)
