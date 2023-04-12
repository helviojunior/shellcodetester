
```bash
wget -O /tmp/binutils.7z https://razaoinfo.dl.sourceforge.net/project/mingw-w64/Toolchains%20targetting%20Win64/Personal%20Builds/mingw-builds/8.1.0/threads-win32/seh/x86_64-8.1.0-release-win32-seh-rt_v6-rev0.7z
7z x binutils.7z -o/tmp/ -r -aoa
p=$(pwd)
cd /tmp/
zip -r -9 mingw64_8.1.zip mingw64/*
cd $p
cp /tmp/mingw64_8.1.zip ./resources/
```