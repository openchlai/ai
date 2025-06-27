# Usage Guide

## Getting Started

This guide will help you get started with the OpenCHS documentation system.

## Development Workflow

### Local Development

Start the development server:

``` bash
npm run dev
```

Visit http://localhost:5173 to view your documentation.

### Building the Documentation

Build for production:

```bash
npm run build
```

### Preview Production Build

Preview the built site:

```bash
npm run serve
```

## Docker Usage

### Build Docker Image

```bash
npm run docker:build
```

### Run Docker Container

```bash
npm run docker:run
```

Access at http://localhost:8080

## Kubernetes Deployment

### Deploy to Cluster

```bash
npm run k8s:deploy
```

### Check Status

```bash
kubectl get pods -n aidocs
kubectl port-forward service/aidocs-service 8080:80 -n aidocs
```

## Testing

### Run All Tests

```bash
npm test
```

### Individual Tests

```bash
npm run test:build    # Test build process
npm run test:links    # Validate links
npm run test:health   # Health checks
```

## Next Steps

- [Features](/features) - Explore available features
- [Documentation](/documentation) - Detailed setup instructions
- [Support](/support) - Get help when needed
- [FAQ](/faq) - Common questions and answers

