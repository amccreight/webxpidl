# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

import os
import sys

import WebIDL

# WebIDL to XPIDL translator for Gecko.


InterfaceConfig = {
    'ClientRectList' : {
        'nativeType': 'nsClientRectList',
        'uuid' : 'c648b9e0-1553-11e2-892e-0800200c9a66',
    },
}

def uuidOf(n):
    return InterfaceConfig[n]['uuid'];

def xifyName(n):
    return 'nsI' + n

Primitivizer = {
    WebIDL.IDLBuiltinType.Types.unsigned_long : 'unsigned long'
}


def typeString(t):
    if isinstance(t, WebIDL.IDLBuiltinType):
        if t.isPrimitive():
            return Primitivizer[t.tag()]

    # I think all types are Nullable in XPIDL, so ignore this.
    if isinstance(t, WebIDL.IDLNullableType):
        return typeString(t.inner)

    # Not sure what this is, so I'll just strip it off..
    if isinstance(t, WebIDL.IDLWrapperType):
        return xifyName(t.name)

    return 'UNKNOWN_TYPE(' + str(t) + ')'


def argumentString(a):
    assert(not a.optional)
    # Probably othing things we should handle, as well.
    s = 'in ' + typeString(a.type) + ' ' + a.identifier.name
    return s


def convertArguments(aa):
    s = ''
    for a in aa:
        s += argumentString(a) + ', '
    return s[:-2]


def convertMethod(m):
    sys.stdout.write('  ')

    # generate the special tag
    if m.isGetter():
        sys.stdout.write('[getter] ')
    elif m.isSetter():
        sys.stdout.write('[setter] ')
    sigs = m.signatures()
    assert(len(sigs) == 1)
    sig = sigs[0] # why isn't this an IDLMethodOverload?
    sys.stdout.write('{0} {1}({2})\n'.format(typeString(sig[0]), \
                                             m.identifier.name, \
                                             convertArguments(sig[1])))


def convertAttr(a):
    sys.stdout.write('  ')
    if a.readonly:
        sys.stdout.write('readonly ')
    sys.stdout.write('attribute {0} {1};\n'.format(typeString(a.type), \
                                                   a.identifier.name))

def convertConst(c):
    print c

def convertMember(m):
    if m.isMethod():
        convertMethod(m)
    elif m.isAttr():
        convertAttr(m)
    else:
        assert(isConst())
        convertConst(m)

def convertDecl(x):
    if x.isExternal():
        sys.stdout.write('interface ' + xifyName(x.identifier.name) + ';\n')
    else:
        n = x.identifier.name
        sys.stdout.write('\n')
        sys.stdout.write('[uuid({0})]\n'.format(uuidOf(n)))
        sys.stdout.write('interface {0}\n'.format(xifyName(n)))
        sys.stdout.write('{\n')
        for m in x.members:
            convertMember(m)
        sys.stdout.write('}\n')

def licenseBoilerplate():
    sys.stdout.write('/* This Source Code Form is subject to the terms of the Mozilla Public\n')
    sys.stdout.write(' * License, v. 2.0. If a copy of the MPL was not distributed with this\n')
    sys.stdout.write(' * file, You can obtain one at http://mozilla.org/MPL/2.0/. */\n')
    sys.stdout.write('\n')


# from WebIDL.py (slightly altered)
def parseIt():
    # Parse arguments.
    from optparse import OptionParser
    usageString = "usage: %prog [options] files"
    o = OptionParser(usage=usageString)
    o.add_option("--cachedir", dest='cachedir', default=None,
                 help="Directory in which to cache lex/parse tables.")
    o.add_option("--verbose-errors", action='store_true', default=False,
                 help="When an error happens, display the Python traceback.")
    (options, args) = o.parse_args()

    if len(args) < 1:
        o.error(usageString)

    fileList = args
    baseDir = os.getcwd()

    # Parse the WebIDL.
    parser = WebIDL.Parser(options.cachedir)
    try:
        for filename in fileList:
            fullPath = os.path.normpath(os.path.join(baseDir, filename))
            f = open(fullPath, 'rb')
            lines = f.readlines()
            f.close()
            #print fullPath
            parser.parse(''.join(lines), fullPath)
        return parser.finish()
    except WebIDL.WebIDLError, e:
        if options.verbose_errors:
            traceback.print_exc()
        else:
            print e


def main():
    licenseBoilerplate()
    for x in parseIt():
        convertDecl(x)

if __name__ == '__main__':
    main()

