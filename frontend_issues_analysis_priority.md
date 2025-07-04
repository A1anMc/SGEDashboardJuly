# Frontend Issues Priority Plan

## Current Sprint Context (from Roadmap)
1. Integrate task management with projects
2. Begin grant management implementation
3. Design program logic interface
4. Enhance user experience

## Priority 1: Critical Build Issues (Block Everything)
These must be fixed first as they prevent any development work:

```bash
# Step 1: Fix Dependencies (Estimated time: 30 mins)
cd frontend
npm install  # Install existing dependencies
```

Add missing core dependencies to package.json:
```json
{
  "dependencies": {
    "@tanstack/react-query": "^5.8.0",  // Required for data fetching
    "axios": "^1.6.0",                  // Required for API calls
    "react-hook-form": "^7.47.0",       // Required for forms
    "@hookform/resolvers": "^3.3.0",    // Required for form validation
    "zod": "^3.22.0"                    // Required for schema validation
  }
}
```

## Priority 2: Sprint-Critical Features (Support Current Goals)
Focus on dependencies and fixes needed for current sprint tasks:

### For "Integrate task management with projects":
1. Fix task-related components first:
   - Add missing dependencies:
   ```json
   {
     "dependencies": {
       "date-fns": "^2.30.0",        // For task date handling
       "react-hot-toast": "^2.4.0"   // For task notifications
     }
   }
   ```
   - Fix TypeScript inconsistencies in task/project interfaces

### For "Begin grant management implementation":
1. Standardize UI library choice:
   ```json
   {
     "dependencies": {
       "@headlessui/react": "^1.7.0",    // Modern, works well with Tailwind
       "@heroicons/react": "^2.0.0"      // Required for icons
     }
   }
   ```
   - Remove @mui/material (unless there's a specific requirement)

### For "Design program logic interface":
- Keep both UI libraries temporarily until design phase is complete
- Then standardize based on design decisions

## Priority 3: Configuration Cleanup
Clean up duplicate configs that could cause issues during development:

1. Next.js config (keep .js version):
   - Delete: `frontend/next.config.ts`
   - Keep: `frontend/next.config.js`

2. PostCSS config (keep .js version):
   - Delete: `frontend/postcss.config.mjs`
   - Keep: `frontend/postcss.config.js`

## Priority 4: Error Handling & UX (Support Sprint Goal #4)
Add error boundaries to critical user flows:
1. Task management integration points
2. Grant management forms
3. Project creation/editing

## Priority 5: Documentation & Structure
Update documentation to reflect current state:
1. Clarify "new-frontend" directory situation
   - If it's planned: Create directory with README explaining future purpose
   - If obsolete: Remove references from docs

## Execution Plan

### Day 1 (Critical Path)
- Morning: Fix all Priority 1 issues (dependencies)
- Afternoon: Begin Priority 2 (sprint-critical features)

### Day 2 (Feature Support)
- Morning: Complete Priority 2 (UI standardization)
- Afternoon: Priority 3 (configuration cleanup)

### Day 3 (Polish & Documentation)
- Morning: Priority 4 (error handling)
- Afternoon: Priority 5 (documentation)

## Success Metrics
- ✅ `npm run build` succeeds
- ✅ Task management integration works
- ✅ Grant management forms are functional
- ✅ Single UI library in use
- ✅ Clean configuration files
- ✅ Updated documentation

## Risk Mitigation
1. **Before deleting any files:**
   - Create a branch: `git checkout -b frontend-cleanup`
   - Commit current state: `git commit -m "Save current state before cleanup"`

2. **Before removing @mui/material:**
   - Audit all components using Material UI
   - Create migration plan if extensive usage found

3. **Testing Strategy:**
   - Test task integration after each dependency update
   - Verify grant forms after UI library standardization
   - Run full test suite after configuration cleanup

## Next Steps After Completion
1. Review Phase 4 requirements (Program Logic & Metrics)
2. Plan UI component library strategy for upcoming features
3. Set up automated dependency checks to prevent future issues 