#!/bin/bash
# Based on: https://github.com/mmozeiko/build-gcc-mingw
# Changed to build only 64 bits
#
# Standalone MinGW-w64+GCC builds for Windows, built from scratch (including all dependencies)
# natively for Windows to compile 32-bit (i686) and 64-bit (x86_64) Windows executables
#

set -eux

ZSTD_VERSION=1.5.2
GMP_VERSION=6.2.1
MPFR_VERSION=4.1.0
MPC_VERSION=1.2.1
ISL_VERSION=0.25
EXPAT_VERSION=2.4.8
BINUTILS_VERSION=2.39
GCC_VERSION=12.2.0
MINGW_VERSION=10.0.0

NAME=gcc-v${GCC_VERSION}-mingw-v${MINGW_VERSION}-x86_64
TARGET=x86_64-w64-mingw32
EXTRA_CRT_ARGS=
EXTRA_GCC_ARGS=
FINAL_NAME=mingw64

if [ -f /etc/lsb-release ]; then
  DEBIAN_FRONTEND=noninteractive apt-get update && \
    apt install --no-install-recommends -y \
    ca-certificates         \
    libgmp-dev              \
    libmpc-dev              \
    libmpfr-dev             \
    libisl-dev              \
    xz-utils                \
    texinfo                 \
    patch                   \
    bzip2                   \
    p7zip                   \
    cmake                   \
    make                    \
    curl                    \
    m4                      \
    zip                     \
    unzip                   \
    rsync                   \
    wget                    \
    gcc                     \
    g++                     \
    libz-dev                \
    g++-multilib            \
    gcc-multilib

    #Never install this packages bellow
    #g++-mingw-w64           \
    #gcc-mingw-w64
fi

function get()
{
  mkdir -p ${SOURCE} && pushd ${SOURCE}
  FILE="${1##*/}"
  if [ ! -f "${FILE}" ]; then
    echo "[`date`] Downloading ${FILE}" >> ${STATUS}
    curl -fL "$1" -o ${FILE}
    echo "[`date`] Extracting ${FILE}" >> ${STATUS}
    case "${1##*.}" in
    gz|tgz)
      tar --warning=none -xzf ${FILE}
      ;;
    bz2)
      tar --warning=none -xjf ${FILE}
      ;;
    xz)
      tar --warning=none -xJf ${FILE}
      ;;
    *)
      exit 1
      ;;
    esac
  fi
  popd
}

# by default place output in current folder
OUTPUT="${OUTPUT:-`pwd`}"

# output status
STATUS=${OUTPUT}/status.txt
echo "[`date`] Starting" > ${STATUS}

# place where source code is downloaded & unpacked
SOURCE=`pwd`/source

# place where build for specific target is done
BUILD=`pwd`/build/${TARGET}

# place where bootstrap compiler is built
BOOTSTRAP=`pwd`/bootstrap/${TARGET}

# place where build dependencies are installed
PREFIX=`pwd`/prefix/${TARGET}

# final installation folder
FINAL=`pwd`/${NAME}

# zip folder
ZIP=`pwd`/release/

echo "[`date`] Starting downloads" >> ${STATUS}
get https://github.com/facebook/zstd/releases/download/v${ZSTD_VERSION}/zstd-${ZSTD_VERSION}.tar.gz
get https://ftp.gnu.org/gnu/gmp/gmp-${GMP_VERSION}.tar.xz
get https://ftp.gnu.org/gnu/mpfr/mpfr-${MPFR_VERSION}.tar.xz
get https://ftp.gnu.org/gnu/mpc/mpc-${MPC_VERSION}.tar.gz
get https://libisl.sourceforge.io/isl-${ISL_VERSION}.tar.xz
get https://github.com/libexpat/libexpat/releases/download/R_${EXPAT_VERSION//./_}/expat-${EXPAT_VERSION}.tar.xz
get https://ftp.gnu.org/gnu/binutils/binutils-${BINUTILS_VERSION}.tar.xz
get https://ftp.gnu.org/gnu/gcc/gcc-${GCC_VERSION}/gcc-${GCC_VERSION}.tar.xz
get https://sourceforge.net/projects/mingw-w64/files/mingw-w64/mingw-w64-release/mingw-w64-v${MINGW_VERSION}.tar.bz2


#Disable ccache (if exists)
# without this the GCC/G++ present some errors loading file
export CCACHE_DISABLE=1

# Multilib symlink.
[ ! -d ${BOOTSTRAP}/ ] && mkdir -p ${BOOTSTRAP}/
[ -d ${BOOTSTRAP}/lib64 ] && rm -rf ${BOOTSTRAP}/lib64
[ ! -L ${BOOTSTRAP}/lib64 ] && ln -s ${BOOTSTRAP}/lib ${BOOTSTRAP}/lib64

