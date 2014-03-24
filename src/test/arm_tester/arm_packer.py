from mushroom_pb2 import *
from head import *
from utils import *

def read_time():
    session = 1
    type    = 1
    version = A_VERSION
    connection = -1
    source = -1
    header = gene_message_header(READ_TIME, session, type, version, connection, source)
    main_frame = gene_arm_frame(header, '')
    print 'Will send read_time'
    return main_frame

def read_time_response(proto_inst, handler):
    data = SynTime()
    data.ParseFromString(proto_inst['data'])
    print 'Get one read_time_response, time : %s' %(data.timestamp)


def update_time_response(proto_inst, handler):
    header = proto_inst['header_inst']
    data = SynTime()
    data.ParseFromString(proto_inst['data'])
    print 'Get one update_time, info : %s' %(data.timestamp)
    
    session = header.session
    type    = 1
    version = header.version
    connection = header.connection
    source = header.source
    header = gene_message_header(UPDATE_TIME_RESPONSE, session, type, version, connection, source)
    
    data = ResponseCode()
    data.code = 0
    data.log = 'Update time succeed'
    main_frame = gene_arm_frame(header, data)
    print 'Will send update_time_response'
    
    handler.send(main_frame)
    return main_frame

def read_controller_state_response(proto_inst, handler):
    header = proto_inst['header_inst']
    data = Controller()
    data.ParseFromString(proto_inst['data'])
    print 'Get one read_controller_state, info: %d, %d' %(data.controller_id, data.state)

    controller_id = data.controller_id
    
    session = header.session
    type    = 1
    version = header.version
    connection = header.connection
    source = header.source
    header = gene_message_header(READ_CONTROLLER_STATE_RESPONSE, session, type, version, connection, source)

    data = Controller()
    data.controller_id = controller_id
    data.state = Controller.OPEN

    main_frame = gene_arm_frame(header, data)
    print 'Will send read_controller_state_response'
    handler.send(main_frame)
    return main_frame

def update_controller_state_response(proto_inst, handler):
    
    header = proto_inst['header_inst']
    data = Controller()
    data.ParseFromString(proto_inst['data'])
    print 'Get one updata_controller_state, info: %d, %d' %(data.controller_id, data.state)

    controller_id = data.controller_id
    
    session = header.session
    type    = 1
    version = header.version
    connection = header.connection
    source = header.source
    header = gene_message_header(UPDATE_CONTROLLER_STATE_RESPONSE, session, type, version, connection, source)
    
    data = ResponseCode()
    data.code = 0
    data.log = 'Updata controller succeed!'

    main_frame = gene_arm_frame(header, data)
    print 'Will send_update_controller_response'
    handler.send(main_frame)
    return main_frame

def read_sensor_data_response(proto_inst, handler):
    header = proto_inst['header_inst']
    data = Room()
    data.ParseFromString(proto_inst['data'])
    print 'Get one read_sensor_data, info: %d' %(data.room_id)

    room_id = data.room_id

    session = header.session
    type    = 1
    version = header.version
    connection = header.connection
    source = header.source
    header = gene_message_header(READ_SENSOR_DATA_RESPONSE, session, type, version, connection, source)
    
    data = SensorData()
    data.room.room_id = room_id
    data.time.timestamp = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    #data.sensor = Sensor()
    
    temp = data.sensor.add()
    humi = data.sensor.add()
    co2  = data.sensor.add()
    light= data.sensor.add() 
    
    temp.id = 1
    temp.type = TEMP
    temp.value = 101
    
    humi.id = 2
    humi.type = HUMI
    humi.value = 201
    
    co2.id = 4
    co2.type = CO2
    co2.value = 401
    
    light.id = 3
    light.type = LIGHT
    light.value = 401

    main_frame = gene_arm_frame(header, data)
    print 'Will send read_sensor_data_response'
    
    handler.send(main_frame)
    return main_frame

def push_sensor_data():
    session = -1
    type    = 1
    version = A_VERSION
    connection = -1
    source = -1
    header = gene_message_header(SENSOR_DATA_PUSH, session, type, version, connection, source)

    data = SensorData()
    data.room.room_id = 1
    data.time.timestamp = (datetime.now()).strftime('%Y-%m-%d %H:%M:%S')
    
    temp = data.sensor.add()
    humi = data.sensor.add()
    co2  = data.sensor.add()
    light= data.sensor.add() 
    
    temp.id = 1
    temp.type = TEMP
    temp.value = 101
    
    humi.id = 2
    humi.type = HUMI
    humi.value = 201
    
    co2.id = 4
    co2.type = CO2
    co2.value = 401
    
    light.id = 3
    light.type = LIGHT
    light.value = 301

    main_frame = gene_arm_frame(header, data)
    print 'Will send push_sensor_data'
    return main_frame

def init():
    session = -1
    type    = 1
    version = A_VERSION
    connection = -1
    source = -1
    header = gene_message_header(INIT, session, type, version, connection, source)
    
    data = Init()
    one_room = data.roomconf.add()
    one_room.id = 1
    
    one_sensor = one_room.sensor.add()
    one_sensor.id = 5
    one_sensor.type = TEMP
    
    one_controller = one_room.controller.add()
    one_controller.controller_id = 1
    one_controller.type = XUNHUAN_FAN

    one_config = data.config.add()
    one_config.key = 'TIME_SYNC_CYCLE'
    one_config.val = 60
    
    main_frame = gene_arm_frame(header, data)
    print 'Will send init msg'
    return main_frame
    
arm_protocal = {
    READ_TIME_RESPONSE      : read_time_response,
    UPDATE_TIME             : update_time_response,
    READ_CONTROLLER_STATE   : read_controller_state_response,
    UPDATE_CONTROLLER_STATE : update_controller_state_response,
    READ_SENSOR_DATA        : read_sensor_data_response,
    }
