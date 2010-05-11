"""poster module

Support for streaming HTTP uploads, and multipart/form-data encoding

```poster.version``` is a 3-tuple of integers representing the version number.
New releases of poster will always have a version number that compares greater
than an older version of poster.
New in version 0.6."""
import poster.streaminghttp
import poster.encode

version = (0, 6, 0) # Thanks JP!