# Clear old builds
[ -d ${BOOTSTRAP} ] && rm -rf ${BOOTSTRAP}
[ -d ${BUILD} ] && rm -rf ${BUILD}

echo "[`date`] Compiling cross binutils" >> ${STATUS}
mkdir -p ${BUILD}/x-binutils && pushd ${BUILD}/x-binutils
${SOURCE}/binutils-${BINUTILS_VERSION}/configure \
  --prefix=${BOOTSTRAP}                          \
  --with-sysroot=${BOOTSTRAP}                    \
  --target=${TARGET}                             \
  --disable-plugins                              \
  --disable-nls                                  \
  --disable-shared                               \
  --enable-multilib                              \
  --disable-werror
make -j`nproc`
make install
popd

echo "[`date`] Compiling cross mingw headers" >> ${STATUS}
mkdir -p ${BUILD}/x-mingw-w64-headers && pushd ${BUILD}/x-mingw-w64-headers
${SOURCE}/mingw-w64-v${MINGW_VERSION}/mingw-w64-headers/configure \
  --prefix=${BOOTSTRAP}                                           \
  --host=${TARGET}
make -j`nproc`
make install
ln -sTf ${BOOTSTRAP} ${BOOTSTRAP}/mingw
popd

echo "[`date`] Compiling cross gcc" >> ${STATUS}
mkdir -p ${BUILD}/x-gcc && pushd ${BUILD}/x-gcc
${SOURCE}/gcc-${GCC_VERSION}/configure \
  --prefix=${BOOTSTRAP}                \
  --with-sysroot=${BOOTSTRAP}          \
  --target=${TARGET}                   \
  --enable-static                      \
  --disable-shared                     \
  --disable-lto                        \
  --disable-nls                        \
  --enable-multilib                    \
  --disable-threads                    \
  --disable-werror                     \
  --disable-libgomp                    \
  --enable-languages=c,c++             \
  --enable-checking=release            \
  --enable-large-address-aware         \
  --disable-libstdcxx-pch              \
  --disable-libstdcxx-verbose          \
  --with-multilib-list=m32,m64         \
  --with-arch-32=i686                  \
  --disable-sjlj-exceptions            \
  --disable-libcc1                     \
  --disable-libgomp                    \
  --with-system-zlib                   \
  --disable-libvtv                     \
  --disable-libquadmath-support        \
  --disable-libatomic                  \
  ${EXTRA_GCC_ARGS}
make -j`nproc` all-gcc
make -j`nproc` all-target-libgcc
make install-gcc
popd

export PATH=${BOOTSTRAP}/bin:$PATH

sleep 60
echo "[`date`] Compiling cross mingw crt" >> ${STATUS}
mkdir -p ${BUILD}/x-mingw-w64-crt && pushd ${BUILD}/x-mingw-w64-crt
${SOURCE}/mingw-w64-v${MINGW_VERSION}/mingw-w64-crt/configure \
  --prefix=${BOOTSTRAP}                                       \
  --with-sysroot=${BOOTSTRAP}                                 \
  --host=${TARGET}                                            \
  --disable-dependency-tracking                               \
  --enable-warnings=0                                         \
  --enable-lib32                                              \
  --enable-lib64                                              \
  ${EXTRA_CRT_ARGS}
make -j`nproc`
make install
popd

echo "[`date`] Installing cross gcc" >> ${STATUS}
pushd ${BUILD}/x-gcc
make -j`nproc`
make install
popd


# Multilib symlink.
[ ! -d ${FINAL}/${TARGET}/ ] && mkdir -p ${FINAL}/${TARGET}/
[ -d ${FINAL}/${TARGET}/lib64 ] && rm -rf ${FINAL}/${TARGET}/lib64
[ ! -L ${FINAL}/${TARGET}/lib64 ] && ln -s ${FINAL}/${TARGET}/lib ${FINAL}/${TARGET}/lib64


echo "[`date`] Compiling zstd lib" >> ${STATUS}
mkdir -p ${BUILD}/zstd && pushd ${BUILD}/zstd
cmake ${SOURCE}/zstd-${ZSTD_VERSION}/build/cmake \
  -DCMAKE_BUILD_TYPE=Release                     \
  -DCMAKE_SYSTEM_NAME=Windows                    \
  -DCMAKE_INSTALL_PREFIX=${PREFIX}               \
  -DCMAKE_FIND_ROOT_PATH_MODE_PROGRAM=NEVER      \
  -DCMAKE_FIND_ROOT_PATH_MODE_INCLUDE=ONLY       \
  -DCMAKE_C_COMPILER=${TARGET}-gcc               \
  -DCMAKE_CXX_COMPILER=${TARGET}-g++             \
  -DZSTD_BUILD_STATIC=ON                         \
  -DZSTD_BUILD_SHARED=OFF                        \
  -DZSTD_BUILD_PROGRAMS=OFF                      \
  -DZSTD_BUILD_CONTRIB=OFF                       \
  -DZSTD_BUILD_TESTS=OFF
