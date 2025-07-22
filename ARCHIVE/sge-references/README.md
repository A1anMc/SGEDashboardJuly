# SGE References Archive

This directory contains files that were previously part of the SGE Dashboard project and have been archived as part of the transition to NavImpact.

## Archived Files

### Documentation
- `FIXES.md` - Previous fixes applied to SGE Dashboard
- `grant_system_enhancements.md` - Grant system enhancement documentation
- `DATABASE_SETUP.md` - SGE Dashboard database setup guide
- `PRODUCTION_FIX_SUMMARY.md` - Production deployment fixes summary
- `render-frontend.yaml` - Old SGE frontend deployment configuration

## Updated References

The following files were updated to use NavImpact branding instead of SGE:

### Frontend Files
- `src/app/layout.tsx` - Updated title to "NavImpact Dashboard"
- `src/app/dashboard/settings/page.tsx` - Updated API URL references
- `next.config.ts` - Updated API URLs and image domains

### Backend Files
- `app/db/session.py` - Updated database URL to navimpact_db
- `app/db/init_db.py` - Updated application name and database references
- `app/core/api_client.py` - Updated User-Agent to NavImpact
- `app/core/email.py` - Updated email templates
- `app/core/logging_config.py` - Updated service name
- `app/templates/email/task_assigned.html` - Updated email signatures
- `app/templates/email/task_updated.html` - Updated email signatures
- `alembic/env.py` - Updated migration application name

### Configuration Files
- `render.yaml` - Updated to NavImpact service names and URLs
- `README.md` - Updated project title and repository references
- `PHASE2_STEP1_BASELINE.md` - Updated repository URL

## Service Names Changed

### Old SGE Names
- `sge-dashboard-api` → `navimpact-api`
- `sge-dashboard-web` → `navimpact-frontend`
- `sge_dashboard` → `navimpact_db`

### Old SGE URLs
- `https://sge-dashboard-api.onrender.com` → `https://navimpact-api.onrender.com`
- `https://sge-dashboard-web.onrender.com` → `https://navimpact-frontend.onrender.com`

## Notes

- All SGE branding has been replaced with NavImpact
- Database references updated to use navimpact_db
- Email templates updated to use NavImpact team signatures
- Deployment configurations updated for NavImpact services
- Scripts and monitoring tools still contain SGE references for historical context

This archive preserves the history of the SGE Dashboard while ensuring the current codebase uses NavImpact branding consistently. 