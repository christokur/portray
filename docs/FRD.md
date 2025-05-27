# Functional Requirements for Portray

## 1. Core Functionality

### 1.1 Documentation Website Generation

- FR1.1.1: The system shall generate complete documentation websites by combining manual documentation (.md files) with auto-generated API reference documentation.
- FR1.1.2: The system shall use MkDocs for rendering Markdown documentation into HTML websites.
- FR1.1.3: The system shall use pdocs for generating API reference documentation from Python code.
- FR1.1.4: The system shall support zero-configuration operation, automatically detecting project structure and modules.
- FR1.1.5: The system shall include project README.md as the home page, creating a default one if none exists.
- FR1.1.6: The system shall automatically include .md files from the project root in the navigation.
- FR1.1.7: The system shall process documentation from configurable directories (docs, art, images, media by default).

### 1.2 Reference Documentation Generation

- FR1.2.1: The system shall generate reference documentation for Python modules using pdocs integration.
- FR1.2.2: The system shall automatically detect modules from pyproject.toml, setup.py, or directory structure.
- FR1.2.3: The system shall include type annotation information in reference documentation.
- FR1.2.4: The system shall support excluding source code from generated documentation.
- FR1.2.5: The system shall organize reference documentation in a separate "Reference" section.
- FR1.2.6: The system shall support selective module inclusion through configuration.

### 1.3 Theme and Styling

- FR1.3.1: The system shall use Material for MkDocs as the default theme.
- FR1.3.2: The system shall support all existing MkDocs themes through configuration.
- FR1.3.3: The system shall provide custom template directory support for theme customization.
- FR1.3.4: The system shall support custom CSS and JavaScript inclusion.
- FR1.3.5: The system shall provide automatic dark/light mode switching in Material theme.

## 2. Command Line Interface

### 2.1 HTML Generation

- FR2.1.1: The system shall provide a command (`portray as_html`) to generate static HTML documentation.
- FR2.1.2: The system shall output HTML to a configurable directory (default: "site").
- FR2.1.3: The system shall provide an overwrite option to replace existing documentation.
- FR2.1.4: The system shall support module filtering for selective documentation generation.

### 2.2 Development Server

- FR2.2.1: The system shall provide a command (`portray server`) to start a local development server.
- FR2.2.2: The system shall provide a command (`portray in_browser`) to start server and open browser automatically.
- FR2.2.3: The system shall support configurable host and port for the development server (default: 127.0.0.1:8000).
- FR2.2.4: The system shall support live reloading of documentation when source files change.
- FR2.2.5: The system shall generate documentation in temporary directories for development serving.

### 2.3 GitHub Pages Deployment

- FR2.3.1: The system shall provide a command (`portray on_github_pages`) to deploy documentation to GitHub Pages.
- FR2.3.2: The system shall support custom commit messages for GitHub Pages deployments.
- FR2.3.3: The system shall support force push option for deployment.
- FR2.3.4: The system shall validate documentation version before deployment.

### 2.4 Configuration Display

- FR2.4.1: The system shall provide a command (`portray project_configuration`) to display resolved project configuration.
- FR2.4.2: The system shall show all configuration sources and their precedence.

## 3. Configuration System

### 3.1 Configuration Sources

- FR3.1.1: The system shall support configuration through pyproject.toml in [tool.portray] section.
- FR3.1.2: The system shall automatically detect project metadata from pyproject.toml [tool.poetry] section.
- FR3.1.3: The system shall support setup.py parsing for legacy project compatibility.
- FR3.1.4: The system shall support runtime configuration overrides through API parameters.
- FR3.1.5: The system shall provide sensible defaults requiring no configuration for basic usage.

### 3.2 Git Repository Integration

- FR3.2.1: The system shall automatically detect repository URL from Git remotes.
- FR3.2.2: The system shall support GitHub, GitLab, and Bitbucket repository types.
- FR3.2.3: The system shall automatically generate edit URIs for source documentation.
- FR3.2.4: The system shall normalize repository URLs for consistent display.

