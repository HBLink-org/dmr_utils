#!/usr/bin/env python
#
###############################################################################
#   Copyright (C) 2016  Cortney T. Buffington, N0MJS <n0mjs@me.com>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software Foundation,
#   Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301  USA
###############################################################################

from __future__ import print_function

import json
from os.path import isfile, getmtime
from os import remove
from time import time
from urllib import URLopener
from csv import reader as csv_reader
from binascii import b2a_hex as ahex

# Does anybody read this stuff? There's a PEP somewhere that says I should do this.
__author__     = 'Cortney T. Buffington, N0MJS'
__copyright__  = 'Copyright (c) 2016-2017 Cortney T. Buffington, N0MJS and the K0USY Group'
__credits__    = 'Colin Durbridge, G4EML, Steve Zingman, N4IRS; Mike Zingman'
__license__    = 'GNU GPLv3'
__maintainer__ = 'Cort Buffington, N0MJS'
__email__      = 'n0mjs@me.com'


#************************************************
#     STRING UTILITY FUNCTIONS
#************************************************

# Create a 2 byte hex string from an integer
def hex_str_2(_int_id):
    try:
        return format(_int_id,'x').rjust(4,'0').decode('hex')
    except TypeError:
        raise

# Create a 3 byte hex string from an integer
def hex_str_3(_int_id):
    try:
        return format(_int_id,'x').rjust(6,'0').decode('hex')
    except TypeError:
        raise

# Create a 4 byte hex string from an integer
def hex_str_4(_int_id):
    try:
        return format(_int_id,'x').rjust(8,'0').decode('hex')
    except TypeError:
        raise

# Convert a hex string to an int (radio ID, etc.)
def int_id(_hex_string):
    return int(ahex(_hex_string), 16)


#************************************************
#     RANDOM UTILITY FUNCTIONS
#************************************************

# Ensure all keys and values in a dictionary are ascii 
def mk_ascii_dict(input):
    if isinstance(input, dict):
        return {mk_ascii_dict(key): mk_ascii_dict(value) for key, value in input.iteritems()}
    elif isinstance(input, list):
        return [mk_ascii_dict(element) for element in input]
    elif isinstance(input, unicode):
        return input.encode('ascii','ignore')
    else:
        return input


#************************************************
#     ID ALIAS FUNCTIONS
#************************************************

# Download and build dictionaries for mapping number to aliases
# Used by applications. These lookups take time, please do not shove them
# into this file everywhere and send a pull request!!!
# Download a new file if it doesn't exist, or is older than the stale time
def try_download(_path, _file, _url, _stale,):
    now = time()
    url = URLopener()
    file_exists = isfile(_path+_file) == True
    if file_exists:
        file_old = (getmtime(_path+_file) + _stale) < now
    if not file_exists or (file_exists and file_old):
        try:
            url.retrieve(_url, _path+_file)
            result = 'ID ALIAS MAPPER: \'{}\' successfully downloaded'.format(_file)
        except IOError:
            result = 'ID ALIAS MAPPER: \'{}\' could not be downloaded'.format(_file)
    else:
        result = 'ID ALIAS MAPPER: \'{}\' is current, not downloaded'.format(_file)
    url.close()
    return result

# LEGACY VERSION - MAKES A SIMPLE {INTEGER ID: 'CALLSIGN'} DICTIONARY
def mk_id_dict(_path, _file):
    dict = {}
    
    if _file.endswith(('.json','.JSON')):         
        try:
            with open(_path+_file, 'rU') as _handle:

                try:
                    ids = json.loads(_handle.read().decode('utf-8', 'ignore'))
                except (ValueError):
                    remove(_path+_file)
                    return dict

                if 'repeaters' in ids:
                    ids = ids['repeaters']
                    id_type = 'locator'
                    id_value = 'callsign'
                elif 'users' in ids:
                    ids = ids['users']
                    id_type = 'radio_id'
                    id_value = 'callsign'
                elif 'tgids' in ids:
                    ids = ids['tgids']
                    id_type = 'tgid'
                    id_value = 'name'
                else:
                    return dict

                try:
                    for row in range(len(ids)):
                        dict[int(ids[row][id_type])] = ids[row][id_value].encode('ascii','ignore')
                except (ValueError, KeyError):
                    remove(_path+_file)
                    return dict;

                _handle.close
                return dict
        except IOError:
            return dict
        
    elif _file.endswith(('.csv','.CSV')):
        try:
            with open(_path+_file, 'rU') as _handle:
                ids = csv_reader(_handle, dialect='excel', delimiter=',')
                for row in ids:
                    dict[int(row[0])] = (row[1])
                _handle.close
                return dict
        except IOError:
            return dict

# NEW VERSION - MAKES A FULL DICTIONARY OF INFORMATION BASED ON TYPE OF ALIAS FILE
# BASED ON DOWNLOADS FROM DMR-MARC AND ONLY WORKS FOR DMR-MARC STYLE JSON FILES!!!  
# RESULTING DICTIONARY KEYS ARE INTEGER RADIO ID, AND VALURES ARE DICTIONARIES OF
# WHATEVER IS IN EACH ROW OF THE DMR-MARC DATABASE USED, IE.:
#   312345: {u'map': u'0', u'color_code': u'1', u'city': u'Morlon'.....u'map_info': u'', u'trustee': u'HB9HFF'}
def mk_full_id_dict(_path, _file):
    dict = {}
    try:
        with open(_path+_file, 'rU') as _handle:
            ids = json.loads(_handle.read().decode('utf-8', 'ignore'))
            if 'repeaters' in ids:
                ids = ids['repeaters']
                id_type = 'locator'
            elif 'users' in ids:
                ids = ids['users']
                id_type = 'radio_id'
            else:
                return dict

            for row in range(len(ids)):
                dict[int(ids[row][id_type])] = ids[row]
        
            _handle.close
            #dict = mk_ascii_dict(dict)
            return dict
    except IOError:
        return dict

# USE THIS TO QUERY THE ID DICTIONARIES WE MAKE WITH THE FUNCTION(S) ABOVE
def get_alias(_id, _dict, *args):
    if type(_id) == str:
        _id = int_id(_id)
    if _id in _dict:
        if args:
            retValue = []
            for _item in args:
                try:
                    retValue.append(_dict[_id][_item])
                except TypeError:
                    return _dict[_id]
            return retValue
        else:
            return _dict[_id]
    return _id

# FOR LEGACY PURPOSES
get_info = get_alias
