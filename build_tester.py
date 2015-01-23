#/usr/bin/env python
import os, sys, subprocess, time, traceback, yaml, types, datetime

import wasanbon
from wasanbon.core import package

report_file_name = 'report_build.yaml'
test_package_name = 'build_test_package'

exclusive_rtc_repo = ['LEDTest']

def check_output(cmd):
    print 'CMD:', cmd
    #if cmd[0].endswith('.py'):
    #    cmd = ['python'] + cmd
    if sys.platform == 'win32' and cmd[0].startswith('./'):
        cmd[0] = cmd[0][2:]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    p.wait()
    output = p.stdout.read()
    return output

def call(cmd):
    print 'CMD:', cmd
    if sys.platform == 'win32' and cmd[0].startswith('./'):
        cmd[0] = cmd[0][2:]
    #if cmd[0].endswith('.py'):
    #    cmd = ['python'] + cmd
    p = subprocess.call(cmd, shell=True)
    return p

def main():
    
    build_status_dir = {}
    if os.path.isfile(report_file_name):
        os.rename(report_file_name, report_file_name + wasanbon.timestampstr())
    report_file = open(report_file_name, "w")

    # Refresh test build package
    output = check_output(['wasanbon-admin.py', 'package', 'list'])
    pack_names = yaml.load(output)

    if test_package_name in pack_names:
        #subprocess.call(['wasanbon-admin.py', 'package', 'unregister', test_package_name, '-c'])
        pass
    else:
        call(['wasanbon-admin.py', 'package', 'create', test_package_name, '-v'])
    
    dirname = check_output(['wasanbon-admin.py', 'package', 'directory', test_package_name])
    if type(dirname) == types.StringType:
        dirname = dirname.strip()
    org_dir = os.getcwd()
    os.chdir(dirname.strip())

    output = check_output(['./mgr.py', 'rtc', 'list'])
    rtc_names = yaml.load(output)
    if type(rtc_names) == types.ListType:
        for rtc_name in rtc_names:
            ret = call(['./mgr.py', 'repository', 'pull', rtc_name])
    else:
        rtc_names = []

        output = check_output(['./mgr.py', 'repository', 'list'])
        rtc_repo_names = yaml.load(output)
        for rtc_repo_name in rtc_repo_names:
            if rtc_repo_name in exclusive_rtc_repo:
                continue
            call(['./mgr.py', 'rtc', 'clone', rtc_repo_name])
            pass
        pass

    output = check_output(['./mgr.py', 'rtc', 'list'])
    rtc_names = yaml.load(output)
    for rtc_name in rtc_names:
        ret = call(['./mgr.py', 'rtc', 'build', rtc_name, '-q'])
        build_status_dir[rtc_name] = {'status' : ret, 'date' : str(datetime.datetime.now())}

    report_file.write(yaml.dump(build_status_dir))
    report_file.close()

    os.chdir(org_dir)
    # subprocess.call(['wasanbon-admin.py', 'package', 'unregister', test_package_name, '-c'])

    return 


if __name__ == '__main__':
    main()
