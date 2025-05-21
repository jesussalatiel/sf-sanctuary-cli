# Your Awesome Project CLI

This document provides instructions on how to set up and use the command-line interface (CLI) for your project.

## Getting Started

Follow the steps below to create and activate a virtual environment and install the necessary dependencies.

### 1. Create a Virtual Environment

It's highly recommended to create a virtual environment to isolate your project dependencies. Use the following command:

```powershell
python -m venv myenv
```

This command will create a new virtual environment named myenv in your project directory.

### 2. Activate the Virtual Environment

Before installing any dependencies, you need to activate the virtual environment.

On Windows:

```powershell
myenv\Scripts\activate
```

On macOS and Linux:

```shell
source myenv/bin/activate

```

Once activated, you should see the name of your environment (myenv) in parentheses at the beginning of your terminal prompt

### 3. Install Requirements

Install all the necessary Python packages listed in the requirements.txt file using pip:

### Install Requirements

```powershell
pip install -r requirements.txt
```

This command will download and install all the libraries your project depends on.

### Installation Options

There are a couple of ways to install the CLI: globally or within the activated virtual environment for development.

#### Option A: Install CLI Globally

To make the CLI accessible from anywhere in your system, you can install it globally using pip:

```powershell
pip install .
```

This command installs your project as a package, making its entry points (like the CLI) available in your system's PATH.

#### Option B: Install Inside Environment (Editable Mode)

For development purposes, you might want to install the CLI in "editable" mode within your activated virtual environment. This allows you to make changes to the code and have them immediately reflected without needing to reinstall the package:

```powershell
pip install -e .
```

The -e flag stands for "editable".

Verifying the Installation
After installation, you can verify that the CLI is correctly installed by using pip to show information about it:

### Verifying the Installation

After installation, you can verify that the CLI is correctly installed by using pip to show information about it:

```powershell
pip show sf-users-cli
```

This command will display details about the installed package, such as its name, version, and location.

## Making Commits

This section explains how to create well-formatted Git commit messages, following conventions often enforced by tools like `gitlint`.

A good commit message typically consists of a **subject line** and an optional **body**. The subject line should be concise and summarize the change, while the body can provide more detailed context.

Here's an example:

```bash
git commit -m "feat: add login functionality with OAuth" -m "Implements authentication with OAuth 2.0 to enhance security and user experience."
```

**Explanation:**

- **`git commit -m "..."`**: This command initiates a commit with the message provided. The `-m` flag allows you to specify the commit message directly from the command line. You can use `-m` multiple times to create a subject and a body.

- **`feat: add login functionality with OAuth"` (Subject Line)**:

  - **`feat`**: This is a type indicator, signifying that this commit introduces a new feature. Common types include `feat` (feature), `fix` (bug fix), `docs` (documentation), `style` (formatting, missing semi colons, etc.; no production code change), `refactor` (code change that neither fixes a bug nor adds a feature), `test` (adding missing tests or correcting existing tests), `chore` (changes to the build process or auxiliary tools and libraries such as documentation generation).
  - **`add login functionality with OAuth`**: This is a brief description of the change. It should be informative and to the point.

- **`Implements authentication with OAuth 2.0 to enhance security and user experience.` (Body)**:
  - This is the body of the commit message, providing more context and details about the changes. It explains the _why_ behind the change.

**Best Practices (inspired by `gitlint` and common conventions):**

- **Separate subject from body with a blank line.** When using multiple `-m` flags, Git handles this automatically.
- **Limit the subject line to 50 characters.** This makes it easier to read in Git logs and on platforms like GitHub.
- **Capitalize the subject line.**
- **Do not end the subject line with a period.**
- **Use the imperative, present tense ("add" not "added", "fix" not "fixed").**
- **The body (if present) should wrap at 72 characters.**
- **Use the body to explain the _what_ and _why_ of the change, not just the _how_.**

By following these guidelines, your commit history will be cleaner and more informative, which is beneficial for collaboration and understanding the evolution of the project.

## Pre-commit Hooks Configuration

This section describes the pre-commit hooks configured for this project. Pre-commit hooks are scripts that run automatically before you commit your code, helping to ensure code quality and consistency. This project uses `pre-commit` to manage these hooks.

To use these hooks, you'll typically need to install `pre-commit`:

```powershell
pip install pre-commit
```

And then enable it in your Git repository:

```powershell
pre-commit install

```
