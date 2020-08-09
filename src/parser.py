import inspect
from sys import path


class Parser:

    def __init__(self, filename):
        self.filename = filename

    def file_exists(self):
        if path.exists(self.filename):
            return True
        print('File: {} does not exist'.format(self.filename))
        return False

    def key_error_output(self, note=''):
        caller = inspect.stack()[1].function
        return 'Key Error at function: ' + caller + ' pdbid: ' + self.filename + ' NOTE: ' + note
