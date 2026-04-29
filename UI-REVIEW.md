# UI Review — Meeting Translator

**Audited:** 2026-04-28
**Baseline:** Abstract 6-pillar standards (no UI-SPEC.md present)
**Screenshots:** Not captured (no dev server detected on ports 3000 or 5173)

---

## Pillar Scores

| Pillar | Score | Key Finding |
|--------|-------|-------------|
| 1. Copywriting | 2/4 | UI is entirely in Portuguese; icon-only action buttons lack accessible labels |
| 2. Visuals | 3/4 | Consistent card-based hierarchy; CallOverlay lacks visual content area below the caption bar |
| 3. Color | 3/4 | Token system is solid; 9 hardcoded hex values leak outside the token layer |
| 4. Typography | 2/4 | 17 distinct font sizes across 6 CSS files; no size scale discipline |
| 5. Spacing | 3/4 | rem-based spacing is consistent; a few arbitrary gap values break the rhythm |
| 6. Experience Design | 3/4 | Loading and error states covered; LanguageSelector silently swallows fetch errors |

**Overall: 16/24**

---

## Top 3 Priority Fixes

1. **17 font sizes with no scale** — Users perceive visual noise and the UI feels typographically inconsistent as they move between screens — Collapse to a 5-stop scale: `0.75rem` (xs), `0.875rem` (sm), `1rem` (base), `1.25rem` (lg), `1.5rem` (xl), replacing the ad-hoc values like `0.78rem`, `0.82rem`, `0.95rem`, `1.05rem`, `1.1rem`, `1.2rem`, `1.3rem`, `1.4rem`, `1.8rem`, `2.5rem` into the nearest standardised stop.

2. **Exit button (✕) in CallOverlay has no aria-label** — Screen-reader and keyboard-only users cannot identify the close action in the most critical screen of the app — Add `aria-label="Encerrar tradução"` to `co-exit-btn` in `CallOverlay.jsx:67`, and `aria-label="Fechar URL"` to `sp-btn-remove` in `SpeakerProfile.jsx:92`.

3. **LanguageSelector silently fails on fetch error** — When the languages API is unreachable the loading text disappears and the list is empty with no explanation, blocking the user from knowing what to do — In `LanguageSelector.jsx:16`, add an `error` state in the `.catch()` handler and render an error message with a retry button, mirroring the pattern already used in `Prerequisites.jsx`.

---

## Detailed Findings

### Pillar 1: Copywriting (2/4)

**Language consistency (informational only):** All copy is in Portuguese (`"Verificar novamente"`, `"Escolha o idioma das legendas"`, `"Próximo →"`, etc.), which is internally consistent for a pt-BR product. No generic English labels like "Submit" or "OK" were found.

**Icon-only buttons without accessible labels:**
- `CallOverlay.jsx:67` — `<button className="co-exit-btn">✕</button>` — No `aria-label`. The `✕` character is not exposed with a meaningful name to assistive technology.
- `CallOverlay.jsx:66` — `<button className="co-popup-btn" title="Abrir em janela flutuante">⬆︎</button>` — Has a `title` attribute, which is better than nothing but `title` is not reliably read by all screen readers. Should be supplemented with `aria-label`.
- `SpeakerProfile.jsx:92` — `<button className="sp-btn-remove">✕</button>` — No `aria-label`. The remove action for a URL in the list has no accessible name.

**CTA labels are clear and action-oriented** (`"Continuar →"`, `"Analisar e criar perfil"`, `"Usar perfil e iniciar"`, `"Nova sessão"`). No generic labels found.

**Empty state in SessionSummary:** The `recent_phrases` section only renders when `sessionData?.recent_phrases?.length > 0`. There is no fallback message when the phrase list is empty (e.g., session ended before any translation occurred). The user sees nothing in that section with no explanation. (`SessionSummary.jsx:38`).

**Error message quality:** `SpeakerProfile.jsx:53` sets `setError(e.message)` directly from the thrown error. If the backend returns a generic network error string it may surface raw technical text to the user. Consider mapping to user-friendly messages.

---

### Pillar 2: Visuals (3/4)

**Positive:** All wizard screens (Prerequisites, LanguageSelector, SpeakerProfile, SessionSummary) follow the same centered card pattern with consistent icon + title + subtitle + action hierarchy. This is clear and scannable.

