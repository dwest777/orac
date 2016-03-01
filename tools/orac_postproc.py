#!/usr/bin/python3
# Run ORAC postprocessor from the community code
# 18 Feb 2016, AP: Initial version

import argparse
import os
import subprocess
import tempfile

import orac_utils

add_driver = """
{dir}/{root}{ph}{pri}
{dir}/{root}{ph}{sec}""".format
pri = '.primary.nc'
sec = '.secondary.nc'

def orac_postproc(args):
    if not os.path.isdir(args.out_dir):
        os.makedirs(args.out_dir, 0o774)

    # Form processing environment
    libs = orac_utils.read_orac_libraries(args.orac_lib)
    orac_utils.build_orac_library_path(libs)

    # form driver file
    driver = orac_utils.postproc_driver(
        bayesian = len(args.phases) > 2 or (args.phases[0] != 'WAT' and
                                        args.phases[1] != 'ICE'),
        compress = args.compress,
        ice_pri  = args.main_out_dir+'/'+args.fileroot+args.phases[1]+pri,
        ice_sec  = args.main_out_dir+'/'+args.fileroot+args.phases[1]+sec,
        out_pri  = args.out_dir+'/'+args.fileroot+pri,
        out_sec  = args.out_dir+'/'+args.fileroot+sec,
        verbose  = args.verbose,
        wat_pri  = args.main_out_dir+'/'+args.fileroot+args.phases[0]+pri,
        wat_sec  = args.main_out_dir+'/'+args.fileroot+args.phases[0]+sec
        )
    for phase in args.phases[2:]:
        driver += add_driver(
            dri  = args.main_out_dir,
            ph   = phase,
            pri  = pri,
            root = args.fileroot,
            sec  = sec
            )

    if (os.path.isfile(args.out_dir+'/'+args.fileroot+pri) and args.no_clobber):
        # Skip already processed files
        if args.verbose or args.progress:
            print(orac_utils.star * 60)
            print(orac_utils.star * 5 +' '+args.fileroot+' already postprocessed')
            print(orac_utils.star * 60)
    else:
        # Write driver file
        (fd, driver_file) = tempfile.mkstemp('.driver', 'POSTPROC.',
                                             args.main_out_dir, True)
        try:
            f = os.fdopen(fd, "w")
            f.write(driver)
            f.close()
        except IOError:
            print('Cannot create driver file '+driver_file)

        # Call main processor
        if args.verbose or args.progress:
            print(orac_utils.star * 60)
            print(orac_utils.star * 5 +' post_process_level2 <<')
            print(orac_utils.star * 5 +' '+
                  driver.replace("\n", "\n"+orac_utils.star*5+" "))
            print(orac_utils.star * 60)
        try:
            os.chdir(args.orac_dir + '/post_processing')
            subprocess.check_call('post_process_level2 '+driver_file,shell=True)
        finally:
            os.remove(driver_file)

    return

#-----------------------------------------------------------------------------

# Set-up to call this as a script
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run the ORAC postprocessor.')
    parser.add_argument('fileroot', type=str, default = None,
                        help = 'Root name of preprocessed files.')
    parser = orac_utils.orac_common_args(parser)
    parser = orac_utils.orac_postproc_args(parser)
    args   = parser.parse_args()
    orac_utils.orac_common_args_check(args)
    orac_utils.orac_postproc_args_check(args)
    orac_postproc(args)
