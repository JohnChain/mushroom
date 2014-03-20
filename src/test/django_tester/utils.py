#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *

def gene_django_frame(head, version, json_inst):
    Body = json.dumps(json_inst)
    Version = '{:{fill}{width}{base}}'.format(version, fill = '0', width = 2 * D_version_byte, base = 'x')
    Length  = '{:{fill}{width}{base}}'.format(len(Body), fill = '0', width = 2 * D_lenght_byte, base = 'x')
    message = head + a2b_hex(Version) + a2b_hex(Length) + Body
    return message