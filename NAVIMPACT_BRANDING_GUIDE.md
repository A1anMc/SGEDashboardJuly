# NavImpact Branding Guide

## 🎯 Project Identity

**Project Name**: NavImpact  
**Repository**: https://github.com/A1anMc/NavImpact.git  
**Brand Colors**: Impact Teal (#0D9488), Energy Coral (#F97316)

## ✅ Required Branding

### Repository Names
- ✅ `NavImpact` or `navimpact`
- ❌ `SGE`, `sge`, `SGEDashboard`

### Package Names
- ✅ `navimpact`
- ❌ `sge-dashboard`, `sge_dashboard`

### Service Names
- ✅ `navimpact-api`, `navimpact-frontend`, `navimpact-db`
- ❌ `sge-dashboard-api`, `sge-dashboard-frontend`

### URLs
- ✅ `navimpact-api.onrender.com`, `navimpact-frontend.onrender.com`
- ❌ `sge-dashboard-api.onrender.com`

## 🔍 Pre-Push Checklist

Before pushing code, ensure:
1. Repository URL contains "NavImpact"
2. package.json name is "navimpact"
3. No SGE references in key files
4. NavImpact branding is present

## 🛠️ Automatic Checks

### Manual Check
```bash
./scripts/check-branding.sh
```

### Git Hook
Automatically runs before every push to prevent branding issues.

## 📝 File Locations to Check

- `frontend/package.json` - Project name
- `render.yaml` - Service names and URLs
- `README.md` - Project title and links
- `app/core/config.py` - Application names
- `alembic/env.py` - Migration names

## 🚨 If Branding Issues Found

1. **Stop the push**
2. **Fix the branding issues**
3. **Run check again**
4. **Proceed with push**

---

**Remember**: NavImpact is the future. SGE is the past. 🎯 