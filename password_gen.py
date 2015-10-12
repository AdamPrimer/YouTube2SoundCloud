#!/usr/bin/env python
import getpass
from bcrypt import hashpw, gensalt

password = getpass.getpass("Desired Password: ")
hashed = hashpw(password, gensalt())
print "Your Hash is: {}".format(hashed)
