#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = "Marck Collado"
__date__ = "19/9/16"


import datetime
from subprocess import check_output, STDOUT
#import subprocess
import os
import errno
import shutil
import logging
import logging.handlers

def logs():
    """Guardem els logs """
    log=logging.getLogger("registre")
    logging.basicConfig(filename='/var/log/registre.log' , level=logging.INFO)
    log.setLevel(logging.WARNING)
    nom_log = logging.handlers.RotatingFileHandler(filename='/var/log/registre.log', mode='a', maxBytes=1024, backupCount=5)
    format_log = logging.Formatter(fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',datefmt='%y-%m-%d %H:%M:%S')
    nom_log.setFormatter(format_log)
    log.addHandler(nom_log)
    return log

def main():
    now = datetime.datetime.now()
    temp_path = "/tmp/registre"
    dest_path = "/usr/local/www/owncloud/data/admin/files/Registre/registre/" + str(now.year)
    opath = "admin/files/Registre/registre/"

    log = logs()

    log.debug("Checking temporary path existence")

    try:
        os.makedirs(temp_path)
        log.warning("%s not exists. It was created", temp_path)
        raise SystemExit()
    except OSError as exception:
        if exception.errno != errno.EEXIST or not os.path.isdir(temp_path):
            log.critical("Critical error: %s", exception)
            raise
    file_count = len(os.listdir(temp_path))
    if file_count > 0 :
        log.debug("Moving %d files to correct path", file_count)
        for item_path in os.listdir(temp_path):
            # shutil.chown not work on python 2.7 only 3.4
            #shutil.chown(item_path, user="www", group="www")
            shutil.move(os.path.join(temp_path, item_path) , os.path.join(dest_path, item_path))
            os.chown(os.path.join(dest_path, item_path), 80, 80)

        log.debug("Registering files in OwnCloud (this could be long)")
        #output = check_output(['/usr/local/bin/sudo', '-u', 'www', '/usr/local/bin/php', '/usr/local/www/ownclo ud/occ', 'files:scan', '-p', 'admin/files/Registre/registre/' + str(now.year) + "/"])
        output = check_output(['/usr/local/bin/sudo', '-u', 'www', '/usr/local/bin/php', '/usr/local/www/owncloud/occ', 'files:scan', '-p', opath])
        log.debug(output)
        log.info("OwnCloud update with %d new files", file_count)
    else:
        log.debug("No files to process")


if __name__ == "__main__":
    main()