**CallOverlay visual gap:** The `co-page` fills the whole viewport (`position: fixed; inset: 0`) but only the top bar (`co-bar`, `min-height: 72px`) and a slim stats row (`co-stats`) are styled. The remaining ~85% of the screen is a dark semi-transparent void (`rgba(0,0,0,0.88)`). For a dedicated overlay screen this is intentional (meeting content shows behind), but because it is a standalone Electron window — not a transparent overlay — it reads as an empty, incomplete screen. There is no guidance or visual affordance telling the user what the dark area is for. A short instructional hint or the session elapsed timer in the center would resolve this.

**SpeakerProfile processing screen** is well done — the animated stepper provides concrete progress feedback instead of a generic spinner.

**PopupOverlay** is appropriately minimal for its floating-window purpose.

**Icon usage:** Emoji icons (`⏳`, `✅`, `⚠️`, `❌`, `🌐`, `📋`) are used as status indicators throughout. These render inconsistently across platforms/OS versions and do not scale with user font preferences. Replacing with SVG icons or a small icon font would be more robust.

---

### Pillar 3: Color (3/4)

**Token system is well-structured.** `index.css` defines 10 semantic tokens (`--bg`, `--card`, `--card-hover`, `--accent`, `--accent-hover`, `--text`, `--text-muted`, `--success`, `--danger`, `--border`). Semantic naming is appropriate.

**Token violations — hardcoded hex values outside `:root`:**

| File | Line | Value | Should be |
|------|------|-------|-----------|
| `Prerequisites.css` | 125 | `background: #111` | `var(--bg)` or a new `--surface` token |
| `SpeakerProfile.css` | 40 | `background: #111` | `var(--bg)` |
| `SpeakerProfile.css` | 85 | `background: #111` | `var(--bg)` |
| `SpeakerProfile.css` | 147 | `border-color: #555` | `var(--border)` or `var(--card-hover)` |
| `SpeakerProfile.css` | 227 | `background: #111` | `var(--bg)` |
| `SessionSummary.css` | 43 | `background: #111` | `var(--bg)` |
| `SessionSummary.css` | 92 | `background: #111` | `var(--bg)` |
| `CallOverlay.css` | 55 | `color: #818cf8` | Should be `var(--accent)` (this is the indigo-400 tint, not in the token set) |
| `CallOverlay.css` | 150 | `border-color: #555` | `var(--border)` |
| `PopupOverlay.css` | 35 | `color: #f0f0f0` | `var(--text)` |
| `PopupOverlay.css` | 49-50 | `#22c55e` / `#ef4444` | `var(--success)` / `var(--danger)` |

The `#818cf8` in `CallOverlay.css:55` is particularly notable — it is a second accent shade not in the token system. This creates a subtle colour inconsistency on the popup button.

**Accent usage (26 references)** is high but spread appropriately across interactive elements (buttons, selected states, stat values, pills). No decorative-only overuse detected.

**60/30/10 split:** Dark neutral backgrounds carry ~60%, card surfaces ~30%, and accent (indigo) ~10%. The balance is reasonable.

---

### Pillar 4: Typography (2/4)

**17 distinct font sizes** are in use across 6 CSS files. This is the most significant finding in the audit. A well-disciplined scale would use 4–6 stops maximum.

| Size | Usage |
|------|-------|
| `2.5rem` | Page-level emoji icons |
| `1.8rem` | `ss-icon` |
| `1.5rem` | Page `h1` titles |
| `1.4rem` | `ss-title` |
| `1.3rem` | `sp-title`, `sp-avatar` |
| `1.2rem` | `co-modal h2` |
| `1.1rem` | `co-caption`, `sp-stat-value` |
| `1.05rem` | `ss-stat-value` |
| `1rem` | Base / buttons |
| `0.95rem` | `ls-subtitle`, `sp-input`, `co-modal p` |
| `0.9rem` | Subtitles, hints, step labels |
| `0.875rem` | Alert text |
| `0.85rem` | Vocab label, phrase list |
| `0.82rem` | `co-stats`, `sp-url-text` |
| `0.8rem` | Hint text, step dots, pill text |
| `0.78rem` | `pr-alert-hint` |
| `0.75rem` | Stat labels |

The sub-`1rem` range alone has 9 stops (`0.75`, `0.78`, `0.8`, `0.82`, `0.85`, `0.875`, `0.9`, `0.95`). Several of these are imperceptibly close and likely unintentional (e.g., `0.875rem` vs `0.9rem` differ by only 2px at 16px base).

