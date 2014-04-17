#!/usr/bin/env python
# -*- coding: utf-8 -*-
from head import *
from mushroom_pb2 import *

def gene_message_header(message_id, session, type, version, connection, source = BIRTH_TYPE_AUTO):
    temp_header = MessageHeader()
    temp_header.message_id  = message_id
    temp_header.session     = session
    temp_header.type        = type
    temp_header.connection  = connection
    temp_header.source      = source
    temp_header.version     = version
    
    message_header          = temp_header.SerializeToString()
    return message_header

def gene_arm_frame(message_header = '', data = '', ):
    if data != '':
        data = data.SerializeToString()
    
    m_header_len = '{:{fill}{width}{base}}'.format(len(message_header), fill = '0', width = 2 * byte_m_header_len, base = 'x')
    m_header_len = a2b_hex(m_header_len)
#     print "heaer_len = %d" %len(message_header)
    

    temp_pkg_len = len(message_header) + len(data) + byte_m_header_len
    pkg_len = '{:{fill}{width}{base}}'.format(temp_pkg_len, fill = '0', width = 2 * byte_pkg_len, base = 'x')
    pkg_len = a2b_hex(pkg_len)
#     print 'Pkg_len = %d' %temp_pkg_len
    main_frame = A_HEAD + pkg_len + m_header_len + message_header + data
    return main_frame

def gene_django_frame(head, version, json_inst):
    Body = json.dumps(json_inst)
    Version = '{:{fill}{width}{base}}'.format(version, fill = '0', width = 2 * D_version_byte, base = 'x')
    Length  = '{:{fill}{width}{base}}'.format(len(Body), fill = '0', width = 2 * D_lenght_byte, base = 'x')
    message = head + a2b_hex(Version) + a2b_hex(Length) + Body
    return message