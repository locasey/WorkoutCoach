# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Mobile-First UI Redesign**: Fully responsive, high-contrast "sporty" interface inspired by professional training tools.
- **Horizontal Day Picker**: New scrollable navigation for the week view on mobile.
- **Today Hero Section**: Dynamic dashboard element highlighting the current day's training with large metrics.
- **Side-by-Side Metrics**: Workout cards now show "Planned vs. Actual" durations and distances.
- **Bottom-Sheet Edit View**: Mobile-optimized modal for updating workout details.
- **Quick Action Buttons**: Touch-friendly buttons (min 44x44px) for one-tap completion and editing.

### Changed
- **Visual Theme**: Transitioned from muted tones to a high-contrast palette (Sporty Blue and Carbon Black).
- **Typography**: Updated to bold, high-glancability fonts (Inter) for better readability during training.
- **Workout Card Layout**: Prioritized Duration as the primary metric in a more minimalist, professional layout.
- **Navigation**: Moved main navigation to a fixed bottom bar on mobile for better ergonomics.
- **Global Styles**: Updated `index.css` and `App.css` with a modernized design system and CSS variables.

### Fixed
- **Critical**: Fixed blank screen bug caused by undefined `swipeHandlers` in WeekAheadView - `useSwipeable` hook was imported but never called.
- Improved mobile responsiveness across all main views.
- Optimized touch targets for accessibility and ease of use on small screens.
- Removed unnecessary container and header borders in Week view for cleaner UI.