**Font weights** are well controlled: only `500`, `600`, and `700` are used — this is appropriate.

**No line-height inconsistency** found outside of the base `body` default. Where declared (`line-height: 1.5`), values are consistent.

---

### Pillar 5: Spacing (3/4)

**Spacing is primarily rem-based and consistent.** No `px`-based padding or margin rules were found in CSS (hardcoded pixel spacing audit returned empty). Most spacing follows a loosely 0.25rem-increment rhythm.

**Minor inconsistencies:**

- `pr-checklist` gap: `0.65rem` (`Prerequisites.css:46`) — falls outside the clean 0.25rem grid. Likely should be `0.5rem` or `0.75rem`.
- `pr-item` gap: `0.65rem` (`Prerequisites.css:51`) — same issue.
- `sp-card` gap: `1.1rem` (`SpeakerProfile.css:18`) — should be `1rem` or `1.25rem`.
- `sp-spinner` margin-top: `0.5rem` is fine; but the overall card `gap: 1.1rem` breaks from the `1.25rem` used in all other cards.
- `co-stats` font-size `0.82rem` and `sp-url-text` `0.82rem` — the `0.82rem` value is an odd stop that doesn't belong to a standard scale.

**Card max-widths vary** without clear rationale: `440px` (Prerequisites), `420px` (LanguageSelector), `480px` (SpeakerProfile), `500px` (SessionSummary). Standardising to two values (e.g., `440px` for simple cards, `500px` for data-heavy cards) would reduce visual inconsistency across the flow.

---

### Pillar 6: Experience Design (3/4)

**Loading states:** All async operations have loading indicators.
- `Prerequisites.jsx:132` — spinner while checking system
- `LanguageSelector.jsx:27` — "Carregando idiomas..." text
- `SpeakerProfile.jsx:119` — animated spinner with 5-step progress indicator
- `CallOverlay.jsx:61` — inline spinner while waiting for first caption

**Error states:**
- `Prerequisites.jsx:110-117` — full error state with recovery instructions and a "Verificar novamente" button. Well handled.
- `SpeakerProfile.jsx:85` — inline error message on `screen === 'input'`. Works.
- `LanguageSelector.jsx:16` — `.catch(() => setLoading(false))` silently discards the error. The user sees an empty language list with no explanation and the "Próximo" button is still enabled (it would proceed with the default `'pt'` selection). This is a silent failure.
- `CallOverlay` — no error handling for WebSocket disconnection beyond the `co-dot--off` indicator. If the WS fails mid-call, the caption freezes with no user-facing message or retry option.

**Empty states:**
- `SessionSummary` recent phrases: no empty state when `recent_phrases` is absent or empty.
- `SpeakerProfile` URL list: no empty state message — acceptable since the section only appears after adding URLs.

**Confirmation for destructive actions:** The exit button in `CallOverlay` correctly opens a confirmation modal before ending the session. This is good UX for an irreversible action.

**Disabled states:** `LanguageSelector` disables "Próximo" while loading. `SpeakerProfile` disables "Analisar" when `urls.length === 0`. Correct.

**No React ErrorBoundary** detected at the app level. An error in any page component would render a blank screen with no recovery path.

**PopupOverlay** does not handle the case where `sessionId` is null (URL opened directly without params). The WebSocket would connect to `ws://localhost:8000/ws/transcribe/null` and produce an error.

---

## Files Audited

- `frontend/src/App.jsx`
- `frontend/src/index.css`
- `frontend/src/pages/Prerequisites.jsx`
- `frontend/src/pages/Prerequisites.css`
- `frontend/src/pages/LanguageSelector.jsx`
- `frontend/src/pages/LanguageSelector.css`
- `frontend/src/pages/SpeakerProfile.jsx`
- `frontend/src/pages/SpeakerProfile.css`
- `frontend/src/pages/CallOverlay.jsx`
- `frontend/src/pages/CallOverlay.css`
- `frontend/src/pages/SessionSummary.jsx`
- `frontend/src/pages/SessionSummary.css`
- `frontend/src/pages/PopupOverlay.jsx`
- `frontend/src/pages/PopupOverlay.css`
- `frontend/src/hooks/useWebSocket.js` (existence confirmed, content not audited)
- `frontend/src/utils/languages.js` (existence confirmed, content not audited)
