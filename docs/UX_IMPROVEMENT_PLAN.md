# Workout Coach - UX Improvement Plan

## Color Palette

```css
:root {
  /* Primary Palette */
  --muted-teal: #8eb19d;      /* Success, completion, wellness */
  --carbon-black: #1e1b18;    /* Primary text */
  --almond-silk: #eacdc2;     /* Background, subtle fills */
  --persian-blue: #072ac8;    /* Primary actions, links, focus */
  --rust-brown: #a44200;      /* High intensity, warnings, rest days */

  /* Extended Neutrals */
  --gray-600: #4a4543;        /* Secondary text */
  --gray-400: #8a8582;        /* Placeholder, disabled */
  --gray-200: #d4cdc9;        /* Borders, dividers */

  /* Semantic Colors */
  --error-red: #c62828;       /* Form errors, destructive actions */
  --success-green: #2e7d32;   /* Success states (distinct from muted-teal) */

  /* Hover States */
  --persian-blue-hover: #0621a3;
  --muted-teal-hover: #7a9d89;
  --rust-brown-hover: #8a3800;
}
```

---

## Implementation Phases

### Phase 1: Design System Foundation (CRITICAL)
**Status:** In Progress

**Goals:**
- [x] Establish CSS variables for colors, typography, spacing
- [x] Replace all purple (#667eea) with Persian blue (#072ac8)
- [ ] Create shared component patterns (buttons, inputs, cards)
- [ ] Implement consistent focus states across all components
- [ ] Add ARIA landmarks and labels

**Files to Update:**
- [x] `frontend/src/index.css` - CSS variables added
- [x] `frontend/src/App.css` - Tab buttons updated
- [x] `frontend/src/components/ChatInterface.css` - All purple replaced
- [x] `frontend/src/components/StravaImport.css` - Table header updated

---

### Phase 2: Critical UX Fixes (HIGH PRIORITY)
**Status:** Pending

**Goals:**
- [ ] Add loading skeletons to all data-fetching components
- [ ] Improve error handling (remove alerts, add retry buttons, toast notifications)
- [ ] Add empty states with CTAs
- [ ] Implement proper keyboard navigation
- [ ] Fix mobile responsive issues (cards, tables)
- [ ] Add "today" indicator to calendars

**Components to Update:**
- `WeekAheadView.jsx` - Loading skeleton, empty state, today indicator
- `MonthView.jsx` - Today indicator, hover states
- `ChatInterface.jsx` - Typing indicator, remove alerts
- `StravaImport.jsx` - Loading states, responsive tables
- `WorkoutCard.jsx` - Completion animations

---

### Phase 3: Interaction Polish (MEDIUM PRIORITY)
**Status:** Pending

**Goals:**
- [ ] Add smooth transitions to card expansions
- [ ] Implement completion animations (checkmark, confetti)
- [ ] Add hover states to calendar cells
- [ ] Create typing indicator for chat
- [ ] Make welcome examples clickable (auto-fill input)
- [ ] Add tooltips to month view workouts
- [ ] Implement undo toast for completions

**Animation Standards:**
```css
--transition-fast: 150ms ease-in-out;
--transition-normal: 250ms ease-in-out;
--transition-slow: 350ms ease-in-out;
```

---

### Phase 4: Mobile Optimization (HIGH PRIORITY)
**Status:** Pending

**Goals:**
- [ ] Implement swipe gestures for week navigation
- [ ] Convert tables to cards on mobile
- [ ] Add bottom sheet for workout details
- [ ] Optimize touch targets (44px minimum)
- [ ] Add pull-to-refresh
- [ ] Implement 3-day mobile week view

**Breakpoints:**
```css
--mobile: 0-640px
--tablet: 641px-1024px
--desktop: 1025px+
```

---

### Phase 5: Advanced Features (MEDIUM PRIORITY)
**Status:** Pending

**Goals:**
- [ ] Add keyboard shortcuts with guide (? key)
- [ ] Implement plan management interface
- [ ] Add activity filtering/sorting (Strava)
- [ ] Create workout edit modal (replace alert)
- [ ] Add batch actions (complete full week)
- [ ] Implement markdown support in chat

---

### Phase 6: Accessibility Audit (CRITICAL)
**Status:** Pending

**Goals:**
- [ ] Run automated accessibility testing (axe, Lighthouse)
- [ ] Manual screen reader testing
- [ ] Color contrast audit and fixes
- [ ] Keyboard navigation verification
- [ ] Add reduce motion support (`prefers-reduced-motion`)

**WCAG Requirements:**
- AA contrast ratio (4.5:1 for text, 3:1 for large text)
- All interactive elements keyboard accessible
- Focus indicators visible (2px outline minimum)
- ARIA labels for all non-text content

---

## Quick Wins (High Impact, Low Effort)

These can be done immediately without major refactoring:

1. **Add loading skeletons** - Replace "Loading..." text with shimmer animations
2. **Implement focus visible states** - Add `:focus-visible` to all interactive elements
3. **Replace emoji with icons** - Use lucide-react consistently
4. **Add "today" indicator** - Highlight current day in week/month views
5. **Fix error handling** - Remove `alert()` calls, use inline messages
6. **Add empty states with CTAs** - Guide users when no data exists
7. **Improve hover states** - Add subtle scale/shadow on interactive elements

---

## Component-Specific Issues

### App.jsx
- [ ] Replace emoji icons with lucide-react icons
- [ ] Add ARIA role="tablist" to navigation
- [ ] Add keyboard shortcuts (Alt+1, Alt+2, Alt+3)
- [ ] Reduce hover transform from 2px to 1px

### WeekAheadView.jsx
- [ ] Add skeleton loader while fetching
- [ ] Add "Today" badge to current day
- [ ] Show week number (e.g., "Week 3 of 12")
- [ ] Add keyboard navigation (arrow keys)

### MonthView.jsx
- [ ] Add hover state on calendar cells
- [ ] Highlight today's date with ring/border
- [ ] Increase workout dot size (2px -> 6px)
- [ ] Add tooltip showing workout details

### ChatInterface.jsx
- [ ] Add typing indicator with animated dots
- [ ] Make welcome examples clickable
- [ ] Auto-scroll to bottom on new messages
- [ ] Replace alert() with toast notifications

### StravaImport.jsx
- [ ] Add loading skeleton for activities
- [ ] Convert table to cards on mobile
- [ ] Add pagination for large activity lists
- [ ] Show sync timestamp

### WorkoutCard.jsx
- [ ] Add smooth expand/collapse transition
- [ ] Animate checkmark on completion
- [ ] Remove edit alert (implement or hide)
- [ ] Add workout type icons

---

## Success Metrics

After implementation, measure:

1. **Lighthouse Accessibility Score**: Target >90
2. **Task Completion Rate**: Can users complete key flows without errors?
3. **Mobile Usability**: Touch targets compliant, responsive layouts working
4. **Performance**: No layout shifts, smooth animations (60fps)

---

## Notes

- **Strava buttons**: Keep orange (#fc4c02) for brand consistency
- **Error color**: Use --error-red (#c62828), not rust-brown
- **Success feedback**: Use --muted-teal for completion states, --success-green for explicit success messages
- **Persian blue contrast**: Ensure white text on --persian-blue passes WCAG AA (it does: 7.1:1 ratio)

---

*Last Updated: January 2026*
