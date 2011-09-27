Overview
========

``nma-python`` is a Python library/CLI tool to interact with the [Notify My Android service](http://nma.usk.bz/).

The goal is to provide complete coverage over NMA's API, and it will be growing as the API does.


Installation
============

``nma-python`` is registered in the [Python Package Index](http://pypi.python.org/pypi/nma-python) so in theory you can just:

    $ pip install nma-python

This should pull nma-python and the required libraries


Requirements
------------

 * Python 2.6+
 * httplib2


Usage
=====

This library will try to cover the entire [NMA API](http://nma.usk.bz/api.php), version represents how many methods are covered, for example the 0.2.x series means 2 methods are fully supported. You can pass along a set of common options:

    $ nma_cli -h
    usage: nma_cli [-h] [--version] [--log-level LOG_LEVEL] [--dev-key DEV_KEY]
        --api-keys API_KEYS {subcommand}

    optional arguments:
      -h, --help            show this help message and exit
      --version             show program's version number and exit
      --log-level LOG_LEVEL, -L LOG_LEVEL
                            Log level to run this app with (default: INFO)
      --dev-key DEV_KEY, -D DEV_KEY
                            Developer key (default: None)
      --api-keys API_KEYS, -A API_KEYS
                            API keys (default: [])


Verify
------

This will verify one or more API keys against the NMA service:

    $ nma_cli -A foobar verify
    nma-python/v0.2.2: WARNING  Invalid API key "foobar"

    $ nma_cli -A eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee verify
    nma-python/v0.2.2: ERROR    An error was returned from the service: The API key is not valid.
    nma-python/v0.2.2: ERROR    The API key eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee is invalid

    $ nma_cli -A $VALID_API_KEY verify
    nma-python/v0.2.2: INFO     The API key $VALID_API_KEY is valid


Notify
------

This will try to send a push notification to the API key(s) provided. Basic usage:

    $ nma_cli notify -h
    usage: nma_cli notify [-h] --application APPLICATION --event EVENT
                      [--priority {low,moderate,normal,high,emergency}]
                      --message MESSAGE

    arguments:
      -h, --help            show this help message and exit
      --application APPLICATION, -a APPLICATION
                            The name of the application that is generating the
                            call (default: None)
      --event EVENT, -e EVENT
                            The event that is been notified. Depending on your
                            application, it can be a subject or a brief
                            description (default: None)
      --priority {low,moderate,normal,high,emergency}, -p {low,moderate,normal,high,emergency}
                            A priority level for this notification (default:
                            normal)
      --message MESSAGE, -m MESSAGE
                            Message to be sent (default: None)

Examples:

    $ nma_cli -A eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee notify -a myapp01 -e event02 -m "This shall return invalid"
    nma-python/v0.2.2: ERROR    An error was returned from the service: None of the API keys provided were valid.
    nma-python/v0.2.2: ERROR    Message to API key eeeeee... could not be sent

    $ nma_cli -A $VALID_API_KEY notify -a myapp01 -e event02 -m "This shall send you a cute push normal notification"
    nma-python/v0.2.2: INFO     Message to API key XXXXXX... was sent

    $ nma_cli -A $VALID_API_KEY notify -a myapp02 -e event03 -p emergency -m "This shall send you an emergency push notification"
    nma-python/v0.2.2: INFO     Message to API key XXXXXX... was sent

