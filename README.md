# utilities
Misc utilies I created to improve my life :).


## Stuffs

### chksum

Utility to create .chksum file on every directory recursively which contains name, size, modified time, and sha256sum
of every file on that directory. Running it the second time will check if any files or sub-directories have been
added / deleted / modified.

I use this as my HDD is unstable and Windows Scan Disk often fix and change the content of many files. This way I can
track exactly which file(s) were changed and I can restore them from my backup.
