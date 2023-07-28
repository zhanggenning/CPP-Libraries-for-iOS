import build_openmp_ios as openmp
import build_libraw_ios as libraw
import build_lcms2_ios as lcms
import build_exiv2_ios as exiv2
import build_tools as tools
import sys

root = sys.path[0]
tools.remove_dir(f'{root}/__pycache__')
tools.remove_dir(f'{root}/output')
tools.remove_dir(f'{root}/source')

exiv2.build()
lcms.build()
openmp.build()
libraw.build(['--enable-openmp'])