
# Unit Testing Guide – Vue + Django Project

## What is Unit Testing?

Unit testing is the process of testing individual parts (units) of your code—like functions, components, or methods—to make sure they behave as expected.

In our project:
- **Frontend units** = Vue components and JavaScript functions
- **Backend units** = Django models, serializers, and view functions

---

## Why Unit Testing?

Here’s why unit testing is important for our project:
- Catch bugs early during development  
- Make code easier to maintain  
- Increase developer confidence during code changes  
- Save time debugging in the long run  
- Acts as documentation of how code is expected to work  

---

## What Makes a Good Unit Test?

A good unit test should:
- Test one specific behavior  
- Be independent (not depend on other tests)  
- Be repeatable and deterministic  
- Be easy to read and understand  

---

## How I Do Unit Testing (My Process)

### Frontend (Vue 3) – Using Vitest

We use **Vitest** for testing Vue components and logic.

#### 1. Install Dependencies:

```bash
npm install --save-dev vitest vue-test-utils jsdom @testing-library/vue
```

#### 2. Example Test Case:

```js
// tests/components/Navbar.spec.js
import { mount } from '@vue/test-utils'
import Navbar from '@/components/Navbar.vue'

describe('Navbar.vue', () => {
  it('renders the logo text', () => {
    const wrapper = mount(Navbar)
    expect(wrapper.text()).toContain('UAT System')
  })
})
```

#### 3. Run the tests:

```bash
npx vitest
```

Or use watch mode during development:

```bash
npx vitest --watch
```

---

### Backend (Django) – Using Pytest

We use **Pytest** for testing Django models, serializers, and views.

#### 1. Install Dependencies:

```bash
pip install pytest pytest-django
```

#### 2. Add `pytest.ini`:

```ini
# pytest.ini
[pytest]
DJANGO_SETTINGS_MODULE = backend.settings
```

#### 3. Example Test Case:

```python
# app_name/tests/test_models.py
import pytest
from app_name.models import Organization

@pytest.mark.django_db
def test_organization_str():
    org = Organization.objects.create(name="Test Org")
    assert str(org) == "Test Org"
```

#### 4. Run the tests:

```bash
pytest
```

Optional: Run with coverage

```bash
pytest --cov=app_name
```

---

## 📦 Folder Structure (How I Organize)

### Frontend:

```
/src
  /components
  /views
/tests
  /components
    ComponentName.spec.js
```

### Backend:

```
/app_name/
  /models.py
  /views.py
/app_name/tests/
  test_models.py
  test_views.py
```

---

## What Is Expected

- Write unit tests for each new component, model, or logic function  
- Use proper naming conventions (e.g., `ComponentName.spec.js`, `test_models.py`)  
- Run tests before pushing changes  
- Keep tests simple and focused on one behavior  

---

## Learn More

- [Vue Unit Testing](https://vue-test-utils.vuejs.org/)  
- [Vitest Docs](https://vitest.dev/)  
- [Django Testing](https://docs.djangoproject.com/en/stable/topics/testing/)  
- [Pytest Docs](https://docs.pytest.org/)  
