# Contributing to WAR KRS Flask

Thank you for your interest in contributing to WAR KRS Flask! 🎉

## 📋 Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Contribution Guidelines](#contribution-guidelines)
- [Pull Request Process](#pull-request-process)
- [Issue Guidelines](#issue-guidelines)
- [Coding Standards](#coding-standards)
- [Testing](#testing)
- [Documentation](#documentation)

## Code of Conduct

Please read and follow our [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all contributors.

## Getting Started

### Types of Contributions

We welcome the following types of contributions:

- 🐛 **Bug fixes**
- ✨ **New features**
- 📚 **Documentation improvements**
- 🧪 **Tests**
- 🎨 **UI/UX improvements**
- 🔧 **Configuration improvements**
- 📊 **Performance optimizations**

### Good First Issues

Look for issues labeled with:
- `good first issue`
- `help wanted`
- `documentation`
- `bug`

## Development Setup

### Prerequisites

- Python 3.12+
- Git
- Virtual environment tool (venv, conda, etc.)

### Local Setup

```bash
# 1. Fork and clone
git clone https://github.com/yourusername/warkrs-flask.git
cd warkrs-flask

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# 4. Setup pre-commit hooks
pre-commit install

# 5. Setup environment
cp .env.example .env
python generate_keys.py

# 6. Initialize database
python init_production_db.py

# 7. Run tests
python -m pytest

# 8. Start development server
python run_web.py
```

## Contribution Guidelines

### Branch Naming

Use descriptive branch names:

```
feature/user-authentication
bugfix/session-timeout-issue
docs/api-documentation
refactor/database-models
```

### Commit Messages

Follow conventional commit format:

```
type(scope): description

feat(auth): add two-factor authentication
fix(database): resolve connection timeout issue
docs(readme): update installation instructions
style(ui): improve dashboard layout
refactor(api): simplify course endpoint logic
test(auth): add unit tests for login flow
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

## Pull Request Process

### Before Submitting

1. ✅ **Create an issue** first (unless it's a minor fix)
2. ✅ **Fork** the repository
3. ✅ **Create feature branch** from `main`
4. ✅ **Write tests** for new functionality
5. ✅ **Update documentation** if needed
6. ✅ **Run all tests** and ensure they pass
7. ✅ **Run linters** and formatters

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Performance improvement
- [ ] Other (specify):

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests added/updated
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or marked as such)

## Screenshots (if applicable)

## Related Issues
Fixes #123
```

### Review Process

1. **Automated checks** must pass
2. **At least one maintainer** approval required
3. **Address feedback** promptly
4. **Squash commits** before merge (if requested)

## Issue Guidelines

### Bug Reports

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.12.0]
- Browser: [e.g. Chrome 91]

**Screenshots**
If applicable

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the proposed feature

**Problem/Use Case**
What problem does this solve?

**Proposed Solution**
How should this be implemented?

**Alternatives Considered**
Other approaches considered

**Additional Context**
Any other relevant information
```

## Coding Standards

### Python Style

- **Follow PEP 8** style guide
- **Use Black** for code formatting
- **Use isort** for import sorting
- **Use flake8** for linting
- **Type hints** where appropriate

```bash
# Format code
black app.py src/ tests/
isort app.py src/ tests/

# Check style
flake8 app.py src/ tests/
mypy app.py src/
```

### Code Quality

- **Write clear, readable code**
- **Add docstrings** to functions and classes
- **Use meaningful variable names**
- **Keep functions small** and focused
- **Follow SOLID principles**

### Example Function

```python
def register_course(user_id: int, course_code: str) -> bool:
    """
    Register a user for a specific course.
    
    Args:
        user_id: The ID of the user
        course_code: The course code to register for
        
    Returns:
        True if registration successful, False otherwise
        
    Raises:
        ValueError: If user_id or course_code is invalid
        DatabaseError: If database operation fails
    """
    if not user_id or not course_code:
        raise ValueError("user_id and course_code are required")
        
    try:
        # Implementation here
        return True
    except Exception as e:
        logger.error(f"Failed to register course {course_code} for user {user_id}: {e}")
        return False
```

## Testing

### Test Requirements

- **Unit tests** for new functions
- **Integration tests** for API endpoints
- **Test coverage** should not decrease
- **Tests should be fast** and reliable

### Test Structure

```
tests/
├── unit/
│   ├── test_auth.py
│   ├── test_models.py
│   └── test_utils.py
├── integration/
│   ├── test_api.py
│   ├── test_database.py
│   └── test_war_controller.py
└── fixtures/
    ├── sample_data.py
    └── mock_responses.py
```

### Running Tests

```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/unit/test_auth.py

# Run with coverage
python -m pytest --cov=app --cov-report=html

# Run integration tests
python -m pytest tests/integration/

# Run performance tests
python -m pytest tests/performance/
```

### Test Example

```python
import pytest
from app import create_app, db
from app.models import User

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.drop_all()

def test_user_registration(client):
    """Test user registration endpoint."""
    response = client.post('/register', data={
        'nim': '123456789',
        'name': 'Test User',
        'password': 'testpassword',
        'confirm_password': 'testpassword'
    })
    
    assert response.status_code == 302
    user = User.query.filter_by(nim='123456789').first()
    assert user is not None
    assert user.name == 'Test User'
```

## Documentation

### Types of Documentation

- **Code comments** for complex logic
- **Docstrings** for functions and classes
- **README updates** for new features
- **API documentation** for endpoints
- **User guides** for new functionality

### Documentation Standards

- **Clear and concise** writing
- **Include examples** where helpful
- **Keep up to date** with code changes
- **Use proper Markdown** formatting

### Example Documentation

```python
class Course:
    """
    Represents a course in the system.
    
    Attributes:
        course_code: The unique course identifier (e.g., 'IF25-40001')
        course_name: The human-readable course name
        class_id: The internal class identifier for registration
        
    Example:
        >>> course = Course('IF25-40001', 'Database Systems', '12345')
        >>> course.register_student(user_id=123)
        True
    """
```

## Release Process

### Version Numbering

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Checklist

- [ ] All tests passing
- [ ] Documentation updated
- [ ] Changelog updated
- [ ] Version number bumped
- [ ] Git tag created
- [ ] Release notes written

## Getting Help

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and ideas
- **Email**: Direct contact with maintainers
- **Documentation**: Check existing docs first

### Maintainer Contact

- **Primary Maintainer**: @maintainer-github-username
- **Security Issues**: security@warkrs.com
- **General Questions**: issues@warkrs.com

## Recognition

Contributors will be recognized in:
- 📜 **Contributors section** in README
- 🏆 **Release notes** for significant contributions
- 🎉 **Special mentions** for outstanding work

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (MIT License).

---

Thank you for contributing to WAR KRS Flask! 🚀
