asunder
-------

It rips your CDs as soon as you insert them, and spits them out as soon as it
is done ripping. It tells you via XMPP when a disc needs switching. I made it
so I could rip my entire CD collection more quickly.

Assumptions
-----------

You are running Debian GNU/Linux unstable. (Others may work but I haven't
tested them yet.)

You have Morituri_ installed. 

.. _Morituri: https://github.com/thomasvs/morituri

Configuring
-----------

You need to configure asunder. Write a file $HOME/.config/asunder/config.ini
that looks like this::

    [notify]
    jid = my_jid@example.com
    password = password
    to = jid1@example.com
         jid2@example.com

The jid and password are used to log asunder in to an XMPP server. When
notifications are sent, one is sent to each "to" jid.

Unfortunately asunder does not presently deal with XMPP rosters; you'll need to
use a usual XMPP client to connect to the server with asunder's credentials,
and add asunder's jid to the roster of each person who will receive
notifications (this may be called "inviting [asunder's jid] to chat").

Running
-------

Run the asunder script. It will tell you a lot on standard output about what it
is doing. Insert an audio disc into a CD-ROM drive. asunder should notice the
disc and begin ripping it within fifteen seconds. If you have many CD-ROM
drives, insert a disc into each. Fun times!

When a rip is finished, the disc should pop out, and you'll get an XMPP message
saying to switch the disc.

Opportunities for enhancement
-----------------------------

asunder only supports XMPP, and the initial setup isn't as cool as it could be.

You can't turn the XMPP notifications off if you don't want them.

asunder likely does not do anything sane when there is no configuration file.

asunder uses udisks 1 to detect that an audio CD has been inserted. Some
distros may use udisks 2 nowadays.

If you were to write a disc detector module that uses another method (like
udisks 2) to detect audio CDs, there's no means to switch that in via the
configuration file.

The documentation is sparse and poor.

The messages are hard-coded and only show up in English: asunder needs l10n.

Errors in subprocesses are not handled well, if at all.

