# Contributing to AI Sales Commander

Thank you for your interest in contributing! This document provides guidelines for contributing to the project.

## Code of Conduct

Be respectful, inclusive, and professional in all interactions.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/yourusername/ai-sales-commander/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots if applicable
   - Environment details (OS, versions, etc.)

### Suggesting Features

1. Search existing feature requests
2. Create a new issue with:
   - Clear use case
   - Expected benefits
   - Implementation ideas (optional)

### Pull Requests

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/ai-sales-commander.git
   cd ai-sales-commander
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Follow existing code style
   - Write clear commit messages
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   # Backend tests
   cd backend
   pytest
   
   # Frontend tests
   cd frontend
   npm test
   ```

5. **Commit your changes**
   ```bash
   git commit -m 'feat: add amazing feature'
   ```
   
   Use conventional commits:
   - `feat:` New feature
   - `fix:` Bug fix
   - `docs:` Documentation
   - `style:` Code formatting
   - `refactor:` Code refactoring
   - `test:` Tests
   - `chore:` Maintenance

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Open a Pull Request**
   - Provide clear description
   - Link related issues
   - Add screenshots for UI changes

## Development Setup

See [SETUP.md](./SETUP.md) for detailed instructions.

## Code Style

### Python (Backend)
- Follow PEP 8
- Use `black` for formatting
- Use `ruff` for linting
- Add type hints
- Write docstrings for functions

```python
def example_function(param: str) -> Dict[str, Any]:
    """
    Brief description.
    
    Args:
        param: Description
        
    Returns:
        Description of return value
    """
    pass
```

### JavaScript/React (Frontend)
- Use ES6+ features
- Follow Airbnb style guide
- Use functional components
- Use hooks over class components
- Add JSDoc comments for complex functions

```javascript
/**
 * Example component
 * @param {Object} props - Component props
 * @returns {JSX.Element}
 */
function ExampleComponent({ prop }) {
  return <div>{prop}</div>;
}
```

## Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v --cov=app
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
docker-compose -f docker-compose.test.yml up
```

## Documentation

- Update README.md for major changes
- Update API_DOCUMENTATION.md for API changes
- Add inline comments for complex logic
- Update CHANGELOG.md

## Review Process

1. Automated tests must pass
2. Code review by maintainers
3. Address feedback
4. Merge when approved

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

## Questions?

- Open a [Discussion](https://github.com/yourusername/ai-sales-commander/discussions)
- Join our [Discord](https://discord.gg/yourinvite)

Thank you for contributing! 🎉
