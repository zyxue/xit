#1/usr/bin/env python

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath('.')))

import time
import re
from multiprocessing import Process

import cProfile

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import xit

def profile():
    profile_file = '/tmp/time.log'
    cProfile.run("xit.main(['prep', '-p', 'mkdir'])", profile_file)
    import pstats
    p = pstats.Stats(profile_file)
    p.sort_stats('cumulative').print_stats(20)

if __name__ == "__main__":
    class ProfileHandler(FileSystemEventHandler):
        def on_modified(self, event):
            super(ProfileHandler, self).on_modified(event)

            TO_BE_IGNORED = ['flymake.py$', '\.#', '.*\.pyc']
            IGNORE_RE = [re.compile(_) for _ in TO_BE_IGNORED]
                         
            action = True
            for _ in IGNORE_RE:
                if _.search(event.src_path):
                    action = False
                    break

            if action:
                os.system('clear')
                p = Process(target=profile)
                p.start()
                p.join()
                what = 'directory' if event.is_directory else 'file'
                print "{0} {1}: {2}".format(event.event_type, what, event.src_path)

    event_handler = ProfileHandler()
    observer = Observer()
    observer.schedule(event_handler, path=sys.argv[1], recursive=True)
    observer.start()
    print 'start watching and profiling:'
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()
