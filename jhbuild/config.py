# jhbuild - a build script for GNOME 1.x and 2.x
# Copyright (C) 2001-2004  James Henstridge
#
#   config.py: configuration file parser
#
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

import os
import traceback

from jhbuild.errors import UsageError, FatalError

__all__ = [ 'Config' ]

_defaults_file = os.path.join(os.path.dirname(__file__), 'defaults.jhbuildrc')
_default_jhbuildrc = os.path.join(os.environ['HOME'], '.jhbuildrc')

_known_keys = [ 'moduleset', 'modules', 'skip', 'prefix',
                'checkoutroot', 'autogenargs', 'makeargs', 'cvsroots',
                'branches', 'module_autogenargs', 'interact',
                'buildscript', 'nonetwork', 'alwaysautogen',
                'nobuild', 'makeclean', 'makecheck', 'use_lib64',
                'tinderbox_outputdir', 'sticky_date' ]

def addpath(envvar, path):
    '''Adds a path to an environment variable.'''
    # special case ACLOCAL_FLAGS
    if envvar in [ 'ACLOCAL_FLAGS' ]:
        envval = os.environ.get(envvar, '-I %s' % path)
        if envval.find(path) < 0:
            envval = envval + ' -I ' + path
    else:
        envval = os.environ.get(envvar, path)
        if not envval.startswith(path):
            envval = path + ':' + envval

    os.environ[envvar] = envval

class Config:
    def __init__(self, filename=_default_jhbuildrc):
        config = {
            '__file__': _defaults_file,
            'addpath':  addpath
            }
        try:
            execfile(_defaults_file, config)
        except:
            traceback.print_exc()
            raise FatalError('could not load config defaults')
        config['__file__'] = filename
        try:
            execfile(filename, config)
        except:
            traceback.print_exc()
            raise FatalError('could not load config file')

        # backward compatibility, from the days when jhbuild only
        # supported Gnome.org CVS.
        if config.has_key('cvsroot'):
            config['cvsroots']['gnome.org'] = config['cvsroot']

        # environment variables
        if config.has_key('cflags') and config['cflags']:
            os.environ['CFLAGS'] = config['cflags']
        if config.has_key('installprog') and config['installprog']:
            os.environ['INSTALL'] = config['installprog']

        # copy known config keys to attributes on the instance
        for name in _known_keys:
            setattr(self, name, config[name])

        self.setup_env()

    def setup_env(self):
        '''set environment variables for using prefix'''

        if not os.path.exists(self.prefix):
            try:
                os.makedirs(self.prefix)
            except:
                raise FatalError("Can't create %s directory" % prefix)

        #includedir = os.path.join(prefix, 'include')
        #addpath('C_INCLUDE_PATH', includedir)
        if self.use_lib64:
            libdir = os.path.join(self.prefix, 'lib64')
        else:
            libdir = os.path.join(self.prefix, 'lib')
        addpath('LD_LIBRARY_PATH', libdir)
        bindir = os.path.join(self.prefix, 'bin')
        addpath('PATH', bindir)
        pkgconfigdir = os.path.join(libdir, 'pkgconfig')
        if not os.environ.has_key('PKG_CONFIG_PATH'):
            pkgconfigdir = pkgconfigdir + ':/usr/lib/pkgconfig'
        addpath('PKG_CONFIG_PATH', pkgconfigdir)
        xdgdatadir = os.path.join(self.prefix, 'share')
        addpath('XDG_DATA_DIRS', xdgdatadir)
        aclocaldir = os.path.join(self.prefix, 'share', 'aclocal')
        if not os.path.exists(aclocaldir):
            try:
                os.makedirs(aclocaldir)
            except:
                raise FatalError("Can't create %s directory" % aclocaldir)

        addpath('ACLOCAL_FLAGS', aclocaldir)

        os.environ['CERTIFIED_GNOMIE'] = 'yes'

        # get rid of gdkxft from the env -- it will cause problems.
        if os.environ.has_key('LD_PRELOAD'):
            valarr = os.environ['LD_PRELOAD'].split(' ')
            for x in valarr[:]:
                if x.find('libgdkxft.so') >= 0:
                    valarr.remove(x)
            os.environ['LD_PRELOAD'] = ' '.join(valarr)
