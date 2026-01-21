# Initial Exploration Stage

Your task is NOT to implement this yet, but to fully understand and prepare.

## Step 1: Get Context from Linear (if applicable)

**If the user mentions a Linear issue or ticket:**

Explicitly invoke the Linear MCP tool to fetch it:
```
I'm calling the linear_getIssue tool with issueId: [ID]
```

This gives you:
- Full issue description and acceptance criteria
- Comments with additional context
- Linked issues or dependencies
- Current status and priority

**If the user doesn't mention a Linear issue:**

Ask: "Is there a Linear issue for this? If so, share the ID or URL and I'll pull in the full context."

If they don't have one, proceed anyway with the exploration based on their description.

## Step 2: Explore the Codebase

Your responsibilities:

1. **Understand current architecture**
   - Analyze relevant files and their relationships
   - Map out dependencies and data flow
   - Identify existing patterns and conventions used in the codebase

2. **Determine integration points**
   - Where does this feature fit in the current structure?
   - What modules/components need to interact with it?
   - Are there existing utilities or abstractions to leverage?

3. **Identify constraints and edge cases**
   - Technical limitations (API limits, performance considerations)
   - Edge cases that need handling (within reason - don't overengineer)
   - Potential conflicts with existing functionality

4. **Surface ambiguities**
   - Anything unclear in the description or Linear issue
   - Missing requirements or acceptance criteria
   - Implementation details that have multiple valid approaches

## Step 3: Ask Clarifying Questions

List all questions and ambiguities in a clear, organized format:

**Requirements Clarifications:**
- [Questions about what the feature should do]

**Technical Decisions:**
- [Questions about how it should be implemented]

**Scope Boundaries:**
- [Questions about what's in/out of scope]

**Edge Cases:**
- [Specific scenarios that need clarification]

Keep it focused - typically 3-7 well-formed questions. Group related questions together.

## Important Guidelines

- **DO NOT assume** requirements or scope beyond what's explicitly described
- **DO NOT start implementing** - this is pure exploration and planning
- **DO explore** the codebase thoroughly to ask informed questions
- **DO reference** specific files, functions, or patterns you found
- **DO highlight** multiple valid approaches when they exist

We'll iterate on this back-and-forth until all ambiguities are resolved and you have no further questions.

## How to Use Linear MCP Tools

When working with Linear issues, explicitly invoke tools by name:

- **Fetch an issue**: "I'm calling linear_getIssue with issueId: WORK-123"
- **Search for related issues**: "I'm calling linear_searchIssues to find similar features"
- **Get project context**: "I'm calling linear_getProject to understand the WorkoutCoach project structure"

Don't just say "I'll check Linear" - actually invoke the MCP tool.

---

**Please confirm that you fully understand, and I will describe the problem I want to solve and the feature in detail. Do not implement anything yet we are just exploring**