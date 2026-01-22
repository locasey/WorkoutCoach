# Workout Coach Development Plan - Jan 18, 2026

  ## Overview

  This plan covers three objectives:
  1. **Repository Cleanup** - Archive old docs, remove temp files *(Done)*
  2. **UX Phases 3-6** - Continue implementing UX_IMPROVEMENT_PLAN.md *(DEFERRED)*
  3. **Workout Plan Management Feature** - New tab for managing plans *(DEFERRED)*


  ## Part 2: UX Implementation Phases

  ### Current Status
  - **Phase 1**: COMPLETE (Design System Foundation)
  - **Phase 2**: COMPLETE (Critical UX Fixes)
  - **Phase 3-6**: PENDING

  ### Implementation Order
  1. Phase 3: Interaction Polish
  2. Phase 4: Mobile Optimization
  3. Phase 5: Advanced Features (includes Plan Management)
  4. Phase 6: Accessibility Audit

  ---

  ### Phase 3: Interaction Polish

  #### 3.1 Card Expansion Animations
  **File**: `frontend/src/components/WorkoutCard.jsx`
  - Add CSS transitions to expanded content section
  - Use `max-height` + `opacity` animation with `--transition-normal`

  #### 3.2 Completion Animations
  **Files**: `WorkoutCard.jsx`, `index.css`
  - Add `@keyframes checkmark-pop` animation
  - Apply when workout status changes to completed
  - Optional: Add canvas-confetti for celebration effect

  #### 3.3 Typing Indicator for Chat
  **File**: `frontend/src/components/ChatInterface.jsx`
  - Create bouncing dots indicator component
  - Replace "Generating your workout plan..." text (line ~96)

  #### 3.4 Clickable Welcome Examples
  **File**: `frontend/src/components/ChatInterface.jsx`
  - Make example prompts clickable (lines 76-84)
  - On click: `setMessage(exampleText)`
  - Add keyboard support (Enter key)

  #### 3.5 Month View Tooltips
  **File**: `frontend/src/components/MonthView.jsx`
  - Add `title` attribute to workout cells showing type, distance, status

  #### 3.6 Undo Toast for Completions
  **Files**: `Toast.jsx`, `WeekAheadView.jsx`
  - Extend Toast to support action buttons
  - Show "Undo" button after marking workout complete

  #### 3.7 Hover States Enhancement
  **File**: `MonthView.jsx`
  - Add subtle scale transform on hover: `hover:scale-[1.02]`

  ---

  ### Phase 4: Mobile Optimization

  #### 4.1 Swipe Gestures
  **File**: `WeekAheadView.jsx`
  - Install `react-swipeable`
  - Swipe left = next week, swipe right = previous week

  #### 4.2 Activity Cards for Mobile
  **File**: `StravaImport.jsx`
  - Create `ActivityCard.jsx` component
  - Show cards on mobile (<768px), table on desktop

  #### 4.3 Bottom Sheet for Workout Details
  - Create `BottomSheet.jsx` component
  - Replace modal on mobile screens

  #### 4.4 3-Day Mobile Week View
  **File**: `WeekAheadView.jsx`
  - Show 3 days centered on today on mobile
  - Maintain 7-day view on larger screens

  #### 4.5 Pull-to-Refresh
  - Add to WeekAheadView and StravaImport

  ---

  ### Phase 5: Advanced Features

  See Part 3 below for Workout Plan Management (main feature)

  #### Other Phase 5 Items:
  - Keyboard shortcuts guide (? key shows modal)
  - Activity filtering/sorting in Strava tab
  - Batch actions (mark full week complete)
  - Markdown support in chat responses

  ---

  ### Phase 6: Accessibility Audit

  #### 6.1 Automated Testing
  - Install `@axe-core/react` for dev mode
  - Run Lighthouse audits (target >90)

  #### 6.2 Reduce Motion Support
  **File**: `index.css`
  ```css
  @media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
  animation-duration: 0.01ms !important;
  transition-duration: 0.01ms !important;
  }
  }
  ```

  #### 6.3 Manual Testing
  - Keyboard-only navigation
  - Screen reader testing (VoiceOver/NVDA)
  - Color contrast verification (WCAG AA: 4.5:1)

  ---

  ## Part 3: Workout Plan Management Feature

  ### Feature Overview
  Allow users to view, manage, and upload workout plans.

  ### User Stories
  1. As a user, I can view all my previously generated workout plans
  2. As a user, I can select which plan is "active" (shown in Week Ahead)
  3. As a user, I can delete old plans I no longer need
  4. As a user, I can upload my own workout plan (frontend only - parsing is backlog)
  5. As a user, I can export any plan to Excel

  ### UI Location
  **New Tab** - Add "My Plans" as a 4th tab alongside Week/Chat/Strava in `App.jsx`

  ### Component Architecture
  ```
  frontend/src/components/
  PlanManager/
  PlanManager.jsx      # Main tab view container
  PlanList.jsx         # Grid of plan cards
  PlanCard.jsx         # Individual plan display
  PlanUpload.jsx       # File upload (drag-drop)
  PlanManager.css      # Styles
  ```

  ### PlanCard UI Design
  ```
  +------------------------------------------+
  | [Active Badge]              [12 weeks]   |
  |                                          |
  | Half Marathon Training                   |
  | Goal: Complete half marathon under 2hrs  |
  |                                          |
  | Started: Jan 15, 2026 | 42 workouts      |
  |                                          |
  | [Activate]  [Export]  [Delete]           |
  +------------------------------------------+
  ```

  ### PlanUpload UI Design
  ```
  +------------------------------------------+
  |     [Drop Zone Icon]                     |
  |                                          |
  |   Drag & drop your workout plan here     |
  |              or                          |
  |         [Browse Files]                   |
  |                                          |
  |   Supported: Excel (.xlsx), CSV          |
  +------------------------------------------+
  | Note: File parsing coming soon           |
  +------------------------------------------+
  ```

  ### Entry Point
  **File**: `App.jsx`
  - Add "My Plans" tab to tab navigation (4th tab)
  - Tab renders `<PlanManager />` component
  - Update tab state management to include new tab

  ### API Endpoints (Existing)
  - `GET /api/workout-plans` - List all plans
  - `POST /api/workout-plans/<id>/activate` - Set active
  - `DELETE /api/workout-plans/<id>` - Delete plan
  - `GET /api/export/excel/<id>` - Export to Excel

  ### Backend Backlog (Not This Phase)
  - `POST /api/workout-plans/upload` - Parse uploaded file
  - File format detection (Excel, CSV, PDF)
  - Workout extraction and normalization
  - Create WorkoutPlan + Workout records from parsed data

  ### Dependencies
  ```json
  {
  "react-dropzone": "^14.2.0"
  }
  ```

  ---

  ## Part 4: New Dependencies Summary

  ```bash
  npm install react-swipeable canvas-confetti react-dropzone
  npm install -D @axe-core/react
  ```

  ---

  ## Part 5: Verification Plan

  ### Repository Cleanup Verification (CURRENT)
  - [ ] All 7 `tmpclaude-*` files deleted
  - [ ] `docs/archived/phases/` exists with 4 phase docs
  - [ ] `docs/archived/setup-guides/` exists with 3 setup docs
  - [ ] `docs/archived/feature-plans/` exists with 2 feature docs
  - [ ] `.gitignore` includes `tmpclaude-*` pattern
  - [ ] Root directory only contains essential docs (7 .md files)
  - [ ] Git commit with cleanup changes

  ### Phase 3 Verification (FUTURE)
  - [ ] Card expand/collapse has smooth animation
  - [ ] Completing workout shows checkmark animation
  - [ ] Chat shows typing indicator while generating
  - [ ] Clicking example prompt fills input
  - [ ] Hover on month cells shows tooltip
  - [ ] "Undo" appears in toast after completion

  ### Phase 4 Verification
  - [ ] Swipe left/right navigates weeks (mobile)
  - [ ] Strava activities show as cards on mobile
  - [ ] Workout details open as bottom sheet on mobile
  - [ ] Pull-to-refresh works on list views

  ### Phase 5 Verification (Plan Management)
  - [ ] Plan Manager opens from Week Ahead view
  - [ ] All plans display with metadata
  - [ ] Active plan highlighted distinctly
  - [ ] Can activate different plan (updates Week view)
  - [ ] Cannot delete active plan (shows warning)
  - [ ] Can delete inactive plans
  - [ ] File upload zone works (UI only)
  - [ ] Export to Excel downloads file

  ### Phase 6 Verification
  - [ ] Lighthouse Accessibility score >90
  - [ ] All elements keyboard accessible
  - [ ] Reduced motion preference respected
  - [ ] Screen reader announces content properly

  ---

  ## Part 6: Files to Create (Future Phases)

  ### Plan Management Feature (When Implemented)
  1. `frontend/src/components/PlanManager/PlanManager.jsx`
  2. `frontend/src/components/PlanManager/PlanList.jsx`
  3. `frontend/src/components/PlanManager/PlanCard.jsx`
  4. `frontend/src/components/PlanManager/PlanUpload.jsx`
  5. `frontend/src/components/PlanManager/PlanManager.css`

  ### Phase 4 Mobile (When Implemented)
  6. `frontend/src/components/BottomSheet.jsx`
  7. `frontend/src/components/ActivityCard.jsx`

  ---

  ## Execution Order

  ### NOW: Repository Cleanup
  1. Delete 7 `tmpclaude-*` temp files
  2. Create `docs/archived/` directory structure
  3. Move 11 files to archive locations
  4. Update `.gitignore` to prevent future temp files
  5. Commit cleanup changes

  ### FUTURE (Deferred)
  - Phase 3: Interaction Polish
  - Plan Management Feature (as new tab)
  - Phase 4: Mobile Optimization
  - Phase 6: Accessibility Audit

  Each phase should be committed separately with clear commit messages.