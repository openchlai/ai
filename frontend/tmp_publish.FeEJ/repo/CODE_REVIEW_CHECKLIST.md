# 🔍 Full-Stack Code Review Checklist

## 🎯 Backend (Django/PHP)
- [ ] Does the code follow PEP 8 / PSR-12 standards?
- [ ] Are security risks handled (SQL injection, XSS, CSRF)?
- [ ] Are database migrations included (if needed)?
- [ ] Is error handling robust?

## 🎯 Frontend (Vue/Vanilla JS)
- [ ] Is the UI responsive and clean?
- [ ] Is state management efficient (Vuex/Pinia)?
- [ ] Does JavaScript follow best practices (ESLint clean)?
- [ ] Are components reusable and well-structured?

## 🔥 Tests
- [ ] Are new features covered with unit tests?
- [ ] Do existing tests pass without errors?

## 🔧 Performance & Security
- [ ] Is data validated and sanitized properly?
- [ ] Are sensitive data and secrets secure?

✅ **Result:** Reviewers now follow a unified checklist.

---

🚀 **Next Steps:**  
- ✅ Add auto-labeling for PR types (e.g., feature, bug).  
- ✅ Set branch protection rules.  
- ✅ Setup Docker for full-stack previews (optional).  

