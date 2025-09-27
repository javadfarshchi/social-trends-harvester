# Contributing to Social Trends Harvester

Thank you for your interest in contributing to Social Trends Harvester! This document provides guidelines for contributing to this project.

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Legal and Ethical Requirements

**IMPORTANT**: By contributing to this project, you certify that:

1. **You have the right to contribute** the code you're submitting
2. **Your contribution does not violate any laws** or third-party rights
3. **You will not submit code that bypasses technical protection measures** (CAPTCHAs, rate limits, access controls)
4. **You will not submit code that violates website terms of service** or enables others to do so
5. **You understand this is a general-purpose framework** for legitimate, authorized data access

### Contributor Certificate of Origin

By making a contribution to this project, you certify that:

- The contribution was created in whole or in part by you and you have the right to submit it under the open source license indicated in the file; or
- The contribution is based upon previous work that, to the best of your knowledge, is covered under an appropriate open source license and you have the right under that license to submit that work with modifications, whether created in whole or in part by you; or
- The contribution was provided directly to you by some other person who certified the above and you have not modified it.
- **You understand and agree that this project and your contributions are public** and that a record of the contribution (including all personal information you submit with it) is maintained indefinitely and may be redistributed consistent with this project or the open source license(s) involved.

## How to Contribute

### Reporting Issues

Before creating an issue, please:
1. **Search existing issues** to avoid duplicates
2. **Use the issue templates** when available
3. **Provide detailed information** including:
   - Clear description of the problem or enhancement
   - Steps to reproduce (for bugs)
   - Expected vs. actual behavior
   - Environment details (OS, Python version, etc.)

### Suggesting Enhancements

We welcome enhancement suggestions! Please:
1. **Check if the enhancement aligns** with the project's compliance-focused goals
2. **Describe the use case** and why it would be valuable
3. **Consider the legal implications** of your suggestion
4. **Propose implementation approaches** if you have ideas

### Pull Requests

#### Before You Start
1. **Fork the repository** and create a feature branch
2. **Review our legal guidelines** in [LEGAL_CONSIDERATIONS.md](LEGAL_CONSIDERATIONS.md)
3. **Ensure your contribution is compliant** with our ethical standards
4. **Discuss major changes** in an issue first

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/javadfarshchi/social-trends-harvester.git
cd social-trends-harvester

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install pre-commit hooks
pre-commit install
```

#### Development Guidelines

##### Code Quality
- **Follow PEP 8** style guidelines
- **Use type hints** for all function signatures
- **Write docstrings** for all public functions and classes
- **Keep functions focused** and single-purpose
- **Use meaningful variable names**

##### Testing
- **Write tests** for all new functionality
- **Maintain test coverage** above 80%
- **Include both unit and integration tests**
- **Test error conditions** and edge cases
- **Mock external dependencies** in tests

```bash
# Run tests
pytest tests/ -v

# Check coverage
pytest --cov=src tests/

# Run linting
black src/ tests/
isort src/ tests/
flake8 src/ tests/
```

##### Documentation
- **Update README.md** if your changes affect usage
- **Add docstrings** with examples for complex functions
- **Update API documentation** for endpoint changes
- **Include configuration examples** where relevant

#### Compliance Requirements for Code Contributions

##### ✅ Allowed Contributions
- **Mock data providers** with sanitized sample data
- **User-provided data adapters** (HAR files, exports, etc.)
- **Compliance features** (robots.txt checking, rate limiting)
- **API improvements** (better error handling, validation)
- **Documentation enhancements**
- **Testing and quality improvements**
- **Performance optimizations**

##### ❌ Prohibited Contributions
- **Platform-specific scraping code** that violates ToS
- **Bypass techniques** (CAPTCHA solving, stealth mode, fingerprint spoofing)
- **Rate limit circumvention** methods
- **Cookie/session management** for unauthorized access
- **Proxy rotation** or IP masking features
- **Any code designed to evade detection** or access controls

##### Security Considerations
- **No secrets in code**: Use environment variables or config files
- **Validate all inputs**: Sanitize and validate user-provided data
- **Safe error handling**: Don't expose sensitive information in errors
- **Resource limits**: Implement appropriate limits and timeouts
- **Audit logging**: Log important actions for compliance tracking

#### Pull Request Process

1. **Create a descriptive title** that summarizes the change
2. **Fill out the PR template** completely
3. **Link related issues** using GitHub keywords (fixes #123)
4. **Ensure all checks pass**:
   - Tests pass
   - Code style checks pass
   - No security vulnerabilities detected
   - Documentation builds successfully

5. **Request review** from maintainers
6. **Address feedback** promptly and professionally
7. **Squash commits** before merging (if requested)

#### PR Template Checklist

```markdown
## Description
Brief description of changes and motivation.

