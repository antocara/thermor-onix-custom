# AGENT GUIDELINES & RESTRICTIONS

## ⛔ STRICT REPOSITORY & PUBLISHING POLICY (MANDATORY)

1. **NO AUTOMATIC PUSH OR PUBLISHING:**
   - The agent **MUST NEVER** execute `git push`, create or push git tags to remote, or publish GitHub Releases without **explicit, direct user confirmation**.
   - Do **NOT** publish releases, trigger remote webhooks, or push commits to any remote repository automatically under any circumstances.
   - Any remote publishing operation requires the user to explicitly say: *"haz el push"*, *"publica la release"* or an equivalent clear confirmation in the prompt.

2. **LOCAL WORK ONLY BY DEFAULT:**
   - All code development, testing, local git commits, file structuring, and linting must remain strictly local until the user requests remote synchronization.

3. **CONVENTIONAL COMMITS MANDATORY:**
   - All Git commit messages **MUST** strictly follow the [Conventional Commits specification](https://www.conventionalcommits.org/) (v1.0.0).
   - Structure: `<type>(<scope>): <description>` (e.g., `fix(switch): ...`, `feat(water_heater): ...`, `chore: ...`).
   - Standard types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, `revert`.

4. **RELEASE & VERSIONING PROTOCOL (MANDATORY):**
   - Whenever preparing a new version or release:
     1. **Update Manifest Version:** The agent **MUST** update the `"version"` field in `custom_components/thermor_onix_custom/manifest.json` before tagging.
     2. **Version Bump Commit Format:** The commit updating `manifest.json` **MUST** follow Conventional Commits:
        `chore(release): bump version to vX.Y.Z` (or `chore: bump version to vX.Y.Z`).
     3. **Directory Synchronization:** Ensure `manifest.json` and integration files are completely synchronized between `c:\Users\antoc\Proyectos\thermor-onix-custom` and `c:\Users\antoc\Proyectos\Home Assistant`.
     4. **Tagging & Publishing:** Only tag (`git tag vX.Y.Z`) and push (`git push origin vX.Y.Z`) after the commit has been created and the user explicitly orders: *"haz el push"* or *"publica la release"*.

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
