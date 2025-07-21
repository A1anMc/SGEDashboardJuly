# 🛡️ NavImpact Development Workflow - Protecting Your Baseline

## 🎯 **Core Principle: Never Break Production**

Your current baseline (`v1.0.0-baseline`) is **GOLD** - never modify it directly.

---

## 🔄 **Safe Development Workflow**

### **Step 1: Create Feature Branch**
```bash
# Always start from your stable baseline
git checkout v1.0.0-baseline
git checkout -b feature/your-feature-name

# Or for hotfixes
git checkout -b hotfix/critical-fix
```

### **Step 2: Develop & Test Locally**
```bash
# Test your changes locally first
./scripts/verify-baseline.sh  # Should still pass
uvicorn app.main:app --reload  # Test locally
```

### **Step 3: Create Staging Environment**
```bash
# Create a staging branch for testing
git checkout -b staging/feature-test
git push origin staging/feature-test

# Deploy to staging (separate Render service)
# Use: navimpact-api-staging.onrender.com
```

### **Step 4: Verify Before Production**
```bash
# Run baseline verification
./scripts/verify-baseline.sh

# Test all critical endpoints
curl https://navimpact-api.onrender.com/health
curl https://navimpact-api.onrender.com/
```

---

## 🚫 **What NOT to Do**

### ❌ **Never:**
- Modify `main` branch directly
- Push untested changes to production
- Change `requirements.txt` without testing
- Modify production environment variables
- Delete or rename the baseline tag

### ❌ **Avoid:**
- Adding new dependencies without thorough testing
- Changing database schema without migrations
- Modifying core configuration files without backup

---

## ✅ **Safe Development Practices**

### **1. Environment Isolation**
```bash
# Use separate .env files
cp .env .env.backup  # Backup current
cp .env .env.development  # Create dev version
cp .env .env.staging     # Create staging version
```

### **2. Dependency Management**
```bash
# Test new dependencies locally first
pip install new-package
# Test thoroughly before adding to requirements.txt

# Use virtual environments
python -m venv venv-dev
source venv-dev/bin/activate
```

### **3. Database Safety**
```bash
# Never modify production database directly
# Use migrations for schema changes
alembic revision --autogenerate -m "description"
alembic upgrade head  # Test locally first
```

### **4. Configuration Changes**
```bash
# Backup current config
cp app/core/config.py app/core/config.py.backup

# Make changes in feature branch
# Test thoroughly before merging
```

---

## 🔍 **Pre-Deployment Checklist**

Before merging to `main`:

- [ ] **Local tests pass**: `./scripts/verify-baseline.sh`
- [ ] **Staging deployment successful**
- [ ] **All API endpoints working**
- [ ] **Database migrations tested**
- [ ] **No new dependency conflicts**
- [ ] **Environment variables documented**
- [ ] **Rollback plan ready**

---

## 🚨 **Emergency Rollback Plan**

### **If Production Breaks:**
```bash
# 1. Immediately rollback to baseline
git reset --hard v1.0.0-baseline
git push --force origin main

# 2. Verify baseline is restored
./scripts/verify-baseline.sh

# 3. Check Render deployment
# Go to: https://dashboard.render.com/web/navimpact-api
```

### **If Database Issues:**
```bash
# 1. Check database connection
curl https://navimpact-api.onrender.com/health

# 2. Verify environment variables in Render
# DATABASE_URL should be correct

# 3. Check database logs in Render dashboard
```

---

## 📋 **Development Commands Reference**

### **Safe Development Start:**
```bash
# Create feature branch from baseline
git checkout v1.0.0-baseline
git checkout -b feature/new-feature

# Verify baseline is intact
./scripts/verify-baseline.sh
```

### **Testing Changes:**
```bash
# Test locally
uvicorn app.main:app --reload

# Test baseline verification
./scripts/verify-baseline.sh

# Test specific endpoints
curl http://localhost:8000/health
curl http://localhost:8000/
```

### **Safe Deployment:**
```bash
# 1. Test in staging first
git push origin staging/feature-test

# 2. Verify staging works
curl https://navimpact-api-staging.onrender.com/health

# 3. Only then merge to main
git checkout main
git merge feature/new-feature
git push origin main
```

---

## 🛡️ **Baseline Protection Commands**

### **Verify Baseline Integrity:**
```bash
# Check if baseline is intact
git show v1.0.0-baseline --name-only

# Compare current with baseline
git diff v1.0.0-baseline HEAD

# Verify baseline still works
./scripts/verify-baseline.sh
```

### **Create New Baseline (Only When Stable):**
```bash
# Only after thorough testing and validation
git tag -a v1.1.0-baseline -m "New stable baseline after feature X"
git push origin v1.1.0-baseline
```

---

## 📊 **Monitoring Your Baseline**

### **Daily Health Check:**
```bash
# Quick baseline verification
./scripts/verify-baseline.sh

# Check production status
curl https://navimpact-api.onrender.com/health
```

### **Weekly Baseline Audit:**
```bash
# Verify no unauthorized changes
git log --oneline v1.0.0-baseline..HEAD

# Check for configuration drift
git diff v1.0.0-baseline HEAD -- app/core/config.py
```

---

## 🎯 **Key Takeaways**

1. **Always branch from baseline** - never modify main directly
2. **Test locally first** - never push untested code
3. **Use staging environment** - test before production
4. **Keep baseline sacred** - it's your safety net
5. **Document all changes** - maintain clear history
6. **Have rollback plan ready** - know how to recover quickly

**Your baseline is your fortress - protect it at all costs! 🛡️** 