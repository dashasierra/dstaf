<h1 align="center">Dasha Sierra (DS) Text Application Framework</h1>

<p align="center">
<a href="https://github.com/dashasierra/dstaf/actions/workflows/Version.yml"><img src="https://github.com/dashasierra/dstaf/actions/workflows/Version.yml/badge.svg?branch=master" alt="CICD Status" /></a>
<a href="https://www.python.org/downloads/"><img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.github.com%2Fdashasierra%2Fdstaf%2Fmaster%2Fpyproject.toml" alt="Python Version PEP 621"></a>
<a href="https://en.wikipedia.org/wiki/Eiffel_Forum_License"><img src="https://img.shields.io/badge/license-EFL_2.0-orange" alt="Eiffel Forum License 2.0" /></a>
<a href="#"><img src="https://custom-icon-badges.demolab.com/badge/Windows-0078D6?logo=windows10&logoColor=white" alt="Microsoft Windows Compatible" /></a>
<a href="#"><img src="https://img.shields.io/badge/Linux-FCC624?style=flat&logo=linux&logoColor=black" alt="Linux Compatible" /></a>
<a href="#"><img src="https://img.shields.io/badge/macOS-000000?style=flat&logo=apple&logoColor=white" alt="macOS Compatible" /></a>
</p>

> **Warning**
This software is not ready for development, testing, or production use.

Dasha Sierra Text Application Framework allows terminal based applications to be
created in Python, creating an abstract set of rules that should enable end
user applications to run in any terminal environment.

## Installation

```powershell
pip install git+https://github.com/dashasierra/dstaf.git
```

## Examples

### Singular Python Application

```python
from dstaf import Application


class MyApp(Application):

    def run(self):
        self.logger.info("Starting %s", self.app_name)
        counter = 0
        while self.running:
            counter += 1
            self.logger.info(counter)
            if counter == 4000:
                self.stop()
        self.logger.info("Shutting down %s", self.app_name)

    def stop(self):
        self.running = False
```

### Multiple Python Application

TODO: Still to be completed.
