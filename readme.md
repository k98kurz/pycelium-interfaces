# Purpose

This repository will be published as a package and will contain the interfaces
and some testing tools that will form the basis of the Pycelium project. All
packages designed to work within the Pycelium project will work with these
interfaces for interoperability, and the testing tools should be used to verify
interface compliance.

# Use

Each interface subpackage includes a testing tool that can be used by importing
the protocol(s) and the `check_module` function. The `check_module` function is
called by passing in a dict mapping implementation classes to protocols. For
example:

```python
from .interfaces.something import SomethingProtocol, check_module
from .someimplementation import SomethingClass

check_module({
    SomethingClass: SomethingProtocol
})
```

The `check_module` function calls `check_implementation` for each (key, value)
pair in the dict parameter, and this then runs a test suite on the
implementation class.

The following subpackages are currently included:
- merkletree: a protocol showing what a Merkle tree should do and unit tests
