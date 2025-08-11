# Json_To_Many

[![PyPI Version](https://img.shields.io/pypi/v/json_to_many.svg)](https://pypi.org/project/json_to_many/)
[![License](https://img.shields.io/pypi/l/json_to_many.svg)](https://github.com/ananthanandanan/Json_To_Many/blob/main/LICENSE)
[![Build Status](https://github.com/ananthanandanan/Json_To_Many/actions/workflows/ci.yml/badge.svg)](https://github.com/ananthanandanan/Json_To_Many/actions)

## Overview

In today's interconnected digital ecosystem, **JSON has become the lingua franca of data exchange**. From REST APIs to configuration files, from database exports to IoT sensor data, JSON is everywhere. However, while JSON excels at machine-to-machine communication, different tools, platforms, and use cases often require data in specific formats.

**Json_To_Many** bridges this gap by providing seamless conversion from JSON to multiple output formats. Whether you're a developer documenting an API, a data analyst preparing reports, or a content creator transforming data for different platforms, this package eliminates the friction of manual format conversion.

### The Problem We Solve

- **Developers** need to transform API responses for documentation (Markdown)
- **Data analysts** require CSV exports for spreadsheet analysis
- **DevOps teams** need XML for legacy system integration
- **Content creators** want structured data in readable formats
- **Business users** need reports generated from JSON APIs

**Json_To_Many** makes these transformations effortless, allowing you to focus on what matters most: your data and insights.

The project is managed using **uv** for dependency management and packaging, and **Ruff** is used for linting to ensure code quality.

## Features

### Current Supported Formats

- **JSON to Markdown**
- **JSON to XML**
- **JSON to CSV**

### Upcoming Supported Formats

- **JSON to TSV**
- **JSON to SQL**
- **JSON to YAML**
- **JSON to HTML**
- **JSON to PDF**

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
  - [Converting JSON to Markdown](#converting-json-to-markdown)
  - [Converting JSON to XML](#converting-json-to-xml)
  - [Converting JSON to CSV](#converting-json-to-csv)
- [Examples](#examples)
- [Development](#development)
  - [Setting Up a Development Environment](#setting-up-a-development-environment)
  - [Coding Guidelines](#coding-guidelines)
- [Contributing](#contributing)
- [Roadmap](#roadmap)
- [License](#license)
- [Contact](#contact)

## Installation

Install **Json_To_Many** using `pip`:

```bash
pip install json_to_many
```

Or, if you prefer using uv:

```bash
uv add json_to_many
```

## Quick Start

```python
from json_to_many import convert

# Convert JSON string to Markdown and save to 'output.md'
json_string = '{"title": "Sample Document", "content": "This is a sample."}'
convert(json_string, 'markdown', output_file='output.md')

# Convert JSON file to XML and get the converted data
xml_data = convert('data.json', 'xml', return_data=True)
print(xml_data)
```

## Usage

### Converting JSON to Markdown

**From a JSON File:**

```python
from json_to_many import convert

# Convert JSON file to Markdown and save to 'output.md'
convert('data.json', 'markdown', output_file='output.md')
```

**From a JSON String:**

```python
from json_to_many import convert

json_string = '{"title": "Sample Document", "content": "This is a sample."}'

# Convert JSON string to Markdown and get the converted data
markdown_data = convert(json_string, 'markdown', return_data=True)
print(markdown_data)
```

**Sample Output:**

```markdown
# title

Sample Document

# content

This is a sample.
```

### Converting JSON to XML

**From a Python Dictionary:**

```python
from json_to_many import convert

json_data = {
    "note": {
        "to": "Alice",
        "from": "Bob",
        "message": "Hello, Alice!"
    }
}

# Convert JSON data to XML and save to 'note.xml'
convert(json_data, 'xml', output_file='note.xml')
```

**Get Converted XML Data Without Saving:**

```python
xml_data = convert(json_data, 'xml', return_data=True)
print(xml_data)
```

**Sample Output:**

```xml
<root><note><to>Alice</to><from>Bob</from><message>Hello, Alice!</message></note></root>
```

### Converting JSON to CSV

**From a Python List of Dictionaries:**

```python
from json_to_many import convert

json_data = [
    {"name": "Alice", "age": 30, "city": "New York"},
    {"name": "Bob", "age": 25, "city": "Los Angeles"}
]

# Convert JSON data to CSV and save to 'data.csv'
convert(json_data, 'csv', output_file='data.csv')
```

**Get Converted CSV Data Without Saving:**

```python
csv_data = convert(json_data, 'csv', return_data=True)
print(csv_data)
```

**Sample Output:**

```csv
name,age,city
Alice,30,New York
Bob,25,Los Angeles
```

**Note:** The CSV converter automatically flattens nested JSON structures and handles complex data types appropriately.

## Examples

The `examples` directory contains sample scripts and data to help you get started.

- **JSON to Markdown Conversion**: [json_to_markdown_example.py](examples/json_to_markdown_example.py)
- **JSON to XML Conversion**: [json_to_xml_example.py](examples/json_to_xml_example.py)
- **JSON to CSV Conversion**: [json_to_csv_example.py](examples/json_to_csv_example.py)

### Running Examples

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/ananthanandanan/Json_To_Many.git
   cd Json_To_Many/examples
   ```

2. **Install Dependencies** (for development):

   ```bash
   uv sync
   ```

   Or install the package directly:

   ```bash
   pip install json_to_many
   ```

3. **Run an Example Script**:

   ```bash
   uv run python json_to_markdown_example.py
   # or if installed globally:
   python json_to_markdown_example.py
   ```

## Development

The project uses **uv** for dependency management and packaging, and **Ruff** for linting and code style enforcement.

### Setting Up a Development Environment

1. **Fork the Repository**:

   Click the "Fork" button at the top right corner of the repository page.

2. **Clone Your Fork**:

   ```bash
   git clone https://github.com/ananthanandanan/Json_To_Many.git
   cd Json_To_Many
   ```

3. **Install Dependencies**:

   ```bash
   uv sync
   ```

4. **Run Tests**:

   ```bash
   uv run pytest
   ```

5. **Check Code Quality with Ruff**:

   ```bash
   uv run ruff check .
   ```

6. **Build the Package**:

   ```bash
   uv build
   ```

### Coding Guidelines

- **Code Style**: Follow PEP 8 guidelines. Use **Ruff** for linting and code style enforcement.
- **Testing**: Write unit tests for new features and bug fixes.
- **Documentation**: Update documentation and examples to reflect changes.

## Contributing

Contributions are welcome! Here's how you can help:

- **Report Bugs**: If you find a bug, please report it by opening an issue.
- **Suggest Features**: Have an idea for a new feature? Feel free to share it.
- **Submit Pull Requests**: If you'd like to fix a bug or implement a feature, you're welcome to contribute code.

### Guidelines for Contributing

1. **Create an Issue**:

   Before starting work on a feature or bug fix, please create an issue to discuss it.

2. **Branch Naming**:

   Use descriptive branch names, e.g., `feature/json-to-yaml` or `bugfix/fix-xml-output`.

3. **Pull Requests**:

   - Include a clear description of the changes.
   - Reference the issue number.
   - Ensure all tests pass and code quality checks are successful.

4. **Code Quality**:

   - Run `uv run pytest` to ensure all tests pass.
   - Run `uv run ruff check .` to ensure code style compliance.

## Roadmap

Our vision is to transform **Json_To_Many** into the **Swiss Army Knife of Data Conversion** - the essential tool for every developer, data analyst, and content creator working with structured data.

### 🎯 **Phase 1: Foundation Enhancement** (Current)

- ✅ **Core Formats**: JSON → Markdown, XML, CSV
- ✅ **Clean Architecture**: Extensible converter pattern
- ✅ **Developer Experience**: Simple API and comprehensive documentation

### 🚀 **Phase 2: Bi-Directional Hub** (Q1-Q2 2025)

- 🔄 **Reverse Conversion**: Support Any → JSON (CSV → JSON, XML → JSON, etc.)
- 🔄 **Cross-Format**: Direct Any → Any conversion without JSON intermediary
- 📊 **New Formats**: YAML, TOML, HTML, TSV support
- 🛡️ **Schema Validation**: JSON Schema integration for type-aware conversion

### 🎨 **Phase 3: Smart Templates & Customization** (Q2-Q3 2025)

- 📝 **Template Engine**: Customizable output formatting
  - Executive summary templates for business reports
  - API documentation templates for developers
  - Data visualization templates for analysts
- 🎯 **Context-Aware Conversion**: Smart formatting based on data structure
- 🔧 **Plugin Architecture**: Custom converter development framework

### 🤖 **Phase 4: Intelligence & Automation** (Q3-Q4 2025)

- 🧠 **AI-Powered Enhancement**: Intelligent structure detection and optimization
- 📈 **Auto-Insights**: Generate summaries and key insights during conversion
- 🔍 **Data Quality**: Automatic validation and cleaning suggestions
- ⚡ **Streaming Support**: Efficient processing of large datasets

### 🌐 **Phase 5: Ecosystem Integration** (Q4 2025)

- 🖥️ **CLI Tool**: Powerful command-line interface for automation
- 🌍 **Web API**: Cloud service for universal access
- 🔌 **Platform Integrations**:
  - Notion, Confluence, SharePoint (documentation)
  - Slack, Discord, Teams (communication)
  - Tableau, Power BI (visualization)
  - Salesforce, HubSpot (CRM)
- 📊 **Data Pipeline Integration**: Apache Airflow, Prefect, Dagster connectors

### 🎯 **Long-term Vision: The Data Transformation Platform**

Transform Json_To_Many into a comprehensive data transformation ecosystem where:

- **Developers** automate documentation generation from APIs
- **Data Teams** build no-code transformation pipelines
- **Business Users** create reports without technical barriers
- **Organizations** standardize data exchange across all tools

### 📈 **Success Metrics**

- **Developer Adoption**: 10K+ GitHub stars, 100K+ monthly downloads
- **Format Coverage**: Support for 15+ input/output formats
- **Enterprise Ready**: SOC 2 compliance, enterprise support
- **Community Growth**: 50+ community-contributed plugins

---

_For detailed technical specifications, implementation timelines, and architecture diagrams, see our comprehensive [**ROADMAP.md**](ROADMAP.md)._

_Want to contribute to this roadmap? Check out our [Contributing](#contributing) guidelines or open an issue to discuss new ideas!_

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please open an issue or contact [K N Anantha nandanan](mailto:ananthanandanan@gmail.com).

---
