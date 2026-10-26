I am the QA, testing, integration-support, and technical-documentation member of an AI-powered Python code-generation project.

IMPORTANT CONTEXT:
- My teammates are still developing the main application.
- I have already completed Phase 1 QA infrastructure.
- Do NOT modify, rewrite, or assume unfinished teammate implementation.
- Do NOT invent bugs, results, technologies, supported languages, function names, APIs, or passing tests.
- Do NOT create fake PASS results.
- Do not execute dangerous generated code.
- My current QA project already contains testing_report.xlsx, BUG_TRACKER.xlsx, tests/, docs/, README.md, requirements.txt, .env.example, and .gitignore.

NEW PROJECT NOVELTY:
We are adding "Multilingual Requirement Intelligence" (Bhasha2Code).
Expected flow:
User requirement in Kannada/Hindi/Urdu/English/mixed language
-> language detection
-> meaning-preserving translation
-> technical requirement normalization
-> user review/confirmation
-> Python code generation
-> safety checker + syntax validator
-> code and explanation in the user's preferred language.

The novelty is NOT merely translation. QA must verify preservation of technical meaning and the complete translation-to-code pipeline.

TASK:
Update my existing QA infrastructure to cover this novelty WITHOUT modifying the unfinished development modules.

1. Update testing_report.xlsx:
Add/extend fields for:
- Input Language
- Expected English Meaning
- Translation Correct?
- Technical Meaning Preserved?
- Normalized Requirement Correct?
- Generated Code Relevant?
- Syntax Valid?
- Output Works?
- Explanation Clear?
- Safety Check
- Result
- Bug ID
- Remarks

Keep existing general test cases. Add at least 10 multilingual cases covering Kannada, Hindi, Urdu, English, and mixed-language input. Do not enter actual results.

2. Create:
data/multilingual_test_cases.csv
with columns:
Test ID, Input Language, Requirement Entered, Expected English Meaning, Expected Technical Meaning, Status
Use Pending as the initial status.

3. Create/update these QA test skeletons:
tests/test_translation.py
tests/test_normalization.py
tests/test_multilingual_flow.py
tests/test_integration.py

They must contain placeholder/TODO tests only where real implementation is unavailable. Do not invent imports or function names.

4. Update docs:
- docs/multilingual_testing.md
- docs/PHASE_2_CHECKLIST.md
- docs/QA_HANDOVER.md
- docs/limitations.md
- docs/screenshot_checklist.md
- docs/demo_checklist.md

5. Update README.md to describe the novelty, but distinguish TARGETED/PLANNED languages from VERIFIED supported languages.

6. Keep requirements.txt conservative. Include pytest if appropriate, but do not add translation libraries until the development team confirms whether they use an API or a local model.

7. Keep .env.example free of real secrets.

8. Add the following QA metrics:
- Translation accuracy
- Technical meaning preservation
- Normalization accuracy
- Code-intent preservation
- Syntax validity
- Functional correctness
- Explanation-language correctness
- Safety-blocking success
- Multilingual Functional Accuracy = correct translation-to-code results / total multilingual test cases * 100

9. Safety testing:
Include multilingual unsafe requests, but never execute them. Verify only that the system flags/warns/blocks them.

10. Do not modify generator.py, app.py, translator.py, language_detector.py, requirement_normalizer.py, validator.py, safety_checker.py, explanation_translator.py, or other teammate implementation files unless they already exist and I explicitly ask you to modify them.

11. At the end, print a complete summary of:
- files created
- files modified
- files intentionally not touched
- what remains pending until teammate implementation arrives.

The final QA package should be ready for Phase 2 integration testing once the development team hands over the actual implementation.
