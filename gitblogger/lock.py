import os
import errno

class LockError (Exception):
    pass

class LockIsLocked (LockError):
    pass

class LockIsUnlocked (LockError):
    pass

class Lock (object):

    def __init__ (self, path):
        self.path = path
        self.locked = False

    def acquire (self):
        if self.locked:
            raise LocksLocked()

        try:
            os.mkdir(self.path)
            self.locked = True
        except OSError, detail:
            if detail.errno == errno.EEXIST:
                raise LockIsLocked()
            else:
                raise

    def release (self):
        if not self.locked:
            raise LockIsUnlocked()

        try:
            os.rmdir(self.path)
            self.locked = False
        except OSError, detail:
            if detail.errno == errno.ENOENT:
                raise LockIsUnlocked()
            else:
                raise

    def __del__ (self):
        if self.locked:
            self.release()

