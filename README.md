# Multi-Agent System

An enterprise multi-agent system that enables distributed agent orchestration, communication, and tool execution across different organizational divisions using AWS services.

## Architecture Overview

The system follows a federated architecture where each enterprise division operates independently while participating in a shared enterprise ecosystem:

- **Division Gateways**: Amazon Bedrock Gateway instances for each division
- **Enterprise Agent Registry**: Centralized registry of all agents across divisions
- **Message Router**: EventBridge + SQS for cross-division communication
- **Tool Registry**: Centralized registry and execution framework for tools
- **Monitoring**: CloudWatch metrics, logs, and X-Ray tracing

## Key Features

- **Cross-Division Agent Discovery**: Agents can discover and communicate with agents across all enterprise divisions
- **Bedrock Agent Integration**: Native support for Amazon Bedrock Agents with conversation memory and knowledge bases
- **Tool Execution Framework**: Centralized tool registry with Lambda-based execution
- **Security & Compliance**: IAM-based access control, encryption, and audit logging
- **Monitoring & Observability**: Comprehensive monitoring with CloudWatch and X-Ray
- **Infrastructure as Code**: Complete AWS CDK templates for deployment

## Project Structure

```
├── src/
│   ├── agents/                 # Agent implementations
│   │   ├── bedrock-agents/     # Bedrock Agent configurations
│   │   ├── lambda-agents/      # Custom Lambda agents
│   │   ├── action-groups/      # Action group implementations
│   │   └── knowledge-bases/    # Knowledge base configurations
│   ├── division-gateways/      # Division gateway implementations
│   │   ├── gateway-config/     # Bedrock Gateway configurations
│   │   ├── federation/         # Cross-division communication
│   │   └── auth/              # Authentication handlers
│   ├── tools/                  # Tool implementations
│   │   ├── registry/          # Tool registry service
│   │   ├── executors/         # Tool execution functions
│   │   └── schemas/           # Tool schemas
│   └── shared/                # Shared services and utilities
│       ├── enterprise-registry/ # Enterprise Agent Registry
│       ├── message-router/     # Message routing service
│       ├── monitoring/         # Monitoring components
│       ├── security/          # Security utilities
│       ├── models/            # Data models
│       └── interfaces/        # Common interfaces
├── infrastructure/
│   └── cdk/                   # AWS CDK infrastructure code
│       ├── stacks/            # CDK stack definitions
│       ├── app.py             # CDK app entry point
│       └── cdk.json           # CDK configuration
├── tests/                     # Test files
├── docs/                      # Documentation
└── pyproject.toml            # Project configuration
```

## Requirements Addressed

This implementation addresses the following requirements from the specification:

- **Requirement 1.1, 1.2, 1.5**: Project structure supports division gateways, agent management, and infrastructure as code
- **Common interfaces and data models**: Defined in `src/shared/models/` and `src/shared/interfaces/`
- **AWS CDK infrastructure templates**: Complete CDK stacks in `infrastructure/cdk/`

## Getting Started

### Prerequisites

- Python 3.11 or higher
- AWS CLI configured with appropriate permissions
- Node.js and npm (for AWS CDK)
- AWS CDK CLI installed

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd multi-agent-system
```

2. Install Python dependencies:
```bash
pip install -e ".[dev]"
```

3. Install CDK dependencies:
```bash
cd infrastructure/cdk
pip install -r requirements.txt
```

### Deployment

1. Bootstrap CDK (first time only):
```bash
cd infrastructure/cdk
cdk bootstrap
```

2. Deploy the infrastructure:
```bash
# Deploy all stacks
cdk deploy --all

# Or deploy specific stacks
cdk deploy MultiAgentSystemSecurity
cdk deploy MultiAgentSystemEnterpriseRegistry
cdk deploy MultiAgentSystemMessageRouter
cdk deploy MultiAgentSystemToolRegistry
cdk deploy MultiAgentSystemMonitoring
cdk deploy MultiAgentSystemDivisionAGateway
cdk deploy MultiAgentSystemDivisionBGateway
```

### Configuration

After deployment, configure the Bedrock Gateways through the AWS Console or CLI using the outputs from the CDK deployment.

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test categories
pytest -m unit
pytest -m integration
```

### Code Quality

```bash
# Format code
black src tests
isort src tests

# Lint code
flake8 src tests
mypy src
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Documentation

- [Architecture Design](docs/architecture.md)
- [API Documentation](docs/api.md)
- [Deployment Guide](docs/deployment.md)
- [Development Guide](docs/development.md)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.