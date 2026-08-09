<!-- TODO: Complete information -->

# macos_alias

A set of tools to work with macOS aliases

## Description

macOS implements aliases (or in more recent versions of macOS, more formally bookmarks).
These are files akin to symlinks and hard links, which point to other files.
While useful, they can only normally be used by Carbon/Cocoa applications
and the Finder.

This library implements scripts which allow aliases to be manipulated
from the command line or Python scripts:
- Determine if a file is an alias
- Read the target of an alias
- Detect broken aliases
- Create an alias

## Getting Started

### Dependencies

None

### Installing

`pip install macos_alias`

### Executing program

This package makes several command line utilities available:
- `is_alias`: Determine if a file is an alias
- `alias_target`: Print out the target file pointed to by an alias
- `make_alias`: Create an alias file
- `macos_alias`: A Python script which implements all the above __and__
can read the target file of a broken alias

All of these programs implement --help, so you can learn how to use them

## Author

Richard LeBer  
richard.leber@gmail.com

## Version History

* 0.0.1
    * Initial Release

## License

This project is licensed under the MIT License - see the LICENSE.md file for details

For options, see [license.md](https://license.md/licenses/)

