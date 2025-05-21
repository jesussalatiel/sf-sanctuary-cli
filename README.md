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
