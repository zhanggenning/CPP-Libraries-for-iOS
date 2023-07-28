# 开源C++库 iOS 版

## 1. 简介

主要保存开源C++的库，交叉编译后可以在iOS平台的静态库。

开源版本：

* exiv2:  0.27.7
* lcms2:  2.15
* openmp: 14.0.6
* libraw: 0.21.1

## 2. 脚本

编译脚本文件夹，保存所有iOS平台的交叉编译脚本

> build_exiv2_ios： exiv2 编译脚本
>
> build_lcms2_ios：lcms2 编译脚本
>
> build_libraw_ios：libraw 编译脚本
>
> build_openmp_ios：openmp 编译脚本
>
> build_tools: 基础工具
>
> build_all: 全部编译

**注**1：如果需要单独编译某个库，需要对应的编译脚本+build_tools.py，即可运行

**注2**：部分源码下载需要挂代理

### 2.1 编译全部

```python
python3 build_all.py
```

### 2.2 单独编译

以exiv2库为例，需要对应的编译文件和build_tools文件：

> build_exiv2_ios.py
>
> build_tools.py

```
python3 build_exiv2_ios.py
```

### 2.3 特殊编译

libraw编译可以带参数，开启对其他库的支持，因此运行先应该先保证其他库存在，然后在编译libraw时携带对应参数，保证libraw开启支持。以 开启 openmp 支持为例：

需要对应文件：

> build_libraw_ios.py
>
> build_toos.py
>
> output/openmp/lib/libomp.a
>
> output/openmp/include/*.h

```python
python3 build_libraw_ios.py --enable-openmp
```

### 2.4 编译输出

编译结束后，会出现以下两个文件夹：

> output: 静态库和头文件的输出路径
>
> source: 开源库的源代码

## 3. 静态库

exiv2:

> include/*.h
>
> lib/libexiv2.a（x86_64, arm64）

lcms2:

> include/*.h
>
> lib/liblcms2（x86_64, arm64）

openmp:

> include/*.h
>
> lib/libomp.a（x86_64, arm64）

libraw:

> include/*.h
>
> lib/libraw（x86_64, arm64）



## 4. Demo使用