make -j`nproc`
make install
popd

echo "[`date`] Compiling gmp lib" >> ${STATUS}
mkdir -p ${BUILD}/gmp && pushd ${BUILD}/gmp
${SOURCE}/gmp-${GMP_VERSION}/configure \
  --prefix=${PREFIX}                   \
  --host=${TARGET}                     \
  --disable-shared                     \
  --enable-static                      \
  --enable-fat
make -j`nproc`
make install
popd

echo "[`date`] Compiling mpfr lib" >> ${STATUS}
mkdir -p ${BUILD}/mpfr && pushd ${BUILD}/mpfr
${SOURCE}/mpfr-${MPFR_VERSION}/configure \
  --prefix=${PREFIX}                     \
  --host=${TARGET}                       \
  --disable-shared                       \
  --enable-static                        \
  --with-gmp-build=${BUILD}/gmp
make -j`nproc`
make install
popd

echo "[`date`] Compiling mpc lib" >> ${STATUS}
mkdir -p ${BUILD}/mpc && pushd ${BUILD}/mpc
${SOURCE}/mpc-${MPC_VERSION}/configure \
  --prefix=${PREFIX}                   \
  --host=${TARGET}                     \
  --disable-shared                     \
  --enable-static                      \
  --with-{gmp,mpfr}=${PREFIX}
make -j`nproc`
make install
popd

echo "[`date`] Compiling isl lib" >> ${STATUS}
mkdir -p ${BUILD}/isl && pushd ${BUILD}/isl
${SOURCE}/isl-${ISL_VERSION}/configure \
  --prefix=${PREFIX}                   \
  --host=${TARGET}                     \
  --disable-shared                     \
  --enable-static                      \
  --with-gmp-prefix=${PREFIX}
make -j`nproc`
make install
popd

echo "[`date`] Compiling expat lib" >> ${STATUS}
mkdir -p ${BUILD}/expat && pushd ${BUILD}/expat
${SOURCE}/expat-${EXPAT_VERSION}/configure \
  --prefix=${PREFIX}                       \
  --host=${TARGET}                         \
  --disable-shared                         \
  --enable-static                          \
  --without-examples                       \
  --without-tests
make -j`nproc`
make install
popd

echo "[`date`] Compiling binutils" >> ${STATUS}
mkdir -p ${BUILD}/binutils && pushd ${BUILD}/binutils
${SOURCE}/binutils-${BINUTILS_VERSION}/configure \
  --prefix=${FINAL}                              \
  --with-sysroot=${FINAL}                        \
  --host=${TARGET}                               \
  --target=${TARGET}                             \
  --enable-lto                                   \
  --enable-plugins                               \
  --enable-64-bit-bfd                            \
  --disable-nls                                  \
  --enable-multilib                              \
  --disable-werror                               \
  --with-{gmp,mpfr,mpc,isl}=${PREFIX}
make -j`nproc`
make install
popd

echo "[`date`] Compiling mingw headers" >> ${STATUS}
mkdir -p ${BUILD}/mingw-w64-headers && pushd ${BUILD}/mingw-w64-headers
${SOURCE}/mingw-w64-v${MINGW_VERSION}/mingw-w64-headers/configure \
  --prefix=${FINAL}/${TARGET}                                     \
  --host=${TARGET}
make -j`nproc`
make install
ln -sTf ${FINAL}/${TARGET} ${FINAL}/mingw
popd


echo "[`date`] Compiling mingw winpthreads lib" >> ${STATUS}
mkdir -p ${BUILD}/mingw-w64-winpthreads && pushd ${BUILD}/mingw-w64-winpthreads
${SOURCE}/mingw-w64-v${MINGW_VERSION}/mingw-w64-libraries/winpthreads/configure \
  --prefix=${FINAL}/${TARGET}                                                   \
  --with-sysroot=${FINAL}/${TARGET}                                             \
  --host=${TARGET}                                                              \
  --disable-dependency-tracking                                                 \
  --disable-shared                                                              \
  --enable-static                                                               \
  --enable-multilib                                                             \
  --with-multilib-list=m32,m64
make -j`nproc`
make install
popd

