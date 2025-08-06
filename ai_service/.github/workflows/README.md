# AI Service GitHub Workflows

This directory contains comprehensive GitHub Actions workflows for the AI Service - a multi-modal audio processing pipeline for call center analytics and child protection services.

## 📋 Workflows Overview

### 1. Main CI/CD Pipeline (`ci-cd.yml`)
**Triggers:** Push to main/develop, PRs, releases, manual dispatch
**Purpose:** Complete CI/CD pipeline with quality gates, testing, security scanning, and deployment

#### Jobs:
- **Code Quality & Security**: Black formatting, isort, flake8, pylint, mypy, bandit, safety
- **Tests**: Unit tests and integration tests with Redis services
- **Docker Build & Test**: Multi-architecture container builds with health checks
- **Model Validation**: Individual AI model testing (Whisper, NER, Classification, etc.)
- **Security Scanning**: Trivy and Snyk vulnerability scanning
- **Performance Testing**: Load testing with Locust
- **Staging Deployment**: Automated deployment to staging environment
- **Production Deployment**: Automated deployment to production with health checks
- **Cleanup & Reporting**: Artifact cleanup and deployment reporting

#### Quality Gates:
- ✅ Code formatting and linting must pass
- ✅ All tests must pass with >80% coverage
- ✅ Security scans must have no critical/high vulnerabilities
- ✅ Docker images must build and pass health checks
- ✅ Performance benchmarks must meet thresholds

### 2. Model Management (`model-management.yml`)
**Triggers:** Model file changes, weekly schedule, manual dispatch
**Purpose:** AI model lifecycle management, validation, and deployment

#### Jobs:
- **Model Validation**: Accuracy, performance, and robustness testing
- **Model Updates**: Automated model version checking and updates
- **Model Benchmarking**: Latency, throughput, memory, and accuracy benchmarks
- **Model Registry**: Centralized model registry with versioning and metadata

#### Features:
- 🤖 Automated model updates from HuggingFace Hub
- 📊 Comprehensive model benchmarking
- 📚 Model registry with validation history
- 🔄 Automated PRs for model updates
- 🚀 Staging deployment with validation

### 3. Data Management (`data-management.yml`)
**Triggers:** Data file changes, weekly schedule, manual dispatch
**Purpose:** Data validation, preprocessing, augmentation, and backup

#### Jobs:
- **Data Validation**: Great Expectations validation suite
- **Data Preprocessing**: ETL pipeline for raw data processing
- **Data Augmentation**: ML data augmentation techniques
- **Data Backup**: S3 backup with versioning

#### Features:
- 🔍 Automated data quality checks
- 🔄 Data preprocessing pipelines
- ✨ Data augmentation for ML training
- 📦 Automated backups to cloud storage

## 🚀 Getting Started

### Prerequisites
1. **Repository Setup**:
   ```bash
   # Enable GitHub Actions
   # Configure repository secrets (see Secrets section)
   ```

2. **Required Secrets**:
   ```
   GITHUB_TOKEN: Automatic (GitHub provides)
   AWS_ACCESS_KEY_ID: For S3 data backups
   AWS_SECRET_ACCESS_KEY: For S3 data backups
   SNYK_TOKEN: For vulnerability scanning (optional)
   ```

3. **Repository Settings**:
   - Enable GitHub Actions
   - Configure branch protection rules
   - Set up environments (staging, production)

### Manual Workflow Triggers

#### Main CI/CD Pipeline
```bash
# Deploy to staging
gh workflow run ci-cd.yml -f environment=staging

# Deploy to production
gh workflow run ci-cd.yml -f environment=production
```

#### Model Management
```bash
# Validate all models
gh workflow run model-management.yml -f model_type=all -f action=validate

# Update specific model
gh workflow run model-management.yml -f model_type=whisper -f action=update

# Benchmark models
gh workflow run model-management.yml -f model_type=all -f action=benchmark

# Deploy updated models
gh workflow run model-management.yml -f model_type=classification -f action=deploy
```

#### Data Management
```bash
# Validate datasets
gh workflow run data-management.yml -f data_action=validate

# Preprocess data
gh workflow run data-management.yml -f data_action=preprocess

# Augment training data
gh workflow run data-management.yml -f data_action=augment

# Backup data to S3
gh workflow run data-management.yml -f data_action=backup
```

## 📊 Workflow Artifacts

### Main CI/CD Pipeline
- **Security Reports**: `security-reports` - Bandit and Safety analysis
- **Test Results**: `test-results-unit`, `test-results-integration` - Test outcomes and coverage
- **Performance Results**: `performance-test-results` - Load testing reports
- **Deployment Report**: `deployment-report` - Complete deployment summary

