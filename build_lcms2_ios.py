import os
import sys
import shutil
import build_tools as tools

name = 'lcms2'
target = 'liblcms2'
archs = ['simulator', 'ios']
version = '2.15'

root = sys.path[0]
source_code_root = f'{root}/source'
source_code_name = f'{name}-{version}'
source_code_path = f'{source_code_root}/{source_code_name}'
output_root = f'{root}/output/{name.lower()}'
output_library_path = f'{output_root}/lib'
output_header_path = f'{output_root}/include'
build_root = lambda arch: f'{output_root}/build-{arch}'

def clean_source_code(): tools.remove_dir(source_code_path)


def download_source_code():
    url_base = 'https://github.com/mm2/Little-CMS/releases/download'
    package = f'lcms{version}/{name}-{version}.tar.gz'
    tools.fetch_source_code(f'{url_base}/{package}', source_code_path)


def clean_library(): tools.remove_dir(output_root)


def build_library():
    os.chdir(source_code_path)

    def do_config(arch):
        clang_root = '/Applications/Xcode.app/Contents/Developer'
        if arch == 'ios':
            platform = 'arm64'
            host = 'arm-apple-darwin'
            devroot = f'{clang_root}/Platforms/iPhoneOS.platform/Developer'
            sdkroot = f'{devroot}/SDKs/iPhoneOS.sdk'
        elif arch == 'simulator':
            platform = 'x86_64'
            host = 'i386-apple-darwin'
            devroot = f'{clang_root}/Platforms/iPhoneSimulator.platform/Developer'
            sdkroot = f'{devroot}/SDKs/iPhoneSimulator.sdk'
        prefix = build_root(arch)

        cmd = f'./configure --disable-shared --enable-static --host=\"{host}\" --prefix=\"{prefix}\" '
        cc = f'{clang_root}/Toolchains/XcodeDefault.xctoolchain/usr/bin/clang'
        cflag = f'-arch {platform} -isysroot {sdkroot} -miphoneos-version-min=13.0 '
        cmd += f'CC=\"{cc} {cflag}\"'
        return cmd

    def do_compile(arch):
        os.system('make distclean')
        os.system(do_config(arch))
        os.system('make all')
        os.system('make install')

        library_file = f'{build_root(arch)}/lib/lib{name}.a'
        if not os.path.exists(library_file):
            raise Exception('Compile code failed!', 1001)

        # copy library
        tools.create_dir(output_library_path)
        target_library_file = f'{output_library_path}/{target}-{arch}.a'
        shutil.copy(library_file, target_library_file)

        # copy header
        header_file = f'{build_root(arch)}/include'
        if not os.path.exists(output_header_path):
            shutil.copytree(header_file, output_header_path)

        # clean
        tools.remove_dir(build_root(arch))

        return target_library_file

    # Build
    libraries = []
    for arch in archs:
        library = do_compile(arch)
        libraries.append(library)

    # Merge
    tools.merge_library(libraries, f'{output_library_path}/{target}.a')


def build(options=[]):
    try:
        download_source_code()
        clean_library()
        build_library()
    except Exception as e:
        clean_library()
        print(f'Error: {e.args[0]}')


def clean():
    tools.remove_dir(output_root)
    clean_source_code()


if __name__ == "__main__":
    tools.main(build, clean)