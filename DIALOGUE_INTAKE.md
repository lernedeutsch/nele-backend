# NELE — DIALOGUE INTAKE FORMAT

This is the only format needed when supplying new dialogue content.

## 1. What you send

You may send either:

### A. Finished dialogue text

Example:

Mia: Hallo! Woher kommst du?
Du: Ich komme aus Polen.
Mia: Wo wohnst du?
Du: Ich wohne in Heidelberg.

### B. Structured dialogue

Use the template below when you already know the learning metadata.

---

## 2. Copy-and-use template

```text
DIALOGUE

Title: ...
Level: A1
Lesson: ...
Section: ...
Topic: ...
Situation: ...
Register: informal

Learning goals:
- ...

Grammar:
- ...

Vocabulary:
- ...

Slots:
- country: ...
- name: ...

Allowed variations:
- change_country
- change_name

Forbidden variations:
- combine_unrelated_topics
- mix_formal_and_informal

Next allowed topics:
- ...

Turns:

NELE:
[exact sentence]

STUDENT:
Expected intent: ...
Expected answer: ...
Accepted variants:
- ...
- ...

Common errors:
- ...

NELE:
[exact sentence]

STUDENT:
Expected intent: ...
Expected answer: ...
Accepted variants:
- ...

Completion:
...

END DIALOGUE
```

## 3. What may be omitted

If only a finished dialogue is supplied, the importer may safely create technical structure such as:

- dialogue ID
- normalized roles
- basic turn structure
- accepted-pattern container
- default safety limits

It must NOT invent:

- learning goals
- grammar targets
- vocabulary lists
- pedagogical claims
- new dialogue content

Missing pedagogical information remains missing.

## 4. What the system does automatically

The submitted dialogue goes through:

RAW
→ NORMALIZE
→ SEMANTIC STRUCTURE
→ SLOT CHECK
→ VALIDATION
→ GOLDEN TESTS
→ CANDIDATE
→ ACTIVE
→ DIALOGUE ENGINE

A rejected dialogue never enters active knowledge.

## 5. Required tests for every new dialogue

The system must verify:

1. canonical correct answer
2. natural correct variant
3. short correct answer
4. minor learner error
5. unrelated answer
6. slot variation
7. person variation, when allowed
8. logical continuation
9. correct completion
10. anti-loop behavior

## 6. Important rule for natural German

The dialogue content should contain German that a learner can actually use in everyday life.

Prefer:

- short sentences
- natural spoken German
- common expressions
- one clear question at a time
- realistic situations

Avoid:

- artificial textbook sentences
- unnecessarily long teacher messages
- multiple questions packed into one turn
- unnatural synonyms added only for variety

## 7. How to add 20 dialogues

Do NOT create 20 separate pieces of logic.

Send one batch:

DIALOGUE 1
...
DIALOGUE 20

The batch importer validates each item separately.

A bad item is rejected with its reason.

A valid item can proceed through the candidate gate.

## 8. What the user should see

For every batch, the system should produce:

ACCEPTED
- dialogue ID
- topic
- lesson
- status

REJECTED
- dialogue ID
- exact reason
- field/turn causing the problem

ACTIVATED
- dialogue IDs promoted to active knowledge

## 9. Golden rule

New dialogue content changes WHAT Nele knows.

It must never silently change HOW Nele behaves.

HOW Nele behaves remains in the global Dialogue Engine.
