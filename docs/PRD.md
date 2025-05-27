# PDOCS Product Requirements Document

## 1. Introduction

This Product Requirements Document (PRD) outlines the specifications and requirements for "pdocs", a Python documentation generation tool. Pdocs is designed to discover and document the public interface of Python modules and packages, generating comprehensive documentation in both HTML and Markdown formats.

This document serves as the central reference for all stakeholders involved in the development, implementation, and maintenance of pdocs. It defines the product's purpose, features, technical requirements, and success criteria.

## 2. Product overview

Pdocs is a library and command-line program that auto-generates API documentation for Python modules by analyzing module docstrings and code structure. Unlike other documentation tools that require special syntax rules or separate documentation files, pdocs works with standard Python docstrings and automatically generates well-structured documentation.

The tool respects Python conventions such as `__all__` for defining public interfaces and provides special mechanisms like `__pdocs__` for documenting identifiers where docstrings are not appropriate. Pdocs distinguishes itself by focusing on simplicity, automation, and integration with existing Python codebases.

## 3. Goals and objectives

### 3.1 Primary goals

- Create a documentation tool that requires minimal configuration to produce high-quality documentation
- Support both HTML and Markdown output formats without requiring special syntax beyond standard Python docstrings
- Provide both a command-line interface and a programmable API for generating documentation
- Generate documentation that is accurate, complete, and reflects the actual code structure
- Make documentation generation an effortless part of the Python development workflow

### 3.2 Success metrics

- Complete documentation generation for 99% of Python modules without manual intervention
- Support for all standard Python docstring formats (Google, NumPy, reStructuredText)
- 95% or higher test coverage for core functionality
- Reduced time to generate documentation compared to alternative tools

## 4. Target audience

### 4.1 Primary users

- Python developers who need to document their libraries and packages
- Open source maintainers who want to provide comprehensive API documentation
- Technical writers who work with Python codebases

### 4.2 Secondary users

- Users of documented Python libraries who consume the generated documentation
- Development teams who need consistent documentation across multiple Python projects
- Continuous integration systems that automatically generate documentation

## 5. Features and requirements

### 5.1 Core functionality

#### 5.1.1 Documentation generation

- **REQ-1.1.1:** The system shall generate documentation from Python module docstrings.
- **REQ-1.1.2:** The system shall support both Markdown and HTML as output formats.
- **REQ-1.1.3:** The system shall traverse the abstract syntax tree to find docstrings for modules, classes, functions, methods, and variables.
- **REQ-1.1.4:** The system shall respect the `__all__` variable when determining the public interface of a module.
- **REQ-1.1.5:** The system shall support the special variable `__pdocs__` to document identifiers where docstrings aren't appropriate.

#### 5.1.2 Documentation rendering

- **REQ-1.2.1:** The system shall render documentation with standard Markdown syntax without additional special rules.
- **REQ-1.2.2:** The system shall automatically link identifiers in docstrings to their corresponding documentation.
- **REQ-1.2.3:** The system shall include source code for modules, functions, and classes when available.
- **REQ-1.2.4:** The system shall use inheritance to infer docstrings for class members when applicable.
- **REQ-1.2.5:** The system shall include type annotation information in the reference documentation.

### 5.2 Command line interface

#### 5.2.1 Documentation server

- **REQ-2.1.1:** The system shall provide a command (`pdocs server`) to start an HTTP server for viewing generated documentation.
- **REQ-2.1.2:** The system shall allow configuration of port and host for the HTTP server.
- **REQ-2.1.3:** The system shall generate documentation in a temporary directory when serving locally.
- **REQ-2.1.4:** The system shall cache generated documentation and regenerate it automatically when source code is updated.
- **REQ-2.1.5:** The system shall support external linking between different packages when run as an HTTP server.

#### 5.2.2 HTML documentation generation

- **REQ-2.2.1:** The system shall provide a command (`pdocs as_html`) to generate HTML documentation.
- **REQ-2.2.2:** The system shall output HTML documentation to a configurable output directory.
- **REQ-2.2.3:** The system shall provide an option to overwrite existing documentation.
- **REQ-2.2.4:** The system shall allow configuration of external links for identifiers to external modules.
- **REQ-2.2.5:** The system shall provide an option to exclude source code from the generated HTML.
- **REQ-2.2.6:** The system shall support customization of link prefixes for all generated documentation links.
- **REQ-2.2.7:** The system shall support customization through override templates.

#### 5.2.3 Markdown documentation generation

- **REQ-2.3.1:** The system shall provide a command (`pdocs as_markdown`) to generate Markdown documentation.
- **REQ-2.3.2:** The system shall output Markdown documentation to a configurable output directory.
- **REQ-2.3.3:** The system shall provide an option to overwrite existing documentation.

### 5.3 Programmatic API

#### 5.3.1 API functions

