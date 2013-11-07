#!/usr/bin/env python
#
# -*- mode: python; sh-basic-offset: 4; indent-tabs-mode: nil; coding: utf-8 -*-
# vim: tabstop=4 softtabstop=4 expandtab shiftwidth=4 fileencoding=utf-8

import argparse
import httplib2
import logging
import sys
import urllib
from xml.dom import minidom

from __init__ import NAME, VERSION


BASE_URL = 'https://www.notifymyandroid.com/publicapi'
USER_AGENT = 'nma-python/v%s' % VERSION
NOTIFY_LEVELS = {
    '-2,low,FLAPPINGDISABLED,DOWNTIMECANCELLED': -2,
    '-1,moderate,ACKNOWLEDGEMENT': -1,
    '0,normal,RECOVERY,FLAPPINGSTOP,DOWNTIMESTOP': 0,
    '1,high,FLAPPINGSTART,DOWNTIMESTART': 1,
    '2,emergency,PROBLEM': 2,
}


class NMAPython(object):
    """
    Main class implementing the public api methods
    """

    _api_keys     = set()
    _dev_key      = None
    _log          = None
    _log_levels   = {
        'INFO': logging.INFO,
        'DEBUG': logging.DEBUG,
        'ERROR': logging.ERROR,
        'FATAL': logging.FATAL,
        'WARN': logging.WARN,
    }

    def __init__(self, api_keys=[], dev_key=None, log_level='INFO'):
        """
        Main class constructor. Parameters:
            api_keys - List: contains a number of api_keys to act upon
            dev_key - String: a 48 char string containing your developer key (optional)
            log_level - String: One of INFO, DEBUG, ERROR, FATAL or WARN (default: INFO)
        """

        self._set_logger(self._log_levels[log_level.upper()])
        if api_keys:
            api_keys = set(api_keys)
        for api_key in api_keys:
            if self._valid_key(api_key):
                self._api_keys.add(api_key)
            else:
                self._warn('Invalid API key "%s"' % api_key)
        if dev_key:
            if self._valid_key(dev_key):
                self.dev_key = dev_key
            else:
                self._warn('Invalid developer key "%s"' % dev_key)

    def _public(self):
        "Returns a list with the 'public' methods for this class"

        public = []
        for x in dir(self):
            if not x.startswith('_'):
                public.append(x)

        return public

    def _valid_key(self, key):
        """
        Really simple validation for api/developer keys. Params:
            key - String: A string that complies with NMA's policies for keys
        """

        return isinstance(key, str)  and len(key) == 48

    def _set_logger(self, level):
        "Sets the logger object for the main class"

        format='%(name)s: %(levelname)-8s %(message)s'
        logging.basicConfig(format=format)
        self._log = logging.getLogger(USER_AGENT)
        self._log.setLevel(level)

    def _info(self, message):
        self._log.log(logging.INFO, message)

    def _debug(self, message):
        self._log.log(logging.DEBUG, message)

    def _warn(self, message):
        self._log.log(logging.WARN, message)

    def _error(self, message):
        self._log.log(logging.ERROR, message)

    def _fatal(self, message, exit_code=5):
        self._log.log(logging.FATAL, message)
        if exit_code:
            sys.exit(exit_code)

    def _call(self, endpoint, method, data={}):
        """
        Makes an HTTP(S) request to the NMA servers. Params:
            method - String: GET or POST
            data - Dict: Fields to send in the request
        """

        method = method.upper()
        headers = {
            'user-agent': USER_AGENT,
        }

        if method == 'POST':
            headers['content-type'] = 'application/x-www-form-urlencoded'

        self._debug('Headers: %s' % headers)
        self._debug('Method: %s' % method)
        self._debug('Data: %s' % data)

        body = urllib.urlencode(data)
        url = '%s/%s' % (BASE_URL, endpoint)
        if method == 'GET':
            url = '%s?%s' % (url, body)
        self._debug('Body is %s' % body)
        ht = httplib2.Http()
        resp, content = ht.request(url, method, headers=headers, body=body)
        self._debug('Response headers: %s' % (resp,))

        if int(resp['status']) == 200:
            content = minidom.parseString(content)
            ret = content.getElementsByTagName('success')
            if ret:
                ret = ret[0]
                self._return = dict(ret.attributes.items())
                self._debug('Remaining calls: %(remaining)s, reset time: %(resettimer)s' % self._return)
                return True
            else:
                ret = content.getElementsByTagName('error')[0]
                self._return = dict(ret.attributes.items())
                self._return['message'] = ret.firstChild.data
                self._debug('Error data: %s' % self._return)
                if self._return['code'] == '402':
                    self._error('%(message). Reset time: %(resettimer)')
                else:
                    self._error('An error was returned from the service: %(message)s' % self._return)
                return False
        else:
            self._error('There seems to be an error when making the call:')
            self._error('Response: code=%(status)s, type=%(content-type)s' % resp)

    def notify(self, application, event, message, priority='normal'):
        """
        Sends a push notification. Params:
            application - String: Application sending the notification
            event - String: Title, or short description
            message - String: Notification message
            priority - String: one of low, moderate, normal, high, emergency
        """

        if len(application) > 256:
            self._warn('Application length is > 256, will be truncated')
        if len(event) > 1000:
            self._warn('Event length is > 1000, will be truncated')
        if len(message) > 10000:
            self._warn('The message length is > 10000, will be truncated')

        level = 0
        for k,v in NOTIFY_LEVELS.items():
            if priority in k.split(','):
                level = v
                break

        for api_key in self._api_keys:
            self._debug('Sending notification with API key %s' % api_key)
            data = {
                'apikey': api_key.encode('utf8'),
                'application': application[:256].encode('utf8'),
                'event': event[:1000].encode('utf8'),
                'description': message[:10000].encode('utf8'),
                'priority': level,
            }
            if self._dev_key:
                data['developerkey'] = self._dev_key

            if self._call(endpoint='notify', method='POST', data=data):
                self._info('Message to API key %s... was sent' % api_key[:6])
            else:
                self._error('Message to API key %s... could not be sent' % api_key[:6])

    def verify(self, api_keys=[]):
        """
        Verifies a list of api_keys against NMA's service. Params:
            api_keys - List: A list of api_keys strings. These get added
                to the ones previously used in the the object constructor
                (if there were any)
        """

        self._debug('Validating %s' % (self._api_keys,))
        for api_key in self._api_keys:
            if self._valid_key(api_key):
                self._api_keys.add(api_key)
            else:
                self._warn('Invalid API key "%s"' % api_key)

        for api_key in self._api_keys:
            self._debug('Validating key "%s"' % api_key)
            data = { 'apikey': api_key.encode('utf8'), }
            if self._dev_key:
                data['developerkey'] = self._dev_key.encode('utf8')
            if self._call(endpoint='verify', method='POST', data=data):
                self._info('The API key %s is valid' % api_key)
            else:
                self._error('The API key %s is invalid' % api_key)


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--version', action='version',
        version='%s v%s' % (NAME, VERSION))
    parser.add_argument('--log-level', '-L', default='INFO',
        help='Log level to run this app with')
    parser.add_argument('--dev-key', '-D', help='Developer key')
    parser.add_argument('--api-keys', '-A', action='append',
        help='API keys', required=True, default=[])
    subparsers = parser.add_subparsers(dest='subparser_name')

