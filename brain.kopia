import random


class Brain:

    def __init__(self):
        self.level = "A1"

    def wybierz_pytanie(self, fragen):
        return random.choice(fragen)
    
    def odpowiedz_na_tekst(self, tekst, memory):
        tekst = tekst.lower().strip()

        if "hallo" in tekst or "guten tag" in tekst:
            return "Hallo! Schön, dass Sie wieder da sind."

        if "wie geht" in tekst:
            return "Mir geht es gut. Und Ihnen?"

        if "ich heiße" in tekst or "ich heisse" in tekst:
            memory.save_answer("", tekst)
            return "Sehr gut. Ich merke mir Ihren Namen."

        if "ich komme aus" in tekst:
            memory.save_answer("", tekst)
            return "Sehr gut. Ich merke mir, woher Sie kommen."

        if "ich wohne in" in tekst:
            memory.save_answer("", tekst)
            return "Sehr gut. Ich merke mir, wo Sie wohnen."

        if "ich arbeite" in tekst:
            memory.save_answer("", tekst)
            return "Sehr gut. Ich merke mir, wo Sie arbeiten."

        if "was weißt du" in tekst or "was weisst du" in tekst:
            return memory.summary()

        if "ende" in tekst or "tschüss" in tekst or "tschuess" in tekst:
            return "ENDE"

        return "Interessant. Bitte sagen Sie den Satz noch einmal einfacher auf Deutsch."