- **REQ-3.1.1:** The system shall expose all command line functionality as programmatic API functions.
- **REQ-3.1.2:** The system shall provide type hints for all public API functions.
- **REQ-3.1.3:** All API functions shall accept and return only built-in Python objects.

#### 5.3.2 Module and package introspection

- **REQ-3.2.1:** The system shall introspect installed modules and packages within the project's environment.
- **REQ-3.2.2:** The system shall support modules that are on the Python path or specified by file paths.
- **REQ-3.2.3:** The system shall extract public interfaces, module variables, classes, functions, and methods.

### 5.4 Compatibility and performance

#### 5.4.1 Compatibility

- **REQ-4.1.1:** The system shall be compatible with Python 3.6 and newer versions.
- **REQ-4.1.2:** The system shall work with installed modules or modules available on PYTHONPATH.

#### 5.4.2 Performance and security

- **REQ-4.2.1:** The system shall handle documentation generation efficiently for large codebases.
- **REQ-4.2.2:** The system shall follow secure coding practices to prevent code injection when processing docstrings.

## 6. User stories and acceptance criteria

### 6.1 Documentation generation

#### US-101: Generate documentation from docstrings
**As a** Python developer,  
**I want to** generate documentation directly from my code's docstrings,  
**So that** I can maintain documentation alongside code in a single location.

**Acceptance criteria:**
- The tool extracts docstrings from modules, classes, methods, and functions
- Documentation reflects the most recent state of the code
- All public members of a module are included in the documentation

#### US-102: Control public interface documentation
**As a** library author,  
**I want to** explicitly control which parts of my code are documented as public,  
**So that** internal implementation details aren't exposed in the documentation.

**Acceptance criteria:**
- The `__all__` variable in a module is respected to determine what's documented
- Members not in `__all__` are excluded from documentation by default
- The special `__pdocs__` variable can be used to override documentation behavior

#### US-103: Document variables and attributes
**As a** Python developer,  
**I want to** document module variables and class attributes,  
**So that** users understand all parts of my API.

**Acceptance criteria:**
- Module-level variables are documented
- Class attributes are documented
- Instance variables are documented
- Documentation includes type information when available

### 6.2 Documentation formats

#### US-201: Generate HTML documentation
**As a** Python developer,  
**I want to** generate HTML documentation from my Python code,  
**So that** users can browse my library's API in a web browser.

**Acceptance criteria:**
- Documentation is generated in HTML format
- HTML output is valid and renders correctly in modern browsers
- Source code is included in the documentation when available
- Output directory is configurable

#### US-202: Generate Markdown documentation
**As a** Python developer,  
**I want to** generate Markdown documentation from my Python code,  
**So that** I can include API documentation in GitHub or other Markdown-based platforms.

**Acceptance criteria:**
- Documentation is generated in Markdown format
- Markdown is well-formatted and follows standard conventions
- Output directory is configurable
- Generated Markdown can be integrated with existing documentation

#### US-203: Preview documentation locally
**As a** Python developer,  
**I want to** preview generated documentation using a local server,  
**So that** I can check documentation before publishing it.

**Acceptance criteria:**
- A local HTTP server can be started with a simple command
- Documentation is automatically regenerated when source files change
- Server host and port are configurable
- Documentation is served from a temporary directory

### 6.3 API usage

#### US-301: Use programmatic API
**As a** Python developer,  
**I want to** use pdocs as a library in my Python scripts,  
**So that** I can automate documentation generation and integrate it with my build process.

**Acceptance criteria:**
- All command-line functionality is available through the Python API
- API functions are well-documented with type hints
- API returns standard Python objects that can be processed further
- API handles errors gracefully with descriptive error messages

#### US-302: Customize documentation templates
**As a** technical writer,  
**I want to** customize the templates used for documentation generation,  
**So that** the documentation matches my organization's style and branding.

**Acceptance criteria:**
- Templates can be overridden by specifying a custom template directory
- Template customization doesn't require modifying the pdocs source code
- Documentation includes instructions for template customization
- Changes to templates are reflected in the generated documentation

#### US-303: Exclude source code from documentation
**As a** library developer,  
**I want to** exclude source code from the generated documentation,  
**So that** I can reduce the size of the documentation and focus on the API.

**Acceptance criteria:**
- An option is available to exclude source code from HTML documentation
- When source code is excluded, documentation still includes all other API information
- Source code exclusion is configurable via both CLI and API

### 6.4 Edge cases and special scenarios

#### US-401: Handle malformed docstrings
**As a** Python developer,  
**I want to** generate documentation even when some docstrings are malformed,  
**So that** documentation generation doesn't fail completely due to minor issues.

**Acceptance criteria:**
- The system handles malformed docstrings gracefully
- Warnings are issued for malformed docstrings
- Documentation generation continues despite encountering issues
- The resulting documentation clearly indicates when docstrings are malformed

