# Switchover & Decommission Checklist

This checklist ensures a smooth transition from the old frontend to the new frontend deployment.

## 🚦 Switchover & Decommission Checklist

### 1. Prepare the New Frontend
- [ ] **Test the new frontend** on its Render preview URL  
  Visit: [https://sge-dashboard-web-new.onrender.com](https://sge-dashboard-web-new.onrender.com)
- [ ] **Confirm homepage loads** without errors
- [ ] **Verify all routes** (dashboard, grants, tasks, etc.)
- [ ] **Ensure static assets** (`_next/static/...`) load correctly (no MIME errors)
- [ ] **Check environment variables**
  - `NEXT_PUBLIC_API_URL` points to the correct backend
  - API calls succeed (no CORS issues)
- [ ] **Test integrations**
  - Authentication (if used)
  - Forms, uploads, or data entry
  - Third-party integrations (analytics, tracking, etc.)

### 2. Backend Configuration
- [ ] **CORS settings:**  
  Ensure backend allows both old and new frontend URLs temporarily:
  ```python
  allow_origins=[
    "https://sge-dashboard-web.onrender.com",
    "https://sge-dashboard-web-new.onrender.com"
  ]
  ```
- [ ] After switchover, **remove the old frontend URL** from backend CORS config.

### 3. User Acceptance Testing (UAT)
- [ ] **Share the new frontend URL** with stakeholders or a test group
- [ ] **Collect feedback & confirm:**
  - UI/UX is consistent
  - No 404/502 issues
  - Data/API integrations work
- [ ] **Fix any final bugs or UX issues** before switchover

### 4. DNS & URL Switchover
- [ ] If using custom domains, **update DNS** to point to the new frontend service  
  On Render: remove domain mapping from old service, attach it to `sge-dashboard-web-new`
- [ ] If no custom domain, **update all bookmarks & links** to the new Render URL
- [ ] **Update backend `FRONTEND_URL` env var** to match the new domain

### 5. Post-Switchover Monitoring
- [ ] **Monitor Render logs** for the new frontend
- [ ] **Verify Render health checks** pass
- [ ] **Confirm API calls** return 200 from the backend
- [ ] Watch for unexpected:
  - 404s on `_next/static`
  - 502s on API calls
  - CORS errors in the browser console

### 6. Decommission Old Frontend
- [ ] **Announce the switchover** to users (if applicable)
- [ ] **Disable or delete** the old `sge-dashboard-web` service in Render
- [ ] **Remove old frontend environment variables & secrets**
- [ ] **Delete any unused deployment scripts/configs** for the old service

### 7. Final Clean-Up
- [ ] **Update README, docs, onboarding materials** to reference only the new frontend
- [ ] **Archive or backup the old frontend codebase** if you want a record
- [ ] **Update CI/CD pipelines** to only deploy the new frontend

---

## ✅ Migration Flow Summary
1. Test new frontend → ensure it's 100% stable  
2. Enable dual CORS → both frontends temporarily allowed  
3. Run UAT → gather & apply feedback  
4. Switch DNS / Render domain mapping  
5. Monitor live traffic for errors  
6. Decommission old frontend  
7. Clean up configs & docs

---

## 📊 Progress Tracking

| Step | Status | Date | Notes |
|------|--------|------|-------|
| 1. Prepare New Frontend | ⏳ Pending | | |
| 2. Backend Configuration | ⏳ Pending | | |
| 3. User Acceptance Testing | ⏳ Pending | | |
| 4. DNS & URL Switchover | ⏳ Pending | | |
| 5. Post-Switchover Monitoring | ⏳ Pending | | |
| 6. Decommission Old Frontend | ⏳ Pending | | |
| 7. Final Clean-Up | ⏳ Pending | | |

## 🚨 Emergency Rollback Plan

If issues arise during switchover:

1. **Immediate Actions:**
   - Revert DNS changes if custom domain is used
   - Re-enable old frontend service in Render
   - Update backend CORS to allow old frontend URL

2. **Investigation:**
   - Review Render logs for both services
   - Check browser console for errors
   - Verify environment variables are correct

3. **Communication:**
   - Notify stakeholders of rollback
   - Document issues for future reference
   - Schedule retry after fixes are implemented

## 📞 Contact Information

- **Technical Lead**: [Your Name]
- **Deployment Manager**: [Your Name]
- **Emergency Contact**: [Your Phone/Email] 