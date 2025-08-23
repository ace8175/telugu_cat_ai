# Contributing to Telugu AI Chat Assistant 🤝

Thank you for your interest in contributing to the Telugu AI Chat Assistant! We welcome contributions from the community to help make this project better.

## Code of Conduct

By participating in this project, you agree to abide by our Code of Conduct:
- Be respectful and inclusive
- Welcome diverse perspectives
- Focus on constructive feedback
- Be patient with newcomers

## Getting Started

### Prerequisites
- Python 3.8+
- Git
- Supabase account (for database)
- Basic understanding of Streamlit and Python

### Development Environment Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/your-username/telugu-ai-chat.git
   cd telugu-ai-chat
   ```

2. **Set up Python Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate on Windows
   venv\Scripts\activate
   
   # Activate on macOS/Linux
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

3. **Database Setup**
   - Create a Supabase account at [supabase.com](https://supabase.com)
   - Create a new project
   - Run the SQL schema from README.md in the SQL Editor
   - Copy your project URL and anon key to `.env` file

4. **Environment Variables**
   ```bash
   # Copy example file
   cp .env.example .env
   
   # Edit .env with your credentials
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

## Contribution Workflow

### 1. Find an Issue
- Check the [GitHub Issues](https://github.com/your-username/telugu-ai-chat/issues) for open tasks
- Look for issues labeled "good first issue" if you're new
- Or create a new issue if you have a feature request or bug report

### 2. Create a Branch
```bash
# Sync with main branch
git checkout main
git pull origin main

# Create feature branch
git checkout -b feature/your-feature-name
# or
git checkout -b fix/issue-number-description
```

### 3. Make Your Changes
Follow our coding standards and make your changes. Test thoroughly.

### 4. Commit Your Changes
```bash
# Add changes
git add .

# Commit with descriptive message
git commit -m "feat: add Telugu voice recognition support"
# or
git commit -m "fix: resolve database connection issue #123"
```

### 5. Push and Create Pull Request
```bash
# Push to your fork
git push origin feature/your-feature-name

# Create PR on GitHub from your fork to main repository
```

## Coding Standards

### Python Style Guide
- Follow [PEP 8](https://pep8.org/) guidelines
- Use meaningful variable and function names
- Add docstrings for all functions and classes
- Keep functions focused and single-purpose

### File Structure
```
telugu-ai-chat/
├── app.py              # Main Streamlit application
├── ai_services.py      # AI model services and logic
├── database.py         # Database operations
├── news_service.py     # News fetching and processing
├── utils.py           # Utility functions
├── config.py          # Configuration management
└── tests/             # Test files
```

### Documentation
- Update README.md if your changes affect setup or usage
- Add comments for complex logic
- Document new environment variables
- Update API documentation if applicable

## Testing

### Running Tests
```bash
# Run all tests
python -m pytest

# Run specific test file
python -m pytest tests/test_database.py

# Run with coverage
python -m pytest --cov=.
```

### Writing Tests
- Write tests for new functionality
- Include both unit tests and integration tests
- Test edge cases and error conditions
- Mock external dependencies (APIs, databases)

## Pull Request Process

### Before Submitting
- [ ] Code follows style guidelines
- [ ] Tests pass locally
- [ ] Documentation updated
- [ ] No breaking changes
- [ ] Commit messages are descriptive

### PR Description Template
```markdown
## Description
Brief description of changes

## Related Issues
Fixes #123, Related to #456

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Documentation update
- [ ] Refactoring
- [ ] Performance improvement

## Testing
- [ ] Unit tests added
- [ ] Integration tests added
- [ ] Manual testing performed

## Screenshots (if UI changes)
```

## Issue Reporting

When reporting issues, please include:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- Environment details (OS, Python version, etc.)
- Error messages or screenshots

## Areas for Contribution

### High Priority
- Telugu language model improvements
- Voice recognition accuracy
- News source integration
- Performance optimization
- Security enhancements

### Good First Issues
- UI/UX improvements
- Documentation updates
- Test coverage expansion
- Bug fixes

## Getting Help

- Check existing documentation and issues first
- Join our [Discord/Slack community] (if available)
- Ask questions in GitHub Discussions
- Email: support@teluguai.com

## Recognition

All contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Given credit for their work

Thank you for contributing to making Telugu AI more accessible! 🎉

---
*This contributing guide is adapted from best practices and may evolve as the project grows.*
