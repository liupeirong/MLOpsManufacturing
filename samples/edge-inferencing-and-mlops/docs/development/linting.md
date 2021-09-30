# Linting <!-- omit in toc -->

Linting is important to keeping code repositories clean and consistent.
This sample project will be using multiple formats including yaml, python, markdown, etc.
and for this reason, the suggested linter is [Mega-Linter](https://nvuillam.github.io/mega-linter/).
Mega-Linter is an open source tool that supports 45 languages, 22 formats
with spelling and copy-paste checks.

## Table of Contents <!-- omit in toc -->

- [Configuration](#configuration)
  - [Python](#python)
  - [Markdown](#markdown)
  - [Spelling](#spelling)
  - [Other](#other)
- [Local Usage](#local-usage)
- [Pipeline Usage](#pipeline-usage)

## Configuration

We can configure Mega-Linter by creating `.mega-linter.yml` file at the root of the repository. Read more about configuration settings [here](https://nvuillam.github.io/mega-linter/configuration/).

### Python

For python files, we will be using [flake8](https://nvuillam.github.io/mega-linter/descriptors/python_flake8/).

```yml
ENABLE_LINTERS: PYTHON_FLAKE8
```

There is native support in VS Code for flake8, here are [instruction on how to enable it](https://code.visualstudio.com/docs/python/linting#_flake8).

### Markdown

For markdown documents, we will use a
[markdownlint](https://nvuillam.github.io/mega-linter/descriptors/markdown_markdownlint/) to define
specific rules for documentation linting.

```yml
ENABLE_LINTERS: MARKDOWN_MARKDOWNLINT

# We can point to a markdownlint config file in the `.mega-linter.yml` file
MARKDOWN_MARKDOWNLINT_CONFIG_FILE: .markdownlintrc
```

There is a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint) available for markdownlint.

### Spelling

We can use [cspell](https://nvuillam.github.io/mega-linter/descriptors/spell_cspell/) to check
for spelling mistakes in code and markdown files.

```yml
ENABLE_LINTERS: SPELL_CSPELL
```

There is a [VS Code extension](https://marketplace.visualstudio.com/items?itemName=streetsidesoftware.code-spell-checker)
available for cSpell.

### Other

Mega-Linter also offers support for Terraform, Kubernetes, Bash, Dockerfile, and much more.
As the project grows, we can determine the linter we would like to use
and update both this document and our `.mega-linter.yml` file.

## Local Usage

There are several options for setting up Mega-Linter:

- Install global `npm install mega-linter-runner -g`
- Install local `npm install mega-linter-runner --save-dev`
- No installation `npx mega-linter-runner`
  - You need to have [NodeJS](https://nodejs.org/en/) and [Docker](https://www.docker.com/)
    installed on your computer to run Mega-Linter locally with Mega-Linter Runner

Usage: `mega-linter-runner [OPTIONS]`

> [Mega-Linter option documentation](https://nvuillam.github.io/mega-linter/mega-linter-runner/)

## Pipeline Usage

Mega-Linter can be used in our PR & CI pipelines:

```yml
- script: |
    docker pull nvuillam/mega-linter:v4
    docker run -v $(System.DefaultWorkingDirectory):/tmp/lint nvuillam/mega-linter
  displayName: 'Code Scan using Mega-Linter'
```