#   verify
    parser_verify = subparsers.add_parser('verify')
    assert parser_verify

#   notify
    parser_notify = subparsers.add_parser('notify',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser_notify.add_argument('--application', '-a', required=True,
        help='The name of the application that is generating the call')
    parser_notify.add_argument('--event', '-e', required=True,
        help='The event that is been notified. Depending on your application, '
        'it can be a subject or a brief description')
    choices = []
    for k in NOTIFY_LEVELS.keys():
        choices.extend(k.split(','))
    parser_notify.add_argument('--priority', '-p', default='normal',
        choices=choices,
        help='A priority level for this notification. You can use numbers '
        'from -2 to 2, or legends from low to emergency, or nagios-style '
        'levels like PROBLEM, etc')
    parser_notify.add_argument('--message', '-m',
        help='Message to be sent', required=True)

    args = parser.parse_args()

    if args.log_level == 'DEBUG':
        httplib2.debuglevel=4

    nma = NMAPython(api_keys=args.api_keys, dev_key=args.dev_key,
        log_level=args.log_level)
    if args.subparser_name == 'verify':
        return nma.verify()
    elif args.subparser_name == 'notify':
        return nma.notify(application=args.application, event=args.event,
            message=args.message, priority=args.priority)
    else:
        logging.fatal('Invalid function "%s"' % args.subparser_name)


if __name__ == '__main__':
    sys.exit(main())

