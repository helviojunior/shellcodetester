# Compiling Windows mingw, gcc and binutils

Automatic 32-bit and 64-bit Windows build of [gcc][] compiler and [mingw-w64][] runtime.

Builds are linked statically to their dependencies and provide only static runtime libraries (libstdc++, libgomp, libwinpthread and others).

Download binary build as zip archive from [latest release][] page.

To build binaries locally run `build.sh`. Make sure you have installed all necessary dependencies.

**Note:** This script was inspired from @mmozeiko work available at [original repo]

To build binaries using Docker, run:

```bash
cat << EOF > start.sh
#!/bin/bash
apt update
DEBIAN_FRONTEND=noninteractive apt install --no-install-recommends -y \
    ca-certificates libgmp-dev libmpc-dev libmpfr-dev libisl-dev xz-utils texinfo patch bzip2 p7zip cmake make curl m4 gcc g++ zip unzip rsync
chmod +x /output/build.sh
/output/build.sh 64
EOF
chmod +x start.sh
docker run -ti --rm -v `pwd`:/output -e OUTPUT=/output -w /mnt ubuntu:22.04 /output/start.sh
```

[gcc]: https://gcc.gnu.org/
[mingw-w64]: http://mingw-w64.org/
[gdb]: https://www.gnu.org/software/gdb/
[make]: https://www.gnu.org/software/make/
[latest release]: https://github.com/helviojunior/shellcodetester/releases/latest
[original repo]: https://github.com/mmozeiko/build-gcc-mingw
