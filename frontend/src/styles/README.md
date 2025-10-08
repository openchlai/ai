UI Style System

This folder defines the unified styling for the app:

- tokens.css: Design tokens (colors, spacing, radius, shadows, fonts). Theme by toggling html[data-theme].
- components.css: Global, reusable component classes: .btn, .input, .card, .modal*, and form helpers.

Usage examples

- Buttons:
  - <button class="btn btn--primary btn--md">Save</button>
  - <button class="btn btn--secondary btn--sm">Cancel</button>

- Inputs:
  - <label class="form-label" for="name">Name</label>
  - <input id="name" class="input" placeholder="Enter name" />
  - <div class="form-hint">First and last</div>

Vue Base Components
- Prefer <BaseButton> and <BaseInput> in new code for accessibility and consistency.

Theming
- Switch theme by setting document.documentElement.dataset.theme = 'dark' | 'light'.