#### US-402: Document imported members
**As a** Python developer,  
**I want to** properly document imported members in my modules,  
**So that** users understand which parts of the API are imported from elsewhere.

**Acceptance criteria:**
- Imported members included in `__all__` are properly documented
- Documentation indicates when a member is imported from another module
- Links to the original module are provided when possible

#### US-403: Generate documentation for large codebases
**As a** maintainer of a large Python project,  
**I want to** generate documentation for my entire codebase efficiently,  
**So that** documentation generation doesn't become a bottleneck in my workflow.

**Acceptance criteria:**
- Documentation generation scales efficiently with codebase size
- Memory usage remains reasonable for large projects
- Generation time for large projects is acceptable
- Progress indication is provided for long-running generation tasks

## 7. Technical requirements/stack

### 7.1 Development environment

- Python 3.6+ required for development and usage
- Poetry for dependency management and packaging
- pytest for testing
- mypy for static type checking
- flake8 for linting
- black for code formatting
- isort for import sorting

### 7.2 Dependencies

- Markdown: For Markdown processing
- Mako: For HTML templating
- hug: For CLI command structure
- docstring_parser: For parsing various docstring formats

### 7.3 Compatibility requirements

- Must work with Python 3.6 and newer versions
- Must support multiple operating systems (Linux, macOS, Windows)
- Must work with modules installed in the current environment or available on PYTHONPATH
- Must support various docstring styles (Google, NumPy, reStructuredText)

## 8. Design and user interface

### 8.1 Command line interface design

The command line interface should follow these design principles:
- Consistent command structure using sub-commands
- Clear help messages and documentation
- Sensible defaults for all options
- Progress indication for long-running operations
- Descriptive error messages

The primary commands will be:
```
pdocs server [modules...] [--port PORT] [--host HOST]
pdocs as_html [modules...] [--output-dir DIR] [--overwrite]
pdocs as_markdown [modules...] [--output-dir DIR] [--overwrite]
```

### 8.2 HTML documentation design

The HTML documentation should:
- Be responsive and work well on various screen sizes
- Use a clean, professional design
- Provide easy navigation between modules, classes, and functions
- Include a search function
- Use syntax highlighting for code examples
- Show inheritance relationships between classes
- Include type annotation information
- Provide links between related components

### 8.3 Markdown documentation design

The Markdown documentation should:
- Follow standard Markdown conventions
- Be organized hierarchically by module, then class, then method/function
- Include proper heading levels for easy navigation
- Use code blocks with syntax highlighting
- Include links between related components
- Be compatible with common Markdown processors (GitHub, MkDocs, etc.)

## 9. Release and deployment

### 9.1 Versioning

- The project will follow semantic versioning (MAJOR.MINOR.PATCH)
- Breaking changes will increment the MAJOR version
- New features without breaking changes will increment the MINOR version
- Bug fixes and minor improvements will increment the PATCH version

### 9.2 Distribution

- The package will be distributed via PyPI
- Installation will be possible via pip, poetry, and pipenv
- Documentation will be available online and included in the package
- Source code will be available on GitHub

### 9.3 Testing and quality assurance

- All features must have corresponding unit tests
- Test coverage should be maintained at 80% or higher
- Integration tests must verify end-to-end functionality
- Performance benchmarks must be established for documentation generation

## 10. Future considerations

### 10.1 Potential enhancements

- Support for additional output formats (PDF, reStructuredText)
- Integration with continuous integration systems
- Plugin system for custom documentation processors
- Support for documenting C extensions
- Interactive documentation with runnable code examples

### 10.2 Integration opportunities

- Integration with GitHub Pages for automatic documentation publishing
- Integration with Read the Docs for hosted documentation
- Integration with code editors for inline documentation preview
- Integration with build systems like Tox, Nox, or Make

## 11. Appendices

### 11.1 Glossary

- **Docstring**: A string literal that occurs as the first statement in a module, function, class, or method definition in Python.
- **AST**: Abstract Syntax Tree, a tree representation of the abstract syntactic structure of source code.
- **Markdown**: A lightweight markup language with plain-text formatting syntax.
- **HTML**: HyperText Markup Language, the standard markup language for documents designed to be displayed in a web browser.
- **API**: Application Programming Interface, a set of functions and procedures allowing the creation of applications that access the features or data of an operating system, application, or other service.
- **CLI**: Command Line Interface, a means of interacting with a computer program where the user issues commands to the program in the form of successive lines of text.

### 11.2 References

- Python documentation: https://docs.python.org/
- PEP 257 (Docstring Conventions): https://www.python.org/dev/peps/pep-0257/
- PEP 484 (Type Hints): https://www.python.org/dev/peps/pep-0484/
- Markdown Specification: https://daringfireball.net/projects/markdown/syntax
