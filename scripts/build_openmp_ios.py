import os
import sys
import build_tools as tools

name = 'openmp'
target = 'libomp'
version = '14.0.6'

root = sys.path[0]
source_code = f'{root}/source/{name}-{version}'
output_root = f'{root}/output/{name.lower()}'
build_root = lambda arch: f'{output_root}/build-{arch}'


def clean_source_code():
    tools.remove_dir(source_code)
    tools.remove_dir(f'{root}/source/cmake')


def download_source_code():
    package = f'https://github.com/llvm/llvm-project/releases/download/llvmorg-{version}/{name}-{version}.src.tar.xz'
    tools.fetch_source_code(package, source_code)
    tools.remove_dir(f'{root}/source/cmake')
    os.chdir(source_code)


def clean_library(): tools.remove_dir(output_root)


def compile_library(arch):
    if arch == 'ios':
        platform = 'OS64'
    elif arch == 'simulator':
        platform = 'SIMULATOR64'
    else:
        raise Exception(f'Unsuppper arch {arch}!', 1000)

    cmake_path = root + '/ios.toolchain.cmake'
    config = f"-B {build_root(arch)} \
            -S {source_code} \
            -DCMAKE_TOOLCHAIN_FILE={cmake_path} \
            -DCMAKE_BUILD_TYPE=Release \
            -DCMAKE_INSTALL_PREFIX={build_root(arch)} \
            -DIOS_PLATFORM={platform} \
            -DENABLE_BITCODE=1 \
            -DENABLE_ARC=0 \
            -DENABLE_VISIBILITY=0 \
            -DPERL_EXECUTABLE=$(which perl) \
            -DLIBOMP_ENABLE_SHARED=OFF \
            -DLIBOMP_OMPT_SUPPORT=OFF \
            -DLIBOMP_USE_HWLOC=OFF"

    build_path = build_root(arch)
    tools.remove_dir(build_path)
    tools.create_dir(build_path)

    os.system(f'cmake {config}')
    os.system(f'cmake --build {build_path} -j 12')
    os.system(f'cmake --build {build_path} --target install')

    # Install
    library = f'{build_root(arch)}/lib/{target}.a'
    if not os.path.exists(library):
        raise Exception('Compile code failed!', 1001)
    header = f'{build_root(arch)}/include'
    return tools.export(arch, library, header, output_root)


def build(options=[]):
    clean_library()
    try:
        download_source_code()
        tools.build(compile_library, target)
    except Exception as e:
        print(f'Error: {e.args}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)
