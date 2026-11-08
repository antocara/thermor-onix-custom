# AGENT GUIDELINES & RESTRICTIONS

## ⛔ STRICT REPOSITORY & PUBLISHING POLICY (MANDATORY)

1. **NO AUTOMATIC PUSH OR PUBLISHING:**
   - The agent **MUST NEVER** execute `git push`, create or push git tags to remote, or publish GitHub Releases without **explicit, direct user confirmation**.
   - Do **NOT** publish releases, trigger remote webhooks, or push commits to any remote repository automatically under any circumstances.
   - Any remote publishing operation requires the user to explicitly say: *"haz el push"*, *"publica la release"* or an equivalent clear confirmation in the prompt.

2. **LOCAL WORK ONLY BY DEFAULT:**
   - All code development, testing, local git commits, file structuring, and linting must remain strictly local until the user requests remote synchronization.

---

## 🛠️ PROJECT ARCHITECTURE & DEVELOPMENT RULES

1. **Home Assistant Custom Components Standards:**
   - Follow official Home Assistant Core integration standards.
   - Use `DataUpdateCoordinator` for unified polling.
   - Always derive dynamic entity state from the live coordinator data (`self.device`), avoiding stale startup snapshots.
   - Provide optimistic state updates for UI switches to eliminate visual flicker.

2. **Language & Documentation Conventions:**
   - **Code files (`.py`):** 100% in English (PEP 257 docstrings, comments, log messages, and internal identifiers).
   - **User-facing strings (`translations/`):** Bilingual support (Spanish `es.json` and English `en.json`).
   - **Repository Documentation:**
     - `README.md` in English (with prominent top link to Spanish version).
     - `README_es.md` in Spanish (with top link to English version).
     - `CONTRIBUTING.md` bilingual in both English and Spanish.
   - **Author / Copyright:** Antonio Carabantes.