### Model Management
- **Model Validation**: `model-validation-{model}-{test_type}` - Validation results per model
- **Benchmark Results**: `benchmark-results-{model}-{metric}` - Performance benchmarks
- **Model Registry**: `model-registry` - Centralized model metadata and status

### Data Management
- **Validation Reports**: `data-validation-report` - Data quality reports
- **Processed Data**: `processed-data` - Clean, processed datasets
- **Augmented Data**: `augmented-data` - ML-ready augmented datasets

## 🔧 Configuration

### Environment Variables
Key environment variables used across workflows:

```yaml
env:
  REGISTRY: ghcr.io
  IMAGE_NAME_PREFIX: ${{ github.repository }}/ai-service
  PYTHON_VERSION: '3.11'
  WORKING_DIRECTORY: ./callcenter-ai/ai_service
  S3_BUCKET: 's3://callcenter-ai-data-prod'
```

### Docker Configuration
The workflows build multi-architecture Docker images with:
- **Base Image**: Python 3.11-slim
- **Platforms**: linux/amd64, linux/arm64
- **Registry**: GitHub Container Registry (ghcr.io)
- **Health Checks**: Automated health endpoint testing

### Model Configuration
Models are configured in the workflow matrix:
- **Whisper**: Speech-to-text transcription
- **Translation**: Swahili-English translation
- **NER**: Named Entity Recognition (spaCy)
- **Classification**: Case category classification
- **Summarization**: Text summarization (T5-based)

## 🛡️ Security & Compliance

### Security Scanning
- **Bandit**: Python security linter
- **Safety**: Dependency vulnerability scanner
- **Trivy**: Container vulnerability scanner
- **Snyk**: Additional vulnerability scanning

### Code Quality
- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: PEP 8 linting
- **pylint**: Advanced static analysis
- **mypy**: Type checking

### Data Privacy
- **Local Processing**: All AI processing happens offline
- **No External APIs**: No data sent to external services
- **Encrypted Storage**: S3 backups use encryption
- **Access Controls**: IAM-based access to resources

## 📈 Monitoring & Observability

### Built-in Monitoring
- **Health Checks**: Automated service health monitoring
- **Performance Metrics**: Response time and throughput tracking
- **Resource Usage**: CPU, memory, and GPU utilization
- **Error Tracking**: Comprehensive error logging and alerting

### Dashboards
The workflows generate reports for:
- **Model Performance**: Accuracy, latency, resource usage
- **Data Quality**: Validation results and drift detection
- **System Health**: Service availability and performance
- **Deployment Status**: Release and rollback tracking

## 🔄 Workflow Schedules

### Automated Schedules
- **Weekly Model Validation**: Sundays at 2 AM UTC
- **Weekly Data Validation**: Saturdays at 3 AM UTC
- **Daily Security Scans**: Daily at 2 AM UTC (if configured)

### Manual Triggers
All workflows support manual triggering with configurable parameters for:
- Target environment selection
- Specific model or data operations
- Custom deployment options

## 🎯 Best Practices

### Development Workflow
1. **Feature Development**: Create feature branches from `develop`
2. **Pull Requests**: All changes via PRs with automated testing
3. **Code Review**: Mandatory reviews before merging
4. **Quality Gates**: All CI checks must pass

### Deployment Strategy
1. **Develop → Staging**: Automatic deployment for testing
2. **Staging Validation**: Manual or automated testing
3. **Main → Production**: Automatic deployment with approval
4. **Rollback Support**: Quick rollback procedures

### Model Management
1. **Validation First**: Always validate before deployment
2. **Staged Rollout**: Deploy to staging before production
3. **Performance Monitoring**: Track model performance post-deployment
4. **Version Control**: Maintain model version history

## 🚨 Troubleshooting

### Common Issues

#### Workflow Failures
```bash
# Check workflow logs
gh run list --workflow=ci-cd.yml
gh run view {run-id}

# Re-run failed jobs
gh run rerun {run-id} --failed
```

#### Model Loading Issues
- Check model file paths and permissions
- Verify model download and validation
- Review memory and disk space requirements

#### Data Pipeline Issues
- Validate data formats and schemas
- Check S3 permissions and connectivity
- Review preprocessing script logs

### Support Channels
- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and questions
- **Wiki**: Detailed troubleshooting guides

---

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Celery Documentation](https://docs.celeryproject.org/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

**Built for Production** 🏭  
These workflows are designed for enterprise-grade AI service deployment with comprehensive quality assurance, security scanning, and operational monitoring.
