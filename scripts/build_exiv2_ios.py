import os
import sys
import build_tools as tools

name = 'exiv2'
target = 'libexiv2'
version = '0.27.7'

root = sys.path[0]
source_code = f'{root}/source/{name}-{version}'
output_root = f'{root}/output/{name.lower()}'
build_root = lambda arch: f'{output_root}/build-{arch}'


def clean_source_code(): tools.remove_dir(source_code)


def download_source_code():
    package = f'https://github.com/zhanggenning/library_script/releases/download/1.0.0/exiv2-{version}.tar.gz'
    tools.fetch_source_code(package, source_code)
    os.chdir(source_code)


def clean_library(): tools.remove_dir(output_root)


def compile_library(arch):
    if arch == 'ios':
        platform = 'OS64'
        host = 'arm64'
    elif arch == 'simulator':
        platform = 'SIMULATOR64'
        host = 'x86_64'
    else:
        raise Exception(f'Unsuppper arch {arch}!', 1000)

    sdk = tools.get_sdk_path(arch)
    cc = tools.get_clang(arch)
    cmake_path = root + '/ios.toolchain.cmake'
    config = f"--fresh \
            -DCMAKE_XCODE_ATTRIBUTE_ONLY_ACTIVE_ARCH=NO \
            -DCMAKE_TOOLCHAIN_FILE={cmake_path} \
            -DCMAKE_INSTALL_PREFIX={build_root(arch)} \
            -DCMAKE_SYSTEM_NAME=iOS \
            -DIOS_PLATFORM={platform}\
            -DCMAKE_OSX_ARCHITECTURES={host} \
            -DCMAKE_OSX_DEPLOYMENT_TARGET=13.0 \
            -DCMAKE_C_COMPILER={cc} \
            -DCMAKE_CXX_COMPILER={cc} \
            -DCMAKE_SYSROOT={sdk} \
            -DCMAKE_BUILD_TYPE=Release \
            -DBUILD_SHARED_LIBS=OFF \
            -DEXIV2_ENABLE_WEBREADY=ON \
            -DEXIV2_ENABLE_CURL=OFF  \
            -DEXIV2_ENABLE_SSH=OFF \
            -DEXIV2_BUILD_SAMPLES=OFF  \
            -DEXIV2_BUILD_EXIV2_COMMAND=OFF \
            -DEXIV2_BUILD_UNIT_TESTS=OFF \
            -DEXIV2_ENABLE_NLS=OFF \
            -DEXIV2_ENABLE_WIN_UNICODE=OFF \
            -DEXIV2_ENABLE_DYNAMIC_RUNTIME=OFF \
            -DEXIV2_ENABLE_VIDEO=OFF \
            -DEXIV2_ENABLE_WEBREADY=OFF \
            -DEXIV2_ENABLE_CURL=OFF \
            -DEXIV2_ENABLE_SSH=OFF"

    build_path = build_root(arch)
    tools.remove_dir(build_path)
    tools.create_dir(build_path)
    os.system(f'make clean')
    os.system(f'cmake {config}')
    os.system(f'make -j`sysctl -n hw.logicalcpu_max`')
    os.system(f'make install')

    # Install
    library = f'{build_root(arch)}/lib/{target}.a'
    if not os.path.exists(library):
        raise Exception('Compile code failed!', 1001)
    header = f'{build_root(arch)}/include/exiv2'
    return tools.export(arch, library, header, output_root)


def build(options=[]):
    clean_library()
    try:
        download_source_code()
        tools.build(compile_library, target)
    except Exception as e:
        print(f'Error: {e.args[0]}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)
