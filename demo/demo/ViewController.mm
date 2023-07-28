//
//  ViewController.m
//  demo
//
//  Created by Genning.Zhang on 2023/7/28.
//

#import "ViewController.h"
#import "libraw.h"
#import "lcms2.h"
#import "omp.h"
#import "exiv2/exiv2.hpp"

@interface ViewController ()

@end

@implementation ViewController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    //libraw
    const char *librawVersion = libraw_version();
    NSLog(@"[libraw version] %s", librawVersion);
    
    //lcms2
    int lcms2Version = cmsGetEncodedCMMversion();
    NSLog(@"[lcms2 version] %d", lcms2Version);
    
    //openmp
    int ompThreadsNumber = omp_get_max_threads();
    NSLog(@"[omp threads num] %d", ompThreadsNumber);
    
    //exiv2
    std::string exiv2Version = Exiv2::versionString();
    NSLog(@"[exiv2 version] %s", exiv2Version.c_str());
}


@end
