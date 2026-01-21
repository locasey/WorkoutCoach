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

## Linear Integration - CRITICAL

You MUST use the Linear MCP server tools to create issues. The Linear MCP server is already connected.

### Step 1: Find Team/Project IDs (only if you don't have them cached)

**Explicitly call the MCP tool:**
```
Use the linear_searchProjects MCP tool to find the WorkoutCoach project
```

Or if you need team info:
```
Use the linear_listTeams MCP tool to get available teams
```

### Step 2: Create the Issue

**You MUST explicitly invoke the Linear MCP tool by name.** Say something like:

"I'm now calling the linear_createIssue tool with the following parameters..."

Then call `linear_createIssue` with:
- `teamId`: The WorkoutCoach team ID (from Step 1)
- `projectId`: The WorkoutCoach project ID (from Step 1) - OPTIONAL but preferred
- `title`: Clear, actionable title
- `description`: Markdown formatted with:
```
  **TL;DR:** [one sentence summary]
  
  **Current State:**
  [what's happening now]
  
  **Expected Outcome:**
  [what should happen]
  
  **Relevant Files:**
  - file1.py
  - file2.ts
  
  **Notes/Risks:**
  [any gotchas or dependencies]
```
- `priority`: 1 (urgent), 2 (high), 3 (normal), 4 (low)
- `labelIds`: Array of label IDs (you may need to use `linear_listLabels` first to get these)

### Step 3: Confirm Creation

After creating, show the issue URL and key details so user can reference it later.

## Important: How to Actually Call MCP Tools

DO NOT just say "I'll use the Linear tool" - you must **explicitly invoke it**. Examples:

❌ Wrong: "I'll create this issue in Linear for you"
✅ Right: "I'm calling the linear_createIssue MCP tool now with these parameters: teamId=..., title=..."

❌ Wrong: "Let me search for the project"
✅ Right: "Using the linear_searchProjects MCP tool to find WorkoutCoach"

The MCP tools are available but you must call them by their exact function names:
- `linear_listTeams`
- `linear_searchProjects` 
- `linear_createIssue`
- `linear_listLabels`
- `linear_updateIssue`

## Behavior Rules

- Be conversational - ask what makes sense, not a checklist
- Default priority: 3 (normal), effort: medium (ask only if unclear)
- Max 3 files in context - most relevant only
- Bullet points over paragraphs
- Always create in WorkoutCoach project
- **ALWAYS explicitly call Linear MCP tools by name**