#/usr/bin/env python



import os, sys, subprocess, time, traceback

import wasanbon

report_file_name = 'build_report.yaml'

def main():
    
    if os.path.isfile(report_file_name):
        os.rename(report_file_name, report_file_name + wasanbon.timestampstr())
    report_file = open(report_file_name, "w")
    return 


if __name__ == '__main__':
    main()