echo "[`date`] Compiling gcc" >> ${STATUS}
mkdir -p ${BUILD}/gcc && pushd ${BUILD}/gcc
${SOURCE}/gcc-${GCC_VERSION}/configure \
  --prefix=${FINAL}                    \
  --with-sysroot=${FINAL}              \
  --target=${TARGET}                   \
  --host=${TARGET}                     \
  --disable-dependency-tracking        \
  --disable-nls                        \
  --enable-multilib                    \
  --disable-werror                     \
  --disable-shared                     \
  --enable-static                      \
  --enable-lto                         \
  --enable-languages=c,c++             \
  --disable-libgomp                    \
  --enable-threads=win32               \
  --enable-checking=release            \
  --enable-mingw-wildcard              \
  --enable-large-address-aware         \
  --disable-libstdcxx-pch              \
  --disable-libstdcxx-verbose          \
  --disable-win32-registry             \
  --with-tune=intel                    \
  --with-multilib-list=m32,m64         \
  --with-arch-32=i686                  \
  --disable-sjlj-exceptions            \
  --disable-libquadmath                \
  --disable-libquadmath-support        \
  --disable-libatomic                  \
  --disable-bootstrap                  \
  --disable-libssp                     \
  --with-libraries=winpthreads         \
  ${EXTRA_GCC_ARGS}                    \
  --with-{gmp,mpfr,mpc,isl,zstd}=${PREFIX}
make -j`nproc`
make install
popd

sleep 60
echo "[`date`] Compiling mingw crt" >> ${STATUS}
mkdir -p ${BUILD}/mingw-w64-crt && pushd ${BUILD}/mingw-w64-crt
${SOURCE}/mingw-w64-v${MINGW_VERSION}/mingw-w64-crt/configure \
  --prefix=${FINAL}/${TARGET}                                 \
  --with-sysroot=${FINAL}/${TARGET}                           \
  --host=${TARGET}                                            \
  --disable-dependency-tracking                               \
  --enable-warnings=0                                         \
  --enable-lib32                                              \
  --enable-lib64                                              \
  ${EXTRA_CRT_ARGS}
make -j`nproc`
make install
popd

echo "[`date`] Final tasks" >> ${STATUS}
rm -rf ${FINAL}/bin/${TARGET}-*
rm -rf ${FINAL}/bin/ld.bfd.exe ${FINAL}/${TARGET}/bin/ld.bfd.exe
rm -rf ${FINAL}/lib/bfd-plugins/libdep.dll.a
rm -rf ${FINAL}/share
[ -L ${FINAL}/${TARGET}/lib32 ] && rm -rf ${FINAL}/${TARGET}/lib32

mkdir -p ${ZIP}/${FINAL_NAME}
rsync -av ${FINAL}/* ${ZIP}/${FINAL_NAME}
[ -d ${ZIP}/${FINAL_NAME}/mingw ] && rm ${ZIP}/${FINAL_NAME}/mingw

find ${ZIP}/${FINAL_NAME} -name '*.exe' -not -path "*/lib32/*" -print0 | xargs -0 -n 8 -P 2 -i bash -c "${TARGET}-strip --strip-unneeded {} || true"
find ${ZIP}/${FINAL_NAME} -name '*.dll' -not -path "*/lib32/*" -print0 | xargs -0 -n 8 -P 2 -i bash -c "${TARGET}-strip --strip-unneeded {} || true"
find ${ZIP}/${FINAL_NAME} -name '*.o'   -not -path "*/lib32/*" -print0 | xargs -0 -n 8 -P 2 -i bash -c "${TARGET}-strip --strip-unneeded {} || true"
find ${ZIP}/${FINAL_NAME} -name '*.a'   -not -path "*/lib32/*" -print0 | xargs -0 -n 8 -P `nproc` -i bash -c "${TARGET}-strip --strip-unneeded {} || true"

echo "GCC_VERSION=${GCC_VERSION}" > ${ZIP}/${FINAL_NAME}/VERSION.txt
echo "MINGW_VERSION=${MINGW_VERSION}" >> ${ZIP}/${FINAL_NAME}/VERSION.txt
echo "BINUTILS_VERSION=${BINUTILS_VERSION}" >> ${ZIP}/${FINAL_NAME}/VERSION.txt

echo "[`date`] Creating package" >> ${STATUS}
pushd ${ZIP}
zip -r -9 ${OUTPUT}/mingw-latest.zip ${FINAL_NAME}
popd

echo "[`date`] Finished" >> ${STATUS}
if [[ -v GITHUB_WORKFLOW ]]; then
  echo "GCC_VERSION=${GCC_VERSION}" >> $GITHUB_OUTPUT
  echo "MINGW_VERSION=${MINGW_VERSION}" >> $GITHUB_OUTPUT
  echo "OUTPUT_BINARY=mingw-latest.zip" >> $GITHUB_OUTPUT
  echo "RELEASE_NAME=gcc-v${GCC_VERSION}-mingw-v${MINGW_VERSION}" >> $GITHUB_OUTPUT
fi
