""" Test file for processing DD xml upfile and sending it to the parsing routines. """

import time
import subprocess
import os.path


def main():
    file_date_time = time.strftime('%m-%d-%Y-%H:%M')
    new_filename_xml = "fz-{}.xml".format(file_date_time)
    zip_filename = 'fz.gz'


    #file_path = "/home/gene/projects/perl/dd_xml/"
    file_path = ""

    zip_file = '{}{}'.format(file_path, zip_filename)

    # Unzip file if file exists
    if os.path.exists(zip_file):
        exec_retval = subprocess.call('/bin/gunzip -q {}'.format(zip_file), shell=True)
        print(exec_retval)

        # if unzip failed, return val will be 1 and just exit
        if exec_retval:
            return
    else:
        print('{} does not exist. Cannot unzip. Quitting.'.format(zip_file))
        return

    # Rename unzipped file
    print('/bin/mv {0}fz {0}{1}'.format(file_path, new_filename_xml))
    subprocess.call('/bin/mv {0}fz {0}{1}'.format(file_path, new_filename_xml), shell=True)

    # Run the parse programs on the file
    #parse_prog_path = '/home/gene/projects/python/'
    parse_prog_path = ''
    subprocess.call('/usr/bin/python3 {0}tx_parse.py {1}{2}'.format(parse_prog_path,
                                                                         file_path,
                                                                         new_filename_xml), shell=True)
    subprocess.call('/usr/bin/python3 {0}tc_parse.py {1}{2}'.format(parse_prog_path,
                                                                         file_path,
                                                                         new_filename_xml), shell=True)


if __name__ == '__main__':
    main()
