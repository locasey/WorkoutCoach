# Weekly Workout Calendar - Design Files

This folder contains the Figma design export for the "Week Ahead" feature.

## Design Source

- **Figma Link**: https://www.figma.com/design/OiO4e2PPkZBk9jgKqHVKRW/Weekly-Workout-Calendar
- **Export Date**: January 2026
- **Format**: React/TypeScript code export from Figma

## Design Components

The design includes fully functional React components:

- **WeekAheadView.tsx** - Main week calendar view with 7-day grid
- **WorkoutCard.tsx** - Expandable workout card component
- **MonthView.tsx** - Full calendar month view
- **UI Components** - Complete shadcn/ui component library (Radix UI)

## Color Palette

- **Muted Teal**: `#8eb19d` - Completed workouts, success states
- **Carbon Black**: `#1e1b18` - Primary text color
- **Almond Silk**: `#eacdc2` - Background, subtle accents
- **Persian Blue**: `#072ac8` - Pending workouts, primary actions
- **Rust Brown**: `#a44200` - Rest days, warning states

## Running the Design Preview

To preview the design standalone:

```bash
cd design
npm install
npm run dev
```

This will start a development server on port 3000.

## Integration Notes

These components need to be integrated into the main frontend app (`frontend/`) and connected to the backend API endpoints:

- `GET /api/workouts/week` - Fetch current week workouts
- `PUT /api/workouts/{id}/complete` - Toggle completion
- `PUT /api/workouts/{id}` - Edit workout details

## Design Features

- ✅ Expandable workout cards (click to show details)
- ✅ Completion status toggles
- ✅ Edit buttons on each workout
- ✅ Progress counter (completed/total)
- ✅ Week/month view toggle
- ✅ Week navigation (previous/next)
- ✅ Intensity visualization
- ✅ Responsive design

## Attribution

This design uses components from [shadcn/ui](https://ui.shadcn.com/) under MIT license.
  