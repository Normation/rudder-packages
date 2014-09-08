#!/usr/bin/env python
#####################################################################################
# Copyright 2013 Normation SAS
#####################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, Version 3.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#####################################################################################
#
# usage: vzps.py [-E <ctid>] [ps arguments]
#
# Returns the process running on VZ system with ID ctid
# Limitation: Works only with PID on second column
#####################################################################################
import os
import sys
import types
import subprocess

def get_command_output(cmd):
    # Get its output and pid 
    process = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=None, shell=False)
    output = process.communicate()
    return output[0].split('\n')

def main():
    # Defaults ps command and arguments
    ps_cmd = 'ps'
    ps_args = ''

    # We default on host ctid
    CTID = 0
    CTID_provided = False

    # Parsing script arguments
    if len(sys.argv) == 2:
        ps_args = sys.argv[1:]

    elif len(sys.argv) >= 3:
        if sys.argv[1] == '-E':
            if not sys.argv[2] or not sys.argv[2].isdigit():
                print('Invalid CTID')
                sys.exit(1)
            CTID = sys.argv[2]
            CTID_provided = True
            if len(sys.argv) >= 4:
                ps_args = sys.argv[3:]
        else:
            ps_args = sys.argv[1:]

    # Join ps_args if it's a list
    if isinstance(ps_args, list):
        ps_args = ' '.join(ps_args)

    # Build ps command
    ps_cmd = '%s %s' % (ps_cmd, ps_args)

    # Build envID string
    envID = 'envID:\t%s' % (str(CTID))

    # Get command output
    plist = get_command_output(ps_cmd)

    # Declare final list
    flist = []
    fadd  = flist.append

    # Loop on output list
    for pline in plist:
        # No CTID provided so just act as ps
        if not CTID_provided:
            fadd(pline)
        else:
            # Make a list out of each line
            proc_list = pline.split()
            if proc_list and 'PID' in proc_list[1]:
                # Add the line to flist if title line
                fadd(pline)
            elif proc_list and os.path.isfile(os.path.join('/proc', proc_list[1], 'status')):
                pid_read = open(os.path.join('/proc', proc_list[1], 'status'), 'rb').read()
                if envID in pid_read:
                    # Add the line to flist if it's an openvz host process
                    fadd(pline)

    # Finally output flist which contains only openvz CTID processes
    for process_line in flist:
        print(process_line)

if __name__ == '__main__':
    main()
