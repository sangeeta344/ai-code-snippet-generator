# Phase 2 — Integration & Multilingual QA Checklist

## A. Collect development code
- [ ] Get latest Git branch/commit
- [ ] Get completed modules
- [ ] Confirm translator implementation
- [ ] Confirm language detector implementation
- [ ] Confirm requirement normalizer implementation
- [ ] Confirm explanation translator implementation
- [ ] Get latest requirements.txt
- [ ] Confirm environment variables
- [ ] Confirm how to run the application

## B. Local setup
- [ ] Create virtual environment
- [ ] Install dependencies
- [ ] Configure .env
- [ ] Start application successfully

## C. Integration
- [ ] Language detection works
- [ ] Translation works
- [ ] Translation review/edit works
- [ ] Normalization produces structured requirement
- [ ] Generator receives normalized requirement
- [ ] Safety checker receives generated code
- [ ] Syntax validator receives safe code
- [ ] Results reach the UI
- [ ] Explanation can be shown in selected language

## D. Multilingual testing
- [ ] Kannada
- [ ] Hindi
- [ ] Urdu
- [ ] English
- [ ] Mixed-language input
- [ ] Empty input
- [ ] Ambiguous input

## E. Safety testing
- [ ] Unsafe request in English
- [ ] Unsafe request in Kannada
- [ ] Unsafe request in Hindi/Urdu
- [ ] Verify warning/blocking without executing dangerous code

## F. Bug management
- [ ] Record reproducible bugs
- [ ] Assign bugs
- [ ] Developer fixes
- [ ] Retest
- [ ] Close or reopen

## G. Metrics
- [ ] Translation accuracy
- [ ] Technical meaning preservation
- [ ] Normalization accuracy
- [ ] Code-intent preservation
- [ ] Syntax validity
- [ ] Functional correctness
- [ ] Explanation-language correctness
- [ ] Safety-blocking success
