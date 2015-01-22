#/usr/bin/env python



import os, sys, subprocess, time, traceback, yaml, types, datetime

import wasanbon
from wasanbon.core import package

report_file_name = 'report_build.yaml'
test_package_name = 'build_test_package'

exclusive_rtc_repo = ['LEDTest']
def main():
    
    build_status_dir = {}
    if os.path.isfile(report_file_name):
        os.rename(report_file_name, report_file_name + wasanbon.timestampstr())
    report_file = open(report_file_name, "w")

    # Refresh test build package
    output = subprocess.check_output(['wasanbon-admin.py', 'package', 'list'])
    pack_names = yaml.load(output)

    if test_package_name in pack_names:
        #subprocess.call(['wasanbon-admin.py', 'package', 'unregister', test_package_name, '-c'])
        pass
    else:
        subprocess.call(['wasanbon-admin.py', 'package', 'create', test_package_name, '-v'])
    
    dirname = subprocess.check_output(['wasanbon-admin.py', 'package', 'directory', test_package_name])
    if type(dirname) == types.StringType:
        dirname = dirname.strip()
    org_dir = os.getcwd()
    os.chdir(dirname.strip())

    output = subprocess.check_output(['./mgr.py', 'rtc', 'list'])
    rtc_names = yaml.load(output)
    if type(rtc_names) == types.ListType:
        for rtc_name in rtc_names:
            ret = subprocess.call(['./mgr.py', 'repository', 'pull', rtc_name])
    else:
        rtc_names = []

        output = subprocess.check_output(['./mgr.py', 'repository', 'list'])
        rtc_repo_names = yaml.load(output)
        for rtc_repo_name in rtc_repo_names:
            if rtc_repo_name in exclusive_rtc_repo:
                continue
            subprocess.call(['./mgr.py', 'rtc', 'clone', rtc_repo_name])
            pass
        pass

    output = subprocess.check_output(['./mgr.py', 'rtc', 'list'])
    rtc_names = yaml.load(output)
    for rtc_name in rtc_names:
        ret = subprocess.call(['./mgr.py', 'rtc', 'build', rtc_name, '-q'])
        build_status_dir[rtc_name] = {'status' : ret, 'date' : str(datetime.datetime.now())}

    report_file.write(yaml.dump(build_status_dir))
    report_file.close()

    os.chdir(org_dir)
    # subprocess.call(['wasanbon-admin.py', 'package', 'unregister', test_package_name, '-c'])

    return 


if __name__ == '__main__':
    main()