## Type of Change
- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Legal and Compliance Checklist
- [ ] This contribution does not bypass technical protection measures
- [ ] This contribution does not violate any platform's terms of service
- [ ] This contribution includes appropriate compliance features
- [ ] I have the right to contribute this code
- [ ] This code follows ethical data access principles

## Testing
- [ ] New tests added for new functionality
- [ ] All tests pass locally
- [ ] Test coverage maintained or improved

## Documentation
- [ ] Documentation updated (if applicable)
- [ ] Docstrings added/updated
- [ ] README updated (if applicable)
```

## Development Standards

### Provider Development

When creating new data providers:

```python
class MyProvider(TrendsProvider):
    """Always extend the base TrendsProvider class."""
    
    @property
    def provider_name(self) -> str:
        return "my_provider"
    
    @property
    def supported_regions(self) -> List[str]:
        return ["US", "GB", "CA"]  # Only regions you actually support
    
    async def fetch_trending(self, count: int = 30, region: str = "US", **kwargs):
        # Always validate inputs
        if count < 1 or count > 60:
            raise ValidationError("Count must be between 1 and 60")
        
        # Always check compliance before making requests
        if not await check_url_compliance(url):
            raise ProviderError("URL access not compliant")
        
        # Always handle errors gracefully
        try:
            # Your implementation here
            pass
        except Exception as e:
            logger.error(f"Error in {self.provider_name}: {e}")
            raise ProviderError(f"Failed to fetch data: {e}")
```

### Error Handling Standards

```python
# Good error handling
try:
    result = await some_operation()
except ValidationError:
    raise  # Re-raise validation errors as-is
except RateLimitError:
    raise  # Re-raise rate limit errors as-is
except Exception as e:
    logger.error(f"Unexpected error in operation: {e}")
    raise ProviderError(f"Operation failed: {e}")

# Bad - don't catch and ignore errors
try:
    result = await some_operation()
except:
    pass  # This hides problems!
```

## Release Process

### Version Numbering
We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist
- [ ] All tests pass
- [ ] Documentation updated
- [ ] Legal review completed (for major changes)
- [ ] Security review completed
- [ ] Changelog updated
- [ ] Version bumped appropriately

## Community Guidelines

### Communication
- **Be respectful** and professional in all interactions
- **Focus on the code** and technical aspects, not personal characteristics
- **Provide constructive feedback** with specific suggestions
- **Be patient** with new contributors
- **Ask questions** if you're unsure about anything

### Recognition
We believe in recognizing contributors:
- Contributors are listed in our README
- Significant contributions are highlighted in release notes
- We provide recommendation letters for contributors when requested

## Getting Help

### Channels
- **GitHub Issues**: For bug reports and feature requests
- **GitHub Discussions**: For questions and general discussion

### Documentation
- [README.md](README.md): Getting started and basic usage
- [LEGAL_CONSIDERATIONS.md](LEGAL_CONSIDERATIONS.md): Legal and compliance guidance
- [SECURITY.md](SECURITY.md): Security policies and reporting
- [API Documentation](docs/): Detailed API reference

### Mentorship
New contributors are welcome! We provide:
- **Good first issues** labeled for newcomers
- **Mentorship** for first-time contributors
- **Code review feedback** to help you improve
- **Guidance** on open source best practices

---

Thank you for contributing to Social Trends Harvester! Together, we can build tools that advance legitimate research and analysis while respecting legal and ethical boundaries.
