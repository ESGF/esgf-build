''' Utility functions for esgf_build.py '''
import os
import hashlib
import errno
import shutil
import subprocess
import shlex

def get_md5sum(file_name):
    '''
        #Utility function, wraps md5sum so it may be used on either mac or
        #linux machines
    '''
    hasher = hashlib.md5()
    with open(file_name, 'rb') as file_handle:
        buf = file_handle.read()
        hasher.update(buf)
        file_name_md5 = hasher.hexdigest()
    return file_name_md5



def mkdir_p(path, mode=0777):
    '''Makes directory, passes if directory already exists'''
    try:
        os.makedirs(path, mode)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            print "{path} already exists".format(path=path)
            print "Removing and rebuilding path."
            shutil.rmtree(path)
            mkdir_p(path, mode=0777)
        else:
            raise


def stream_subprocess_output(command_string, file_handle):
    ''' Print out the stdout of the subprocess in real time '''
    process = subprocess.Popen(shlex.split(command_string), stdout=subprocess.PIPE)
    with process.stdout:
        for line in iter(process.stdout.readline, b''):
            print line,
            file_handle.write(line)
    # wait for the subprocess to exit
    process.wait()


def replace_string_in_file(file_name, original_string, new_string):
    '''Goes into a file and replaces string'''
    with open(file_name, 'r') as file_handle:
        filedata = file_handle.read()
    filedata = filedata.replace(original_string, new_string)

    # Write the file out again
    with open(file_name, 'w') as file_handle:
        file_handle.write(filedata)
