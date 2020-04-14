##
#
# Copyright 2020 - Intersect Technologies CC
# Author: Niel Swart <niel@nielswart.com>
#
##

from util import Logger

__version__ = "0.1.0"

log = Logger.getLogger()

from device_mode import CONFIG_MODE

if CONFIG_MODE:
    import app_config as app

    log.info("Running app in config mode")

else:
    import app_run as app

    log.info("Running app in run mode")

app.main()
