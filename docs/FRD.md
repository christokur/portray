# Functional Requirements for pdocs

## 1. Core Functionality

### 1.1 Documentation Generation
- FR1.1.1: The system shall generate documentation from Python module docstrings.
- FR1.1.2: The system shall support Markdown and HTML as output formats.
- FR1.1.3: The system shall traverse the abstract syntax tree to find docstrings for modules, classes, functions, methods, and variables.
- FR1.1.4: The system shall respect the `__all__` variable when determining the public interface of a module.
- FR1.1.5: The system shall support special variable `__pdocs__` to document identifiers where docstrings aren't appropriate.

### 1.2 Documentation Rendering
- FR1.2.1: The system shall render documentation with standard Markdown syntax without additional special rules.
- FR1.2.2: The system shall automatically link identifiers in docstrings to their corresponding documentation.
- FR1.2.3: The system shall include source code for modules, functions, and classes when available.
- FR1.2.4: The system shall use inheritance to infer docstrings for class members when applicable.
- FR1.2.5: The system shall include type annotation information in the reference documentation.

## 2. Command Line Interface

### 2.1 Documentation Server
- FR2.1.1: The system shall provide a command (`pdocs server`) to start an HTTP server for viewing generated documentation.
- FR2.1.2: The system shall allow configuration of port and host for the HTTP server.
- FR2.1.3: The system shall generate documentation in a temporary directory when serving locally.
- FR2.1.4: The system shall cache generated documentation and regenerate it automatically when source code is updated.
- FR2.1.5: The system shall support external linking between different packages when run as an HTTP server.

### 2.2 HTML Documentation Generation
- FR2.2.1: The system shall provide a command (`pdocs as_html`) to generate HTML documentation.
- FR2.2.2: The system shall output HTML documentation to a configurable output directory.
- FR2.2.3: The system shall provide an option to overwrite existing documentation.
- FR2.2.4: The system shall allow configuration of external links for identifiers to external modules.
- FR2.2.5: The system shall provide an option to exclude source code from the generated HTML.
- FR2.2.6: The system shall support customization of link prefixes for all generated documentation links.
- FR2.2.7: The system shall support customization through override templates.

### 2.3 Markdown Documentation Generation
- FR2.3.1: The system shall provide a command (`pdocs as_markdown`) to generate Markdown documentation.
- FR2.3.2: The system shall output Markdown documentation to a configurable output directory.
- FR2.3.3: The system shall provide an option to overwrite existing documentation.

## 3. Programmatic API

### 3.1 API Functions
- FR3.1.1: The system shall expose all command line functionality as programmatic API functions.
- FR3.1.2: The system shall provide type hints for all public API functions.
- FR3.1.3: All API functions shall accept and return only built-in Python objects.

### 3.2 Module and Package Introspection
- FR3.2.1: The system shall introspect installed modules and packages within the project's environment.
- FR3.2.2: The system shall support modules that are on the Python path or specified by file paths.
- FR3.2.3: The system shall extract public interfaces, module variables, classes, functions, and methods.

## 4. Compatibility and Performance

### 4.1 Compatibility
- FR4.1.1: The system shall be compatible with Python 3.6 and newer versions.
- FR4.1.2: The system shall work with installed modules or modules available on PYTHONPATH.

### 4.2 Performance and Security
- FR4.2.1: The system shall handle documentation generation efficiently for large codebases.
- FR4.2.2: The system shall follow secure coding practices to prevent code injection when processing docstrings.