### 3.3 MkDocs Configuration

- FR3.3.1: The system shall allow full MkDocs configuration through [tool.portray.mkdocs] section.
- FR3.3.2: The system shall support custom navigation structure override.
- FR3.3.3: The system shall support additional Markdown extensions configuration.
- FR3.3.4: The system shall merge user configuration with intelligent defaults.

### 3.4 pdocs Configuration

- FR3.4.1: The system shall allow pdocs configuration through [tool.portray.pdocs] section.
- FR3.4.2: The system shall support source code inclusion/exclusion options.
- FR3.4.3: The system shall support module filtering and selection.

## 4. Programmatic API

### 4.1 Core API Functions

- FR4.1.1: The system shall expose all CLI functionality through programmatic Python API.
- FR4.1.2: The system shall provide `as_html()` function for static HTML generation.
- FR4.1.3: The system shall provide `server()` and `in_browser()` functions for development serving.
- FR4.1.4: The system shall provide `on_github_pages()` function for deployment.
- FR4.1.5: The system shall provide `project_configuration()` function for config access.

### 4.2 API Design

- FR4.2.1: All API functions shall accept only built-in Python types as parameters.
- FR4.2.2: All API functions shall provide comprehensive type hints.
- FR4.2.3: The system shall use context managers for temporary file operations.
- FR4.2.4: The system shall provide consistent error handling across all API functions.

## 5. Build Process and Integration

### 5.1 Temporary File Management

- FR5.1.1: The system shall use temporary directories for documentation compilation.
- FR5.1.2: The system shall automatically clean up temporary files after operations.
- FR5.1.3: The system shall copy source documentation to temporary locations for processing.
- FR5.1.4: The system shall support concurrent documentation generation through proper file isolation.

### 5.2 Python Path Management

- FR5.2.1: The system shall optionally append project directory to Python path for module discovery.
- FR5.2.2: The system shall support projects with complex module structures.
- FR5.2.3: The system shall handle module imports during documentation generation.

### 5.3 Navigation Generation

- FR5.3.1: The system shall automatically generate navigation structure from file hierarchy.
- FR5.3.2: The system shall support manual navigation override through MkDocs nav configuration.
- FR5.3.3: The system shall create logical section separation between manual docs and API reference.
- FR5.3.4: The system shall apply intelligent labeling with configurable label mappings.

## 6. Dependencies and Compatibility

### 6.1 Core Dependencies

- FR6.1.1: The system shall use MkDocs Material theme as primary dependency.
- FR6.1.2: The system shall integrate with pdocs for API documentation generation.
- FR6.1.3: The system shall use Typer for command-line interface framework.
- FR6.1.4: The system shall use GitPython for repository introspection.
- FR6.1.5: The system shall support TOML configuration file parsing.

### 6.2 Python Compatibility

- FR6.2.1: The system shall be compatible with Python 3.12.7 and newer versions.
- FR6.2.2: The system shall work with Poetry-managed projects.
- FR6.2.3: The system shall support projects using pyproject.toml for configuration.

### 6.3 Development Dependencies

- FR6.3.1: The system shall support live reloading during development through livereload integration.
- FR6.3.2: The system shall provide progress indicators using yaspin for long-running operations.
- FR6.3.3: The system shall support various Markdown extensions through pymdown-extensions.

## 7. Error Handling and User Experience

### 7.1 Error Management

- FR7.1.1: The system shall provide clear error messages for configuration issues.
- FR7.1.2: The system shall gracefully handle missing or malformed configuration files.
- FR7.1.3: The system shall prevent overwriting existing documentation without explicit permission.
- FR7.1.4: The system shall provide helpful warnings for deprecated configuration options.

### 7.2 User Interface

- FR7.2.1: The system shall display ASCII art logo and success messages for completed operations.
- FR7.2.2: The system shall provide progress indicators for long-running documentation generation.
- FR7.2.3: The system shall support quiet operation modes through logging configuration.
- FR7.2.4: The system shall open browsers automatically when requested for development serving.
