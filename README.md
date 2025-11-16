# Codex-test
Testing how codex works

## Graphic design portfolio site overview
This repository contains a single-page portfolio built for graphic designer **Aria Lane**. The site is composed of two files: `index.html` for the markup and `styles.css` for all visual styling. It is a static site (no build tools or JavaScript) that can be opened directly in a browser.

### Page structure (`index.html`)
* **Header navigation** — A sticky header with the designer’s name and anchor links to each section.
* **Hero** — Introductory copy, call-to-action buttons, and a featured project card set against animated gradient blobs.
* **Selected work** — Three project cards with animated gradient thumbnails, titles, and descriptions.
* **Capabilities** — A muted background section with a grid of service cards describing brand, campaign, and print offerings.
* **About** — Bio copy alongside a stat card highlighting years of experience, project count, and disciplines.
* **Contact** — A two-column layout with a contact form and supporting copy encouraging inquiries.
* **Footer** — Brand statement plus external links for email, Dribbble, and Behance.

### Visual design (`styles.css`)
* **Color system & typography** — Neon-inspired palette defined as CSS variables and the “Space Grotesk” typeface for a futuristic feel.
* **Layout** — Reusable `.container` widths, responsive CSS Grid layouts for the hero, work, services, contact, and footer sections, and a sticky header with backdrop blur.
* **Components** — Gradient animated thumbnails, glassy cards with subtle borders/shadows, pill buttons (primary gradient and ghost styles), and stat/service cards.
* **Effects & animation** — Soft glow background gradients (`--gradient`), shifting background animations for work thumbnails, and a floating animation for the hero blob to keep the page lively.
* **Responsive behavior** — Media queries collapse the navigation, adjust hero spacing, and stack flex/grid layouts on smaller screens.

### How to view
Open `index.html` in any modern browser. No additional setup is required because all styling lives in `styles.css` and fonts are loaded from Google Fonts.
