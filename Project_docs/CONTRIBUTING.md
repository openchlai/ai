# Contributing to OpenCHSAI

Thank you for considering contributing to OpenCHSAI! 🚀  
This document outlines how to contribute code, documentation, and ideas to this project.

## 📜 Code of Conduct

Please read and adhere to our [Code of Conduct](CODE_OF_CONDUCT.md).

## 🏁 Getting Started

1. **Fork the repository** and clone it locally:

   ```bash
   git clone https://github.com/your-username/openchsai.git
   cd openchsai
   ```

2. Create a new branch for your contribution:

   ```bash
   git checkout -b feature/your-feature-name
   ```

## 🛠️ Development Setup

Refer to the DEPLOYMENT_GUIDE.md and DATA_PIPELINE.md for detailed setup instructions for the backend, frontend, models, and data pipeline components.

Basic setup example:

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend
npm install && npm run dev

# Models
cd ../models
pip install -r requirements.txt
```

Use the provided script to set up the required folders:

```bash
./setup_folders.sh
```

## 🧪 Running Tests

Refer to TESTING_STRATEGY.md for testing protocols.

```bash
# Backend tests
cd tests
pytest

# Frontend tests
cd ../frontend
npm run test
```

## ✍️ Making Contributions

### 💡 Feature Requests and Improvements

- Open an issue with the enhancement label.
- Clearly describe the problem and your proposed solution.
- Reference affected files or documents (e.g., ARCHITECTURE.md, ROADMAP.md).

### 🐛 Bug Reports

- Describe steps to reproduce the issue.
- Include relevant logs, error messages, or screenshots.
- Mention affected modules (e.g., data_pipeline, gateway, trainer).

### 🧑‍💻 Code Contributions

- Follow our CODE_REVIEW_CHECKLIST.md.
- Use consistent coding styles:
  - Python: PEP 8, use black and flake8
  - JavaScript/Vue: use eslint and prettier
- Include or update relevant documentation (API_REFERENCE.md, etc.).
- Add or update tests to cover your changes.

## 🔄 Pull Request Process

1. Push your branch:

   ```bash
   git push origin feature/your-feature-name
   ```

2. Open a Pull Request.
3. Link related issues and summarize your changes.
4. Collaborate with reviewers and revise if needed.
5. Once approved, it will be merged by a maintainer.

## 🔒 Security

To report security issues, please follow the guidance in SECURITY.md.

## 📚 Additional Resources

- README.md
- PROJECT_CHARTER.md
- PRIVACY_POLICY.md
- ROADMAP.md
- GOVERNANCE.md
