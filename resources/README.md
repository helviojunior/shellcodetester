# Compiling Windows mingw, gcc and binutils

Automatic 32-bit and 64-bit Windows build of [gcc][] compiler and [mingw-w64][] runtime.

Builds are linked statically to their dependencies and provide only static runtime libraries (libstdc++, libgomp, libwinpthread and others).

Download binary build as zip archive from [latest release][] page.

To build binaries locally run `build.sh`. Make sure you have installed all necessary dependencies.

**Note:** This script was inspired from @mmozeiko work available at [original repo]

To build binaries using Docker, run:

```bash
docker run -ti --rm -v `pwd`:/output -e OUTPUT=/output -e CCACHE_DISABLE=1 -w /mnt ubuntu:22.04 /output/build.sh
```

[gcc]: https://gcc.gnu.org/
[mingw-w64]: http://mingw-w64.org/
[gdb]: https://www.gnu.org/software/gdb/
[make]: https://www.gnu.org/software/make/
[latest release]: https://github.com/helviojunior/shellcodetester/releases/latest
[original repo]: https://github.com/mmozeiko/build-gcc-mingw
