# Multilingual QA Test Plan

The novelty is treated as **Multilingual Requirement Intelligence**, not simple translation.

Expected pipeline:

User language -> language detection -> meaning-preserving translation ->
technical requirement normalization -> user confirmation -> Python code generation ->
syntax validation + safety checks -> explanation in preferred language.

## Evaluation criteria

For each multilingual test case evaluate:
- Translation correct?
- Technical meaning preserved?
- Normalized requirement correct?
- Generated code matches intent?
- Python syntax valid?
- Functional output correct?
- Explanation understandable in requested language?
- Safety behavior correct?

## Multilingual Functional Accuracy

Multilingual Functional Accuracy =
correct translation-to-code results / total multilingual test cases * 100

Do not enter results until actual testing has been performed.
