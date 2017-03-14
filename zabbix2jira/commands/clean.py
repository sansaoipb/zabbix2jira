# -*- coding: utf-8 -*-
"""The clean command."""


from .base import Base
import os


class Clean(Base):
    """Clear the cache directory and other temporary files"""

    def run(self, action=None):
        folder = self._get_config_str('Main', 'CACHE_DIRECTORY')
        self.log.info("Cleaning cache directory %s" % folder)
        for the_file in os.listdir(folder):
            file_path = os.path.join(folder, the_file)
            try:
                if os.path.isfile(file_path):
                    self.log.debug("Removing %s" % file_path)
                    os.unlink(file_path)
            except Exception, e:
                self.log.error(e)
