# Frontend Validation

The workspace uses semantic navigation/sections, labeled inputs, native selects/ranges/checkboxes, button accessible names, live report/error regions, reduced-motion handling and focus-visible outlines. Icons use lucide-react. Responsive mobile navigation scrolls horizontally within its own region; report strings and hashes wrap.

Before release, validate keyboard-only navigation, focus trapping/restoration in account dialogs, screen reader announcements during polling, tab panel semantics, color contrast, long metadata, 320-pixel widths and zoom. Current dialog behavior is a baseline and still needs dedicated accessibility review.

Capture desktop/mobile screenshots from synthetic fixtures; verify image previews load, report panes do not overlap, controls remain operable and browser console/network errors are absent. A build passing does not replace browser interaction or accessibility testing.

The Playwright regression exercises image upload, analysis, sanitization, authorized download and deletion, checks loaded preview pixels and horizontal overflow at 1440/390/320 pixels, and rejects page/console errors. Run `npm --prefix frontend run test:browser` after installing Chromium with `frontend/node_modules/.bin/playwright.cmd install chromium` on Windows. It captures `docs/workspace-desktop.png` and `docs/workspace-mobile.png` from synthetic input. Keyboard, screen-reader and focus-management review remain open.