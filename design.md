# D&D Tracker Web App - Design Specification

This document defines the design system for the D&D Tracker web app. The design draws inspiration from **D&D Beyond**’s dark fantasy aesthetic while keeping implementation simple using **Bootstrap**, **vanilla CSS/JS**, **Font Awesome**, and **Google Fonts**.

---

## 🎨 Color Palette

**Primary Palette** (inspired by D&D Beyond):
- **Dark Background**: `#121212` (main app background)
- **Dark Gray**: `#1E1E1E` (cards, panels, secondary background)
- **Light Gray**: `#2D2D2D` (hover states, table row backgrounds)
- **Accent Red**: `#D63636` (buttons, highlights, active states)
- **Muted Red**: `#8B2D2D` (hover states, subtle accents)
- **White**: `#FFFFFF` (primary text)
- **Off-White / Light Gray**: `#CCCCCC` (secondary text)

**Utility Colors:**
- Success: `#2ECC71`
- Warning: `#F1C40F`
- Danger: `#E74C3C`
- Info: `#3498DB`

---

## 🔤 Typography

Use **Google Fonts**:
- **Headings**: [Cinzel](https://fonts.google.com/specimen/Cinzel) (fantasy, serif style)
- **Body**: [Roboto](https://fonts.google.com/specimen/Roboto) (clean, modern, sans-serif)

**Font Weights**:
- Headings: 700
- Subheadings: 500
- Body: 400

**Examples:**
```css
font-family: 'Cinzel', serif; // for h1-h4
font-family: 'Roboto', sans-serif; // for body text
```

---

## 🖼️ Layout & Components

### Navbar
- Dark background (`#1E1E1E`)
- Accent red hover/active link underline
- Font Awesome icons for quick navigation
- Sticky at top

### Sidebar (optional)
- Collapsible, dark gray background
- Red highlights for active section

### Cards (Bootstrap `.card`)
- Background: `#1E1E1E`
- Border: `1px solid #2D2D2D`
- Rounded corners: `0.5rem`
- Drop shadow: subtle (`0 2px 4px rgba(0,0,0,0.6)`)

### Tables (for character stats, initiative, etc.)
- Dark background rows alternating with slightly lighter gray
- Header row: bold, accent underline
- Hover row: background `#2D2D2D`

### Buttons
- **Primary**: Red background, white text
  ```css
  .btn-primary {
    background-color: #D63636;
    border: none;
  }
  .btn-primary:hover {
    background-color: #8B2D2D;
  }
  ```
- **Secondary**: Dark gray background, light gray text
- Rounded corners, Bootstrap sizing

### Modals
- Background: `#1E1E1E`
- Border: `1px solid #2D2D2D`
- Accent red close button

---

## 🎭 Icons

Use **Font Awesome** for icons:
- Dice: `fa-dice-d20`
- Characters: `fa-user`
- Campaigns: `fa-map`
- Items: `fa-sword`
- Settings: `fa-cog`

---

## 🌌 Visual Style
- Dark fantasy aesthetic, but modern and minimal.
- Use **red accents** sparingly for emphasis.
- Rounded corners & subtle shadows to avoid a flat look.
- Maintain high contrast for readability.

---

## 📱 Responsiveness
- Bootstrap grid system for mobile-first layout.
- Navbar collapses into a hamburger menu on mobile.
- Cards stack vertically on small screens.

---

## ✨ Example UI Flow
1. **Dashboard** → List of campaigns/sessions (cards with dice/map icons).
2. **Campaign View** → Tabs for characters, sessions, notes.
3. **Session Tracker** → Initiative table, notes panel, active combat tracker.
4. **Character View** → Character stats in a card layout.

---

## 📂 File Structure
```
/css
  styles.css   // custom overrides
/js
  scripts.js   // app logic
index.html
campaign.html
character.html
```

---

## ✅ Implementation Notes
- Extend Bootstrap with minimal custom CSS overrides.
- Use utility classes (`text-light`, `bg-dark`, `p-3`, etc.) wherever possible.
- Keep CSS modular: typography, buttons, layout, theme.
- Ensure color contrast accessibility (WCAG AA).

