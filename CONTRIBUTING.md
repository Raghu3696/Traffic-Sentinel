# Contributing to Intelligent Rate Limiter

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

If you find a bug, please open an issue with:
- Clear description of the problem
- Steps to reproduce
- Expected vs actual behavior
- System information (OS, Python version, etc.)

### Suggesting Features

Feature suggestions are welcome! Please:
- Check if the feature already exists or is planned
- Describe the use case clearly
- Explain why it would be valuable

### Code Contributions

1. **Fork the Repository**
   ```bash
   git clone https://github.com/yourusername/intelligent-rate-limiter.git
   cd intelligent-rate-limiter
   ```

2. **Create a Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set Up Development Environment**
   ```bash
   ./setup.sh
   ```

4. **Make Your Changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add docstrings to functions
   - Update documentation if needed

5. **Test Your Changes**
   ```bash
   # Run the application
   python app.py
   
   # Run tests (when available)
   pytest tests/
   
   # Run the demo
   python test_traffic.py
   ```

6. **Commit Your Changes**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```
   
   Commit message format:
   - `Add: ...` for new features
   - `Fix: ...` for bug fixes
   - `Update: ...` for updates/improvements
   - `Docs: ...` for documentation changes

7. **Push and Create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```
   
   Then create a Pull Request on GitHub with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots/examples if applicable

## Development Guidelines

### Code Style
- Follow PEP 8
- Use type hints
- Write descriptive variable names
- Keep functions focused and small

### Testing
- Add tests for new features
- Ensure existing tests pass
- Test edge cases

### Documentation
- Update README.md if needed
- Add docstrings to new functions
- Update API documentation

## Areas for Contribution

Here are some areas where contributions would be especially valuable:

### Features
- [ ] Additional ML models (Random Forest, LSTM)
- [ ] Geographic-based rate limiting
- [ ] WebSocket support
- [ ] User authentication system
- [ ] Grafana dashboard integration
- [ ] Advanced analytics

### Testing
- [ ] Unit tests
- [ ] Integration tests
- [ ] Load testing scripts
- [ ] CI/CD pipeline

### Documentation
- [ ] API documentation
- [ ] Architecture diagrams
- [ ] Tutorial videos
- [ ] Blog posts/articles

### Performance
- [ ] Optimization of ML training
- [ ] Redis optimization
- [ ] Caching improvements
- [ ] Async performance

## Questions?

Feel free to:
- Open an issue for questions
- Start a discussion
- Reach out to maintainers

## Code of Conduct

Be respectful, inclusive, and professional. We're all here to learn and build together!

Thank you for contributing! 🙏
