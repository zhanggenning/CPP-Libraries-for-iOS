import os
import sys
import build_tools as tools

name = 'lcms2'
target = 'liblcms2'
version = '2.15'

root = sys.path[0]
source_code_path = f'{root}/source/{name}-{version}'
output_root = f'{root}/output/{name.lower()}'
build_root = lambda arch: f'{output_root}/build-{arch}'


def clean_source_code(): tools.remove_dir(source_code_path)


def download_source_code():
    package = f'https://github.com/mm2/Little-CMS/releases/download/lcms{version}/{name}-{version}.tar.gz'
    tools.fetch_source_code(package, source_code_path)


def clean_library(): tools.remove_dir(output_root)


def compile_library(arch):
    if arch == 'ios':
        platform = 'arm64'
        host = 'arm-apple-darwin'
    elif arch == 'simulator':
        platform = 'x86_64'
        host = 'i386-apple-darwin'
    else:
        raise Exception(f'Unsuppper arch {arch}!', 1000)

    sdk = tools.get_sdk_path(arch)
    cc = tools.get_clang(arch)
    cflag = f'-arch {platform} -isysroot {sdk} -miphoneos-version-min=13.0 '
    config = f" --disable-shared \
                --enable-static \
                --host={host} \
                --prefix={build_root(arch)} \
                CC=\"{cc} {cflag}\""

    os.system('make distclean')
    os.system(f'./configure {config}')
    os.system('make all')
    os.system('make install')

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
        os.chdir(source_code_path)
        tools.build(compile_library, target)
    except Exception as e:
        print(f'Error: {e.args[0]}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)