# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from __future__ import print_function

import os
import sys
import importlib
import pkgutil
import locale

from .compat import text_type

def inpath(filename, path):
    for dir in path:
        if os.path.isfile(os.path.join(dir, filename)):
            return True
        # also check for filename.exe on Windows
        if sys.platform.startswith('win') and os.path.isfile(os.path.join(dir, filename + '.exe')):
            return True
    return False


def try_import_module(module_name):
    """Like importlib.import_module() but doesn't raise if the module doesn't exist"""

    if pkgutil.get_loader(module_name) is None:
        return
    return importlib.import_module(module_name)


def _get_encoding():
    try:
        encoding = locale.getpreferredencoding()
    except locale.Error:
        encoding = ""
    if not encoding:
        # work around locale.getpreferredencoding() returning an empty string in
        # Mac OS X, see http://bugzilla.gnome.org/show_bug.cgi?id=534650
        if sys.platform == "darwin":
            encoding = "utf-8"
        else:
            encoding = "ascii"
    return encoding

_encoding = _get_encoding()


def uencode(s):
    if isinstance(s, text_type):
        return s.encode(_encoding, 'replace')
    else:
        return s

def udecode(s):
    if not isinstance(s, text_type):
        return s.decode(_encoding, 'replace')
    else:
        return s

def uprint(*args, **kwargs):
    '''Print Unicode string encoded for the terminal'''

    print(*[uencode(s) for s in args], **kwargs)

def N_(x):
    return text_type(x)

_ugettext = None

def _(x):
    x = text_type(x)
    if _ugettext is not None:
        return _ugettext(x)
    return x


def install_translation(translation):
    global _ugettext

    _ugettext = translation.ugettext