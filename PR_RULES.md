# Pull Request Guidelines

## 📋 Overview

This document outlines the standards and processes for contributing to ComfyUI-HTTP. Following these guidelines ensures code quality, maintainability, and smooth collaboration.

## 🔄 Pull Request Process

### 1. Before Creating a PR

- **Fork and Clone**: Fork the repository and clone it locally
- **Branch Strategy**: Create a feature branch from `main`
  ```bash
  git checkout -b feature/your-feature-name
  # or
  git checkout -b fix/issue-description
  # or
  git checkout -b docs/documentation-update
  ```

- **Issue Reference**: Link your PR to an existing issue when applicable
- **Environment Setup**: Ensure you have the development environment properly configured

### 2. Branch Naming Convention

Use descriptive branch names following this pattern:

- `feature/add-http-auth-support` - For new features
- `fix/memory-leak-in-http-client` - For bug fixes
- `docs/update-api-documentation` - For documentation updates
- `refactor/improve-error-handling` - For code refactoring
- `test/add-integration-tests` - For test additions
- `chore/update-dependencies` - For maintenance tasks

### 3. Code Standards

#### Code Quality Requirements

- **Type Hints**: All functions must include proper type hints
- **Docstrings**: Use Google-style docstrings for all public methods
- **Error Handling**: Implement comprehensive error handling with meaningful messages
- **Logging**: Use appropriate logging levels for debugging and monitoring

#### Example Code Structure

```python
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class HTTPGetNode:
    """HTTP GET node for ComfyUI workflows.
    
    This node performs HTTP GET requests and returns the response data
    for use in ComfyUI workflows.
    
    Attributes:
        timeout: Request timeout in seconds
        max_retries: Maximum number of retry attempts
    """
    
    def __init__(self, timeout: int = 30, max_retries: int = 3) -> None:
        """Initialize the HTTP GET node.
        
        Args:
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            
        Raises:
            ValueError: If timeout or max_retries are invalid
        """
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        self.timeout = timeout
        self.max_retries = max_retries
        
    def execute(self, url: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Execute HTTP GET request.
        
        Args:
            url: Target URL for the request
            headers: Optional HTTP headers
            
        Returns:
            Dictionary containing response data and metadata
            
        Raises:
            requests.RequestException: If the request fails
            ValueError: If URL is invalid
        """
        # Implementation here
        pass
```

### 4. Testing Requirements

#### Mandatory Tests

- **Unit Tests**: Cover all new functions and methods
- **Integration Tests**: Test HTTP endpoints and workflows
- **Error Cases**: Test error conditions and edge cases
- **Performance Tests**: For performance-critical code

#### Test Structure

```python
import pytest
from unittest.mock import Mock, patch
from your_module import HTTPGetNode

class TestHTTPGetNode:
    """Test suite for HTTPGetNode."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.node = HTTPGetNode(timeout=30)
    
    def test_execute_success(self):
        """Test successful HTTP GET request."""
        # Test implementation
        pass
    
    def test_execute_timeout(self):
        """Test request timeout handling."""
        # Test implementation
        pass
    
    @pytest.mark.parametrize("invalid_url", ["", "not-a-url", None])
    def test_execute_invalid_url(self, invalid_url):
        """Test handling of invalid URLs."""
        # Test implementation
        pass
```

### 5. Documentation Requirements

- **README Updates**: Update README.md if adding new features
- **Code Comments**: Comment complex logic and algorithms
- **API Documentation**: Document public interfaces
- **Examples**: Provide usage examples for new features

### 6. Commit Message Standards

Follow [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

#### Examples:

```
feat(http): add authentication support for HTTP requests

- Add support for Bearer token authentication
- Add support for Basic authentication
- Update documentation with auth examples

Closes #123
```

```
fix(image): resolve memory leak in image processing

The image conversion was not properly releasing memory after processing
large images. This fix ensures proper cleanup of PIL Image objects.

Fixes #456
```

```
docs(readme): update installation instructions

- Add pip installation method
- Update ComfyUI integration steps
- Fix broken links in documentation
```

#### Commit Types:

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only changes
- `style`: Code style changes (formatting, semicolons, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements
- `ci`: CI/CD changes

### 7. PR Description Template

Use this template for your PR description:

```markdown
## Description
Brief description of changes made.

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Code refactoring

## Related Issues
Closes #(issue number)
Relates to #(issue number)

## Changes Made
- List of specific changes
- Use bullet points
- Be descriptive but concise

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed
- [ ] Performance impact assessed

## Screenshots/Examples
If applicable, add screenshots or code examples.

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes
```

### 8. Review Process

#### Automated Checks

All PRs must pass:
- **Code Formatting**: Black, isort
- **Linting**: Flake8, MyPy
- **Tests**: pytest with minimum 80% coverage
- **Security**: Security scanning tools

#### Manual Review

- **Code Quality**: Architecture, design patterns, best practices
- **Performance**: Impact on existing functionality
- **Security**: Potential security vulnerabilities
- **Documentation**: Clarity and completeness
- **Backward Compatibility**: Breaking changes assessment

#### Review Criteria

**Approve Criteria:**
- All automated checks pass
- Code meets quality standards
- Adequate test coverage
- Proper documentation
- No security concerns

**Request Changes Criteria:**
- Failing tests or checks
- Poor code quality
- Insufficient documentation
- Security vulnerabilities
- Breaking changes without justification

### 9. Merging Guidelines

#### Merge Requirements

- ✅ All CI checks pass
- ✅ At least one approving review from maintainer
- ✅ No unresolved conversations
- ✅ Branch is up to date with main
- ✅ All requested changes addressed

#### Merge Strategy

- **Squash and Merge**: For feature branches (default)
- **Merge Commit**: For release branches
- **Rebase and Merge**: For hotfixes (when appropriate)

### 10. Release Process

#### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `MAJOR.MINOR.PATCH`
- `MAJOR`: Breaking changes
- `MINOR`: New features (backward compatible)
- `PATCH`: Bug fixes (backward compatible)

#### Release Workflow

1. **Create Release Branch**: `release/v1.2.0`
2. **Update Version**: Update version in `pyproject.toml`
3. **Update Changelog**: Document all changes
4. **Create Release PR**: Merge to main
5. **Tag Release**: Create git tag
6. **Publish**: Publish to package registries

### 11. Contribution Recognition

All contributors are recognized in:
- **Contributors List**: GitHub contributors page
- **Changelog**: Credit in release notes
- **Documentation**: Acknowledgments section

### 12. Getting Help

- **Discussions**: Use GitHub Discussions for questions
- **Issues**: Create issues for bugs or feature requests
- **Documentation**: Check existing documentation first
- **Code Review**: Ask for specific feedback in PR comments

---

## 🛠️ Development Setup

### Quick Start

```bash
# Clone repository
git clone https://github.com/wawahuy/ComfyUI-HTTP.git
cd ComfyUI-HTTP

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest

# Format code
black .
isort .

# Lint code
flake8 .
mypy .
```

### Environment Variables

```bash
# Optional: Set up environment variables
export COMFYUI_HTTP_DEBUG=1
export COMFYUI_HTTP_LOG_LEVEL=DEBUG
```

---

**Thank you for contributing to ComfyUI-HTTP! 🚀**

*This document is living and will be updated as the project evolves.*