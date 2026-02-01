# Feature Implementation Plan: Mobile-First UI Redesign

**Overall Progress:** `100%`

## TLDR
Redesigning the Workout Coach interface to be a **mobile-first, sporty, and minimalist** training tool. The goal is to maximize "glancability" by focusing on **Duration** as the primary metric and using a **TrainingPeaks-inspired** aesthetic to provide a professional coaching experience.

## Critical Decisions
- **Navigation:** Bottom navigation bar for better one-handed mobile ergonomics.
- **Hierarchy:** "Today Hero" layout to immediately answer "What is my workout now?" while keeping the rest of the week accessible via a horizontal day picker.
- **Aesthetic:** High-contrast, minimal decoration, and bold typography to align with professional sports tools like TrainingPeaks.
- **Metrics:** Prioritizing **Duration** (minutes) over distance as the primary visual indicator, with side-by-side "Planned vs. Actual" tracking.

## Tasks:

- [x] **Step 1: Layout & Mobile Navigation** 🏗️
  - [x] Implement fixed bottom navigation bar in `App.jsx` (Done)
  - [x] Add CSS for bottom-nav-safe areas (padding-bottom on main container) ✅
  - [x] Standardize mobile breakpoints for all main views ✅

- [x] **Step 2: Glanceable Week Dashboard** 📋
  - [x] Implement horizontal scrolling "Day Picker" for week navigation ✅
  - [x] Create "Today" Hero section with expanded workout details and large metrics ✅
  - [x] Add visual status indicators (dots/lines) for the weekly summary ✅

- [x] **Step 3: "Sporty" Workout Card Redesign** 🏃
  - [x] Rebuild `WorkoutCard.jsx` with high-contrast borders and bold typography ✅
  - [x] Primary focus on Duration (e.g., "45m") in the main card body ✅
  - [x] Implement side-by-side layout for **Planned** vs. **Actual** (with Strava placeholder) ✅

- [x] **Step 4: Mobile-First Interactions** 🔘
  - [x] Refactor `WorkoutEditModal.jsx` into a mobile-friendly bottom-sheet component ✅
  - [x] Add "Quick Action" buttons (Complete/Reschedule) directly to the cards ✅
  - [x] Optimize all touch targets for mobile (min 44x44px) ✅

- [x] **Step 5: Visual Polish & High-Contrast Theme** 🎨
  - [x] Update global CSS with the new minimalist color palette and font weights ✅
  - [x] Refine icons and labels for maximum clarity at small sizes ✅
  - [x] Ensure consistent "Empty States" for days without workouts ✅

