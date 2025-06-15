# Contributing Guidelines

Thank you for your interest in contributing to DSTaf! To maintain a high-quality codebase and a welcoming community, please follow the guidelines below.

## Code Review Process

- All contributions must be reviewed and approved by the code owners before being merged.
- Ensure your changes are well-documented, tested, and adhere to the project's coding standards.
- When submitting a pull request, provide a clear description of the changes and reference any relevant issues.

## Code Standards

To ensure consistency and maintainability, please adhere to the following code standards:

- **Code Style:** Follow the project's coding style and conventions.
  - Class names must be CamelCase.
  - Function names and variables must be lower_case.
  - Constants and Enumerator names must be UPPER_CASE.
- **Formatting:** Use consistent indentation, spacing, and line length limits. It is best you run [autopep8](https://github.com/hhatto/autopep8) against your code contributions before committing to a branch.
- **Naming Conventions:** Use clear, meaningful names for variables, functions, and classes. Follow any naming conventions established in the repository.
- **Testing:** Write unit tests for new features or bug fixes. Ensure existing tests continue to pass.
- **Documentation:** Provide clear comments for complex logic and update relevant documentation as needed.
- **Security:** Absolutely no hard-coded credentials, input validation issues, and other security vulnerabilities.

## Code of Conduct

All contributors are expected to adhere to our [Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project, you agree to create a respectful and inclusive environment for everyone.

## Getting Started

1. Fork and Clone the repository locally. (Only authorised contributors can open branches on this repository directly)
2. Create a new branch for your changes.
3. Commit meaningful changes with clear commit messages.
4. Ensure code standards are met and tests pass.
6. Submit a pull request for review.
7. Your pull request must pass version semaphore standards, pylint tests, and imports must be optimised before a code owner will review your pull request.


Thank you for contributing!
