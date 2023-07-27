import os
import sys
import shutil
import build_tools as tools

name = 'openmp'
target = 'libomp'
archs = ['ios', 'simulator']
version = '14.0.6'

root = sys.path[0]
source_code_root = f'{root}/source'
source_code_name = f'{name}-{version}.src'
source_code_path = f'{source_code_root}/{source_code_name}'
output_root = f'{root}/output/{name.lower()}'
output_library_path = f'{output_root}/lib'
output_header_path = f'{output_root}/include'
build_root = lambda arch: f'{output_root}/build-{arch}'


def clean_source_code():
    tools.remove_dir(source_code_path)
    tools.remove_dir(f'{source_code_root}/cmake')


def download_source_code():
    url_base = f'https://github.com/llvm/llvm-project/releases/download/llvmorg-{version}'
    package = f'{name}-{version}.src.tar.xz'
    tools.fetch_source_code(f'{url_base}/{package}', source_code_path)
    tools.remove_dir(f'{source_code_root}/cmake')


def clean_library(): tools.remove_dir(output_root)


def build_library():
    cmake_path = root + '/ios.toolchain.cmake'

    def do_config(arch):

        if arch == 'ios':
            platform = 'OS64'
        elif arch == 'simulator':
            platform = 'SIMULATOR64'
        else:
            raise Exception(f'Unsuppper arch {arch}!', 1000)

        cmd = f'-B {build_root(arch)} -S {source_code_path} '
        cmd += f'-DCMAKE_TOOLCHAIN_FILE={cmake_path} -DCMAKE_BUILD_TYPE=Release '
        cmd += f'-DCMAKE_INSTALL_PREFIX={build_root(arch)}/install '
        cmd += f'-DIOS_PLATFORM={platform} -DENABLE_BITCODE=1 -DENABLE_ARC=0 -DENABLE_VISIBILITY=0 '
        cmd += f'-DPERL_EXECUTABLE=$(which perl) '
        cmd += f'-DLIBOMP_ENABLE_SHARED=OFF -DLIBOMP_OMPT_SUPPORT=OFF -DLIBOMP_USE_HWLOC=OFF'
        return cmd

    def do_compile(arch):
        print(f'Start compile for {arch}!')
        build_path = build_root(arch)
        tools.remove_dir(build_path)
        tools.create_dir(build_path)

        os.system(f'cmake {do_config(arch)}')
        os.system(f'cmake --build {build_path} -j 12')
        os.system(f'cmake --build {build_path} --target install')

        library_file = f'{build_path}/install/lib/{target}.a'
        if not os.path.exists(library_file):
            raise Exception('Compile code failed!', 1001)

        # copy library
        tools.create_dir(output_library_path)
        target_library_file = f'{output_library_path}/{target}-{arch}.a'
        shutil.copy(library_file, target_library_file)

        # copy header
        header_file = f'{build_path}/install/include'
        if not os.path.exists(output_header_path):
            shutil.copytree(header_file, output_header_path)

        tools.remove_dir(build_path)
        return target_library_file

    # Build
    libraries = []
    for arch in archs:
        library = do_compile(arch)
        libraries.append(library)

    # Merge
    tools.merge_library(libraries, f'{output_library_path}/{target}.a')

    # Framework
    # tools.make_framework("OMP", output_header_path, f'{output_library_path}/{target}.a', output_root)


def build(options=[]):
    try:
        download_source_code()
        clean_library()
        build_library()
    except Exception as e:
        clean_library()
        print(f'Error: {e.args}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)
