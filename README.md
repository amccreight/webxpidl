webxpidl
========

Automated generation of coercions from XPIDL to WebIDL for Gecko, as one step
towards allowing JS to implement WebIDL interfaces.

See https://bugzilla.mozilla.org/show_bug.cgi?id=785193


To run
------

Set PYTHONPATH to the directory that includes the WebIDL parser, like so:

PYTHONPATH=<mozillasourcedirectory>/dom/bindings/parser/ python WebXPIDL.py <WebIDL file>