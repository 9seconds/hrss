concierge
*********

|PyPI| |Build Status| |Code Coverage|

``concierge`` is a small utility/daemon which is intended to help humans
to maintain their SSH configs.

.. contents::
    :depth: 2
    :backlinks: none


Introduction
============

There is not problems with SSH config format: it works for decades and
is going to work for my children I guess. This utility will die, but one
will update his ``~/.ssh/config`` to access some network server.

The problem with SSH that it really hard to scale. I am not quite sure
about other people jobs, but on my current and previous jobs I was
used to maintain quite large sets of records in SSH configs. Usual
deployment of some modern app consist several machines (let's say ``X``)
and during development we are using several stage environments (let's
say ``Y``). So, frankly, you need to have ``X * Y`` records in your
``~/.ssh/config``. Only for work.

Sometimes you need to jugle with jump hosts. Sometimes your stage is
moving to another set of IPs. Sometimes life happens and it is quite
irritating to manage these configuration manually.

I did a lot of CSS stylesheets and SSH config management is pretty close
to that. I want to have SASS_ for SSH config. The main goal of this
tool is to provide user with some templating and clutter-free config
management in SASS way.


Demo
====

.. image:: https://asciinema.org/a/dqxhschtqyx7lxfda25irbgh5.png
    :alt: Asciinema screencast
    :width: 700
    :target: https://asciinema.org/a/dqxhschtqyx7lxfda25irbgh5


Installation
============

Installation is quite trivial:

.. code-block:: shell

    $ pip install concierge

or if you want to install it manually, do following:

.. code-block:: shell

    $ git clone https://github.com/9seconds/concierge.git
    $ cd concierge
    $ python setup.py install

By default, no template support is going to be installed. If you want to
use Mako_ or Jinja2_, please refer to `Templaters`_ section.

Also, it is possible to install support of `libnotify
<https://developer.gnome.org/libnotify/>`_. Please install tool like
this:

.. code-block:: shell

    $ pip install concierge[libnotify]

In that case, you will have a desktop notifications about any problem
with parsing of your ``~/.conciergerc``. Yep, these Ubuntu popups on the
right top of the screen.

If you have a problems with Pip installation (with modifiers, for
example), please update your pip and setuptools first.

.. code-block:: shell

    $ pip install --upgrade pip setuptools

Eventually there will be no such problem anywhere.

Please be noticed, that ``concierge`` is **Python 3** only tool. It
should work on ``cPython >= 3.3`` without any problems. Come on, Python
3.4 is bundled even with CentOS 7!

After installation, 2 utilities will be available:

* ``concierge-check``
* ``concierge``


Templaters
----------

``concierge`` comes with support of additional templaters, you may plug
them in installing the packages from PyPI. At the time of writing,
support of following templaters was done:

* `concierge-mako <https://github.com/9seconds/concierge-mako>`_ -
  support of Mako_ templates
* `concierge-jinja <https://github.com/9seconds/concierge-jinja>`_ -
  support of Jinja2_ templates

To install them just do

.. code-block:: shell

    $ pip install concierge-mako

And ``concierge`` will automatically recognizes support of Mako and now
one may use ``concierge -u mako`` for her ``~/.conciergerc``.


concierge-check
---------------

``concierge-check`` is a tool to verify syntax of your
``~/.conciergerc`` file. Please check `Syntax description`_ to get on
speed.

Also, it supports a number of options but they are pretty trivial.

Please remember, that both ``concierge-check`` and ``concierge``
use syslog for logging data in process. Options like ``--debug`` or
``--verbose`` will affect only stderr logging, syslog will have only
errors.


concierge
---------

``concierge`` is intended to work in daemon mode. It converts between
your ``~/.conciergerc`` and destination ``~/.ssh/config`` (so
`Installation`_ magic work in that way).

I use systemd so ``concierge`` is bundled to support it. To get an
instructions of how to use the tool with systemd, please run following:

.. code-block:: shell

    $ concierge --systemd

It will printout an instructions. If you do not care, please run following:

.. code-block:: shell

    $ eval "$(concierge --systemd --curlsh)"

It will install systemd user unit and run concierge daemon automatically.

``concierge`` supports the same options and behavior as
`concierge-check`_ so please track your syslog for problems.


Syntax description
==================

Well, there is no big difference between plain old ``ssh_config(5)`` and
``concierge`` style. Base is the same so please check the table with
examples to understand what is going to be converted and how.

Syntax came from the way I structure my SSH configs for a long time    .
Basically I am trying to keep it in the way it looks like hierarchical .

Let's grow the syntax. Consider following config

::

    Host m
        HostName 127.0.0.1

    Host me0
        HostName 10.10.0.0

    Host me1
        HostName 10.10.0.1

    Host m me0 me1
        Compression no
        ProxyCommand ssh -W %h:%p env1
        User nineseconds

    Host *
        Compression yes
        CompressionLevel 9


So far so good. Now let's... indent!

::

    Host m
        HostName 127.0.0.1

        Host me0
            HostName 10.10.0.0
            ProxyCommand ssh -W %h:%p env1

        Host me1
            HostName 10.10.0.1
            ProxyCommand ssh -W %h:%p env1

        Host m me0 me1
            Compression no
            User nineseconds

    Host *
        Compression yes
        CompressionLevel 9


It is still valid SSH config. And valid ``concierge`` config. Probably
you already do similar indentation to visually differ different server
groups. Let's check what do we have here: we have prefixes, right. And
most of options are quite common to the server groups (environments).

Now let's eliminate ``Host m me0 me1`` block. This would be invalid SSH
config but valid ``conciergerc`` config. Also I am going to get rid of
useless prefixes and use hierarchy to determine full name (``fullname =
name + parent_name``).

Please be noticed that all operations maintain effectively the same
``conciergerc`` config.

::

    Host m
        Compression no
        HostName 127.0.0.1
        User nineseconds

        Host e0
            HostName 10.10.0.0
            ProxyCommand ssh -W %h:%p env1

        Host e1
            HostName 10.10.0.1
            ProxyCommand ssh -W %h:%p env1

    Host *
        Compression yes
        CompressionLevel 9


Okay. Do we need rudiment ``Host *`` section? No, let's move everything
on the top. Idea is the same, empty prefix is ``*``.

::

    Compression yes
    CompressionLevel 9

    Host m
        Compression no
        HostName 127.0.0.1
        User nineseconds

        Host e0
            HostName 10.10.0.0
            ProxyCommand ssh -W %h:%p env1

        Host e1
            HostName 10.10.0.1
            ProxyCommand ssh -W %h:%p env1


By the way, you may see, that indentation defines parent is the same
way as Python syntax is organized. So following config is absolutely
equivalent.

::

    Compression yes

    Host m
        Compression no
        HostName 127.0.0.1
        User nineseconds

        Host e0
            HostName 10.10.0.0
            ProxyCommand ssh -W %h:%p env1

        Host e1
            HostName 10.10.0.1
            ProxyCommand ssh -W %h:%p env1

    CompressionLevel 9


This is a basic. But if you install ``concierge`` with support of Mako or
Jinja2 templates, you may use them in your ``~/.conciergerc``.

::

    Compression yes
    CompressionLevel 9

    Host m
        Compression no
        HostName 127.0.0.1
        User nineseconds

        % for i in range(2):
        Host e${i}
            HostName 10.10.0.${i}
            ProxyCommand ssh -W %h:%p env1
        % endfor

This is a Mako template I use. Please refer `Mako
<http://docs.makotemplates.org/en/latest/syntax.html>`__ and `Jinja2
<http://jinja.pocoo.org/docs/dev/templates/>`__ documentation for details.

By the way, if you want to hide some host you are using for grouping only,
please prefix it with ``-`` (``-Host``).


Examples
--------

Here are some examples. Please do not hesitate to check `Demo`_, pause it,
look around.

+----------------------------------------+--------------------------------------------+
| Source, converted from (~/.concierge)  | Destination, converted to (~/.ssh/config)  |
+========================================+============================================+
| ::                                     | ::                                         |
|                                        |                                            |
|   Host name                            |   Host name                                |
|       HostName 127.0.0.1               |       HostName 127.0.0.1                   |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+
| ::                                     | ::                                         |
|                                        |                                            |
|   Compression yes                      |   Host name                                |
|                                        |       HostName 127.0.0.1                   |
|   Host name                            |                                            |
|       HostName 127.0.0.1               |   Host *                                   |
|                                        |       Compression yes                      |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+
| ::                                     | ::                                         |
|                                        |                                            |
|   Compression yes                      |   Host name                                |
|                                        |       HostName 127.0.0.1                   |
|   Host name                            |                                            |
|       HostName 127.0.0.1               |   Host *                                   |
|                                        |       Compression yes                      |
|   Host *                               |       CompressionLevel 9                   |
|       CompressionLevel 9               |                                            |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+
| ::                                     | ::                                         |
|                                        |                                            |
|   Compression yes                      |   Host name                                |
|                                        |       HostName 127.0.0.1                   |
|   Host name                            |                                            |
|       HostName 127.0.0.1               |   Host nameq                               |
|                                        |       HostName node-1                      |
|       Host q                           |       ProxyCommand ssh -W %h:%p env1       |
|           ViaJumpHost env1             |                                            |
|           HostName node-1              |   Host *                                   |
|                                        |       Compression yes                      |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+
| ::                                     | ::                                         |
|                                        |                                            |
|   Compression yes                      |   Host nameq                               |
|                                        |       HostName node-1                      |
|   -Host name                           |       ProxyCommand ssh -W %h:%p env1       |
|       HostName 127.0.0.1               |                                            |
|                                        |   Host *                                   |
|       Host q                           |       Compression yes                      |
|           ViaJumpHost env1             |                                            |
|           HostName node-1              |                                            |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+
| ::                                     | ::                                         |
|                                        |                                            |
|   Compression yes                      |   Host blog                                |
|                                        |       User sa                              |
|   Host m                               |                                            |
|       User nineseconds                 |   Host me0                                 |
|                                        |       HostName 10.10.0.0                   |
|       % for i in range(2):             |       Protocol 2                           |
|       Host e${i}                       |       ProxyCommand ssh -W %h:%p gw2        |
|           HostName 10.10.0.${i}        |       User nineseconds                     |
|           ViaJumpHost gw2              |                                            |
|       % endfor                         |   Host me1                                 |
|                                        |       HostName 10.10.0.1                   |
|       Protocol 2                       |       Protocol 2                           |
|                                        |       ProxyCommand ssh -W %h:%p gw2        |
|   Host blog                            |       User nineseconds                     |
|       User sa                          |                                            |
|                                        |   Host *                                   |
|                                        |       Compression yes                      |
|                                        |                                            |
+----------------------------------------+--------------------------------------------+


.. _SASS: http://sass-lang.com
.. _Mako: http://www.makotemplates.org
.. _Jinja2: http://jinja.pocoo.org

.. |PyPI| image:: https://img.shields.io/pypi/v/concierge.svg
    :target: https://pypi.python.org/pypi/concierge

.. |Build Status| image:: https://travis-ci.org/9seconds/concierge.svg?branch=master
    :target: https://travis-ci.org/9seconds/concierge

.. |Code Coverage| image:: https://codecov.io/github/9seconds/concierge/coverage.svg?branch=master
    :target: https://codecov.io/github/9seconds/concierge?branch=master
