# ==========================================
# NELE – WORTSCHATZLOGIK
# ==========================================

from brain.logic.vocabulary_modules.helpers import (
    clean_vocabulary_word,
    display_vocabulary_word,
    remember_vocabulary_word
)

from brain.logic.vocabulary_modules.meaning import (
    extract_meaning_word,
    answer_vocabulary_question
)

from brain.logic.vocabulary_modules.examples import (
    answer_vocabulary_example
)

from brain.logic.vocabulary_modules.usage import (
    extract_usage_word,
    is_vocabulary_usage_follow_up,
    answer_vocabulary_usage
)

from brain.logic.vocabulary_modules.article import (
    extract_article_word,
    is_article_follow_up,
    answer_vocabulary_article
)

from brain.logic.vocabulary_modules.plural import (
    extract_plural_word,
    is_plural_follow_up,
    answer_vocabulary_plural
)

from brain.logic.vocabulary_modules.similar import (
    answer_similar_vocabulary_word
)

from brain.logic.vocabulary_modules.difference import (
    answer_vocabulary_difference_follow_up,
    answer_explicit_vocabulary_difference
)

from brain.logic.vocabulary_modules.opposite import (
    extract_opposite_word,
    is_opposite_follow_up,
    answer_vocabulary_opposite
)

from brain.logic.vocabulary_modules.explanation import (
    is_simple_explanation_request,
    answer_simple_explanation
)
