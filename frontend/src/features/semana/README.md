# Semana theme guide

The Semana website is themed at the feature boundary. Shared components under
`src/components/ui` remain neutral; the `.semana-theme` wrapper supplies their
colors, while components in this directory supply the event's distinctive
shape, typography, and decoration.

## Preview period

`/semana` is intentionally a plain, standalone preview placeholder. The full
event pages remain implemented in the `(site)` route group, which keeps their
public URLs unchanged while applying `SemanaShell` only to those pages. During
the preview period, their shared layout redirects every event route back to the
preview. Set `SEMANA_PREVIEW_MODE` to `false` in `config.ts` when those routes
are production-ready, then replace the preview page with the event entry point.

The 2025 preview can be used as visual reference from commit `4ed8a52`. It used
`logo-colorida-symcomp.svg`, `barra-carregamento.svg`, `2025.svg`, `ime-usp.svg`,
and sponsor logos from `public/sc-2025/`. Commit `5c79f87` later added its pixel
particle background. Recover or replace only the assets selected for the new
design; the old sponsor list must not be copied into a new edition.

## Starting a new edition

1. Choose the edition palette and update `.semana-theme` in
   `src/app/styles/globals.css`.
2. Add the edition's shell assets under `public/semana/<year>/`.
3. Update asset paths and accessible names in `components/semana-shell.tsx`.
4. Update the display and body fonts in `fonts.ts`, if the new identity uses
   different fonts.
5. Restyle the feature components only when the new identity changes their
   shape or behavior.
6. Check every Semana route on mobile and desktop, then run the frontend
   verification commands at the end of this guide.

Do not rename the reusable components or create copies such as
`Semana2026Button`. The active edition should replace the current theme. Keep
old assets in their year directory only when an archived edition still uses
them.

## Color contract

Set all of these semantic variables on `.semana-theme`:

| Variable                 | Used for                                    |
| ------------------------ | ------------------------------------------- |
| `--background`           | Page and shell background                   |
| `--foreground`           | Text placed directly on the page background |
| `--card`                 | Cards, dialogs, and form surfaces           |
| `--card-foreground`      | Text inside cards                           |
| `--popover`              | Menus and popovers                          |
| `--popover-foreground`   | Text inside menus and popovers              |
| `--primary`              | Main action or highlight color              |
| `--primary-foreground`   | Text placed on the primary color            |
| `--secondary`            | Secondary action color                      |
| `--secondary-foreground` | Text placed on the secondary color          |
| `--muted`                | Quiet surfaces and placeholders             |
| `--muted-foreground`     | Supporting text                             |
| `--accent`               | Hover and selected states                   |
| `--accent-foreground`    | Text placed on the accent color             |
| `--border`               | Default borders                             |
| `--input`                | Form-control borders                        |
| `--ring`                 | Keyboard focus ring                         |
| `--radius`               | Default corner radius                       |

The current design also has Semana-specific variables:

| Variable            | Used for                         |
| ------------------- | -------------------------------- |
| `--semana-contrast` | Heavy borders and offset shadows |
| `--semana-accent`   | Branded hover surfaces           |
| `--semana-tertiary` | Optional third decorative color  |

Prefer the semantic variables first. Add a `--semana-*` variable only when a
visual role has no semantic equivalent and is reused in more than one place.
Use HSL channels without the `hsl()` wrapper, for example `244 75% 16%`.

## Shell assets

Create this directory for a new edition:

```text
public/semana/<year>/
├── logo-horizontal.svg
├── ime-usp-branca.svg
└── og-image.png              # add when social metadata is enabled
```

The minimum shell contract is:

- `logo-horizontal.svg`: event identity displayed in the header. It should
  work on the chosen header background and include a useful SVG `viewBox`.
- `ime-usp-branca.svg`: institutional footer mark for a dark footer. Rename it
  and update the shell when the design needs a dark version instead.
- `og-image.png`: social sharing image. A practical target is 1200 x 630 px.

Optional decorative illustrations belong in the same year directory, but
only add them when a page actually renders them. Speaker photos and sponsor
logos should live under descriptive subdirectories:

```text
public/semana/<year>/speakers/
public/semana/<year>/sponsors/
public/semana/<year>/illustrations/
```

Use SVG for logos and simple illustrations. Use optimized WebP, AVIF, or PNG
for photographs and raster artwork. Do not embed large base64 images inside
SVG files.

## Components to review

- `components/semana-shell.tsx`: header, navigation, footer, and shell assets.
- `components/semana-button.tsx`: branded border, shadow, casing, and states.
- `components/semana-input.tsx`: branded form-control shape and focus state.
- `components/semana-home.tsx`: edition-specific landing-page composition.
- `fonts.ts`: display and body font definitions.

Pages such as schedule, login, registration, and profile should consume these
components and semantic colors. Avoid placing year names, raw hex colors, or
asset paths inside generic feature components.

## Accessibility checks

- Check foreground/background contrast for normal text and controls.
- Keep a visible keyboard focus ring on every link and control.
- Give meaningful logos an accurate `alt`; decorative images use `alt=""`.
- Verify header and menu behavior at narrow mobile widths.
- Check hover, focus, active, disabled, error, and loading states.
- Do not communicate activity type or form status through color alone.

## Verification

From `frontend/`, run:

```bash
pnpm run format
pnpm run lint
pnpm exec tsc --noEmit
pnpm run build
```

Then inspect at least:

```text
/semana
/semana/inicio
/semana/cronograma
/semana/login
/semana/cadastro
/semana/perfil
```
