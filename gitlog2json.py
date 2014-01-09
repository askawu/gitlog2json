#!/usr/bin/env python

# commit
# auther
# date
# subtitle
# message

import re
import sys
import json
import argparse
import subprocess


def jsonize(log_range):

    # commit, author, date, subtitle, message
    NUM_STATE = 6
    STATE_COMMIT = 0 
    STATE_AUTHOR = 1 
    STATE_DATE = 2 
    STATE_NEWLINE = 3
    STATE_SUBJECT = 4 
    STATE_MSG = 5

    state = STATE_COMMIT
    msg = ""

    if log_range:
        proc = subprocess.Popen(["git", "log", "--no-merges", log_range], stdout=subprocess.PIPE)
    else:
        proc = subprocess.Popen(["git", "log", "--no-merges"], stdout=subprocess.PIPE)

    rv = proc.wait()
    if rv != 0: 
        return

    o = open("gitlog.json", "w")
    o.write("[\n")

    while True:
        line = proc.stdout.readline()
        if line == '':
            break

        if state == STATE_COMMIT:
            match = re.search("commit (\w{40})\n", line)
            if match:
                o.write("  {\n")
                o.write('    "commit":  %s,\n' % json.dumps(match.group(1)))
            else:
                print "parse error: ", state
                break
        elif state == STATE_AUTHOR:
            match = re.search("Author: ([\w\.\s]+) <([\w\.]+@[\w\.-]+)>\n", line)
            if match:
                txt = "%s <%s>" % (match.group(1), match.group(2))
                o.write('    "author":  %s,\n' % json.dumps(match.group(1)))
                o.write('    "email":   %s,\n' % json.dumps(match.group(2)))
            else:
                print "parse error", state
                break
        elif state == STATE_DATE:
            match = re.search("Date:\s{3}([\w\s:\+-]+)\n", line)
            if match:
                o.write('    "date":    %s,\n' % json.dumps(match.group(1)))
            else:
                print "parse error: ", state
                break
        elif state == STATE_NEWLINE:
            match = re.search("\n", line) 
            if not match:
                print "parse error: ", state
                break
        elif state == STATE_SUBJECT:
            o.write('    "subject": %s,\n' % json.dumps(line.rstrip("\n")))
        elif state == STATE_MSG:
            match = re.search("commit (\w{40})\n", line)
            if match:
                # finish up
                o.write('    "message": %s\n' % json.dumps(msg))
                o.write('  },\n\n')
                # escape from msg
                o.write("  {\n")
                o.write('    "commit":  %s,\n' % json.dumps(match.group(1)))
                msg = ""
                state = STATE_COMMIT
            else:
                msg = msg + line
                continue
        state = (state + 1) % NUM_STATE

    o.write('    "message": %s\n' % json.dumps(msg))
    o.write('  }\n')
    o.write("]\n")
    o.close()

def parse_args():
    parser = argparse.ArgumentParser(description='Convert the git log to a json file')
    parser.add_argument('log_range', nargs='?', help='<since>..<until>')
    return parser.parse_args()

def main():
    args = parse_args()
    jsonize(args.log_range)

if __name__ == '__main__':
    main()
