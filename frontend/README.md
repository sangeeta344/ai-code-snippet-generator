# CodeForge AI — Frontend / UI Developer Workspace

> **Natural Language → Production Python**  
> AI-Powered Python Code Generator  
> **Integrated Full-Stack Application**

---

## 🚀 How to Run the Application

From the project root (`D:\Desktop\TCS hackthon`):

```bash
python -m streamlit run frontend/app.py
```

The application will launch in your browser at `http://localhost:8501`.

---

## 🎨 Design & Visual Aesthetic

- **Theme:** Enterprise Blue (`#0066B3`) + Deep Navy (`#0B1F33`) + Orange AI Accents (`#FF7A00`) on subtle micro-dot canvas (`#F3F6F9`).
- **Panels:** Glassmorphism cards with subtle borders and hover depth.
- **Typography:** Inter font family with Fira Code for code blocks and snippets.
- **Pipeline Tracker:** Visual 5-step status progression in the sidebar.

---

## 🧩 User Flow & Feature Set

1. **Hero Section:**
   - Brand banner: `CODEFORGE AI | Natural Language → Production Python`
   - Real-time engine status pill (indicates whether running in Live AI or Demo Mode).
2. **Interactive Sidebar:**
   - 5-stage visual execution pipeline:
     1. Requirement → 2. Analysis → 3. Context Retrieval → 4. Code Generation → 5. Validation
   - Bottom status card showing active engine and model details.
3. **Requirement Input Card:**
   - Quick Requirement Presets selector (Prime checker, CSV salary, Palindrome, Fibonacci, etc.).
   - Natural language input text area.
   - Target Programming Language selector (Python 3.10+, Async, Strict Types).
   - Additional Constraints input field (optional).
   - Primary `⚡ Generate Code` and `🔄 Reset` buttons.
   - Empty input validation guard with user-friendly error message.
4. **Live Execution Pipeline:**
   - Animated progress tracking showing AST analysis, TF-IDF RAG retrieval, code synthesis, syntax checking, and security screening.
5. **Requirement Analysis (6 Cards):**
   - **Intent:** Primary goal of the requirement.
   - **Inputs:** Expected input formats and parameters.
   - **Outputs:** Return values and generated artifacts.
   - **Constraints:** Technical boundaries and algorithmic time/space limits.
   - **Edge Cases:** Handled boundary conditions.
   - **Libraries:** Verified standard library and package imports.
6. **Retrieved Context (Knowledge Base Matches):**
   - TF-IDF similarity scores with progress bars matching curated reference patterns.
7. **Generated Python Code Editor:**
   - High-contrast dark code editor (`#0D1824`) with line numbers and syntax highlighting.
   - Direct `⬇ Download Python Code` and `📋 Copy to Clipboard` buttons.
8. **Explanation Section:**
   - Architectural walkthrough explaining the chosen algorithm, logic, and assumptions.
9. **Verification Cases:**
   - Structured cards displaying sample inputs and expected outputs.
10. **Automated Unit Tests:**
    - Self-contained, runnable `unittest`-compatible test suite for the generated function.
11. **Validation & Audit Summary:**
    - 4 safety and integrity checks: Python AST Syntax, Safety Screening, AST Structure, Edge Case Handling.
    - Generation metrics: Latency, Context Count, Validation Status, Confidence Score.

---

## 🔌 Backend Integration

The frontend connects directly to `backend.generate()`:

```python
import backend

result = backend.generate(
    requirement=requirement_text,
    constraints=constraints_text,
    language=selected_language,
)
```

The returned dictionary conforms to the established schema, complete with AST validation, safety screening, RAG context, explanation, examples, and test cases.
