# Purpose

This repository will be published as a package and will contain the interfaces/
specifications and some testing tools that will form the basis of the Pycelium
project. All packages designed to work within the Pycelium project will work
with these interfaces for interoperability, and the testing tools should be used
to verify specification compliance.

# Installation

```bash
pip install pycelium-specifications
```

# Use

Each specification includes a doc string introducing the specification and how
the testing works.

Each specification includes a testing tool that can be used by importing the
protocol(s) and the `check_module` function. The `check_module` function is
called by passing in a dict mapping implementation classes to protocols. For
example:

```python
from sepcifications.something import SomethingProtocol, check_module
from someimplementation import SomethingClass
import someimplementation

check_module(someimplementation, {SomethingClass: SomethingProtocol})
```

The `check_module` function runs high-level tests on the module, then it
calls `check_implementation` for each (key, value) pair in the dict parameter,
and this then runs a test suite on the implementation class. Any failures to
meet the specification will be reported.

Note that some types of implementation failures will prevent the full test suite
from running, e.g. failure to instantiate.

There are two types of specification requirements: must-haves and should-haves.
Any failure to meet a must-have requirement will be reported as an
`ImplementationError`. Any detectable failure to meet a should-have requirement
will be reported as an `ImplementationNote`. Not all should-have requirements
can be automatically detected, e.g. lack of documentation or test coverage for
additional features.

The following subpackages are currently included:
- merkletree: a specification showing what a Merkle tree should do

# ISC License

Copyleft (c) 2023 k98kurz

Permission to use, copy, modify, and/or distribute this software
for any purpose with or without fee is hereby granted, provided
that the above copyleft notice and this permission notice appear in
all copies.

Exceptions: this permission is not granted to Alphabet/Google, Amazon,
Apple, Microsoft, Netflix, Meta/Facebook, Twitter, or Disney; nor is
permission granted to any company that contracts to supply weapons or
logistics to any national military; nor is permission granted to any
national government or governmental agency; nor is permission granted to
any employees, associates, or affiliates of these designated entities.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL
WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE
AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR
CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS
OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT,
NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN
CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
