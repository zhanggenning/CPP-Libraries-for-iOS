# 开源C++库 (iOS 版)

## 1. 简介

交叉编译开源C++库的源码，生成可以在iOS平台的静态库，所有库最低支持iOS 13.0。

相关C++库版本：

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



## 4. Demo集成

demo使用静态库需要在Xcode中做如下通用配置，然后再根据各库的特点再分别配置：

```objc
// 1. 设置静态库查找路径和头文件查找路径
Build Setting -> Lirary Search Path -> [静态库路径]
Build Setting -> Header Search Path -> [头文件路径]

// 2. M系列芯片Mac需要配置模拟器使用arm64架构
Build Setting -> Excluded Architectures -> Debug -> Any iOS Simulator SDK [arm64]

// 3. 添加依赖系统库 (libz.tbd, libc++.tbd)
Build Phases -> Link Binary With Libraries -> [libz.tbd]
Build Phases -> Link Binary With Libraries -> [libc++.tbd]

// 4. c++模块化编译(非必需，加上之后提升编译速度)
Build Setting -> Apple Clang - Address Sanitizer -> Other C++ Flags [-fcxx-modules]

// 5. 添加静态库
Build Phases -> Link Binary With Libraries -> [xxx.a]
```

### 4.1 lcms2集成

```objc
// 添加自定义宏 CMS_NO_REGISTER_KEYWORD（禁用头文件中 register）
Build Setting -> Apple Clang - Preprocessing -> Preprocessor Macros [CMS_NO_REGISTER_KEYWORD]
```

### 4.2 openmp 集成

```objc
// Other Linker Flags 添加 -XClang -openmp
Build Setting -> Linking -> Other Linker Flags [-XClang -openmp]
```

### 4.3 exiv2 集成

```objective-c
// 1.（0.27.7 ）版本使用的是 c++14标准，因此Xcode中的C++标准设置为C++14
Build Settings -> Apple Clang - Language - C++ -> C++ Language Dialect [C++14 或者 GNU++14]

// 2. 依赖系统 libiconv.tbd
Build Phases -> Link Binary With Libraries -> [libiconv.tbd]
  
// 3. 头文件引入方式
#import "exiv2/exiv2.hpp"
```

### 4.4 libraw 集成

* libraw 如果在编译时开了 --enable-openmp，那么demo里一定要先链接openmp，再链接libraw
* libraw 如果在编译时开了 --enable-lcms2，那么demo里一定要先链接lcms2，再链接libraw

