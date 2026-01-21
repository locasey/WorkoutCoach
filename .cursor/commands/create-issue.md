# Create Issue

User is mid-development and thought of a bug/feature/improvement. Capture it fast so they can keep working.

## Your Goal

Create a Linear issue in the **WorkoutCoach** project with:
- Clear title
- TL;DR of what this is about
- Current state vs expected outcome
- Relevant files that need touching
- Risk/notes if applicable
- Proper type/priority/effort labels

## How to Get There

**Ask questions** to fill gaps - be concise, respect the user's time. They're mid-flow and want to capture this quickly. Usually need:
- What's the issue/feature
- Current behavior vs desired behavior
- Type (bug/feature/improvement) and priority if not obvious

Keep questions brief. One message with 2-3 targeted questions beats multiple back-and-forths.

**Search for context** only when helpful:
- Web search for best practices if it's a complex feature
- Grep codebase to find relevant files
- Note any risks or dependencies you spot

**Skip what's obvious** - If it's a straightforward bug, don't search web. If type/priority is clear from description, don't ask.

**Keep it fast** - Total exchange under 2min. Be conversational but brief. Get what you need, create ticket, done.

## Linear Integration

Once you have enough info, use the Linear MCP tools to create the issue:

1. Use `linear_searchProjects` to find the WorkoutCoach project/team if needed
2. Use `linear_createIssue` to create the issue with:
   - `teamId`: WorkoutCoach team ID
   - `title`: Clear, actionable title
   - `description`: Markdown formatted with TL;DR, current vs expected, relevant files
   - `priority`: 1 (urgent), 2 (high), 3 (normal), 4 (low)
   - `labels`: bug, feature, improvement, etc.

After creating, confirm with the issue URL so user can reference it later.

## Behavior Rules

- Be conversational - ask what makes sense, not a checklist
- Default priority: 3 (normal), effort: medium (ask only if unclear)
- Max 3 files in context - most relevant only
- Bullet points over paragraphs
- Always create in WorkoutCoach project
