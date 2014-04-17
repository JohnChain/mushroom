#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
from PyQt4 import QtGui, QtCore
from django_packer import *
from django_frame_main import *

class FormWidget(QtGui.QWidget):

    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        
        self.django_simulator = ''
        self.dj_reciver = ''
        
        self.initUI()
        
    def initUI(self):
        self.v_layout = QtGui.QVBoxLayout(self)
        
        self.lbl_ip = QtGui.QLabel(self)
        self.lbl_ip.move(60, 40)
        self.lbl_ip.setText('IP')
        self.lbl_port = QtGui.QLabel(self)
        self.lbl_port.move(60, 200)
        self.lbl_port.setText('PORT')

        self.edit_ip = QtGui.QLineEdit(self)
        self.edit_ip.setText('10.18.50.66')
        self.edit_ip.move(60, 100)
        self.edit_port = QtGui.QLineEdit(self)
        self.edit_port.setText('9001')
        self.edit_port.move(60, 250)

        self.btn_connect = QtGui.QPushButton("connect")
        self.btn_connect.setCheckable(True)
        self.btn_connect.clicked[bool].connect(self.onConnect)
        
        self.h_layout1 = QtGui.QHBoxLayout(self)
        self.h_layout1.addWidget(self.lbl_ip)
        self.h_layout1.addWidget(self.edit_ip)
        self.h_layout1.addWidget(self.lbl_port)
        self.h_layout1.addWidget(self.edit_port)
        self.h_layout1.addWidget(self.btn_connect)
        
        
        self.controller_read_lbl_1 = QtGui.QLabel(self)
        self.controller_read_lbl_2 = QtGui.QLabel(self)
        self.controller_read_lbl_3 = QtGui.QLabel(self)
        
        self.controller_read_lbl_1.setText('Room ID')
        self.controller_read_lbl_2.setText('Controller ID')
        self.controller_read_lbl_3.setText('State')
        
        self.controller_read_txt_1 = QtGui.QLineEdit(self)
        self.controller_read_txt_2 = QtGui.QLineEdit(self)
        self.controller_read_txt_3 = QtGui.QLineEdit(self)
        
        self.controller_read_btn_1 = QtGui.QPushButton(self)
        self.controller_read_btn_1.setText('Read State')
        self.controller_read_btn_1.clicked.connect(self.onReadController)
        
        self.controller_read_formlayout = QtGui.QFormLayout(self)
        self.controller_read_formlayout.addRow(self.controller_read_lbl_1, self.controller_read_txt_1)
        self.controller_read_formlayout.addRow(self.controller_read_lbl_2, self.controller_read_txt_2)
        self.controller_read_formlayout.addRow(self.controller_read_lbl_3, self.controller_read_txt_3)
        self.controller_read_formlayout.addRow(self.controller_read_btn_1)
        
        self.controller_update_lbl_1 = QtGui.QLabel(self)
        self.controller_update_lbl_2 = QtGui.QLabel(self)
        self.controller_update_lbl_3 = QtGui.QLabel(self)
        
        self.controller_update_lbl_1.setText('Room ID')
        self.controller_update_lbl_2.setText('Controller ID')
        self.controller_update_lbl_3.setText('State')
        
        self.controller_update_txt_1 = QtGui.QLineEdit(self)
        self.controller_update_txt_2 = QtGui.QLineEdit(self)
        self.controller_update_txt_3 = QtGui.QLineEdit(self)
        
        self.controller_update_btn_1 = QtGui.QPushButton(self)
        self.controller_update_btn_1.setText('Update State')
        self.controller_update_btn_1.clicked.connect(self.onUpdateController)
        
        self.controller_update_formlayout = QtGui.QFormLayout(self)
        self.controller_update_formlayout.addRow(self.controller_update_lbl_1, self.controller_update_txt_1)
        self.controller_update_formlayout.addRow(self.controller_update_lbl_2, self.controller_update_txt_2)
        self.controller_update_formlayout.addRow(self.controller_update_lbl_3, self.controller_update_txt_3)
        self.controller_update_formlayout.addRow(self.controller_update_btn_1)
        
        self.h_layout2 = QtGui.QHBoxLayout(self)
        self.h_layout2.addLayout(self.controller_read_formlayout)
        self.h_layout2.addLayout(self.controller_update_formlayout)


        self.log_control_btn_err = QtGui.QPushButton(self)
        self.log_control_btn_cmc = QtGui.QPushButton(self)
        self.log_control_btn_wrk = QtGui.QPushButton(self)
        self.log_control_btn_dbg = QtGui.QPushButton(self)
        
        self.log_control_btn_err.setCheckable(True)
        self.log_control_btn_cmc.setCheckable(True)
        self.log_control_btn_wrk.setCheckable(True)
        self.log_control_btn_dbg.setCheckable(True)
        
        self.log_control_btn_err.setText('error')
        self.log_control_btn_cmc.setText('communication')
        self.log_control_btn_wrk.setText('work')
        self.log_control_btn_dbg.setText('debug')
        
        self.log_control_btn_err.clicked[bool].connect(self.onUpdateLog)
        self.log_control_btn_cmc.clicked[bool].connect(self.onUpdateLog)
        self.log_control_btn_dbg.clicked[bool].connect(self.onUpdateLog)
        self.log_control_btn_wrk.clicked[bool].connect(self.onUpdateLog)
        
        self.log_control_lbl_err = QtGui.QLabel(self)
        self.log_control_lbl_cmc = QtGui.QLabel(self)
        self.log_control_lbl_wrk = QtGui.QLabel(self)
        self.log_control_lbl_dbg = QtGui.QLabel(self)
        
        self.log_btn_v_layout = QtGui.QVBoxLayout(self)
        self.log_btn_v_layout.addWidget(self.log_control_btn_err)
        self.log_btn_v_layout.addWidget(self.log_control_btn_cmc)
        self.log_btn_v_layout.addWidget(self.log_control_btn_wrk)
        self.log_btn_v_layout.addWidget(self.log_control_btn_dbg)
        
        self.log_lbl_v_layout = QtGui.QVBoxLayout(self)
        self.log_lbl_v_layout.addWidget(self.log_control_lbl_err)
        self.log_lbl_v_layout.addWidget(self.log_control_lbl_cmc)
        self.log_lbl_v_layout.addWidget(self.log_control_lbl_wrk)
        self.log_lbl_v_layout.addWidget(self.log_control_lbl_dbg)
        
#         self.log_formlayout = QtGui.QFormLayout(self)
#         self.log_formlayout.addRow(self.log_control_btn_err, self.log_control_lbl_err)
#         self.log_formlayout.addRow(self.log_control_btn_cmc, self.log_control_lbl_cmc)
#         self.log_formlayout.addRow(self.log_control_btn_wrk, self.log_control_lbl_wrk)
#         self.log_formlayout.addRow(self.log_control_btn_dbg, self.log_control_lbl_dbg)
        
        self.h_layout3 = QtGui.QHBoxLayout(self)
        self.h_layout3.addLayout(self.log_btn_v_layout)
        self.h_layout3.addLayout(self.log_lbl_v_layout)
        
        self.v_layout.addLayout(self.h_layout1)
        self.v_layout.addLayout(self.h_layout2)
        self.v_layout.addLayout(self.h_layout3)
#         self.v_layout.addLayout(self.log_formlayout)
        
    def onConnect(self, pressed):
        if pressed:
            try:
                self.ip = self.edit_ip.text()
                self.port = int(self.edit_port.text())
                
                self.django_simulator = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.django_simulator.connect((self.ip, self.port))
                self.btn_connect.setText('Connected')
                
                self.dj_reciver = DjangoFrameMain(self.django_simulator)
                self.init_log_btn()
                
            except socket.error, e:
                self.btn_connect.setText('Unconnected')
                print e
        else:
            self.django_simulator.shutdown(socket.SHUT_RDWR)
            self.django_simulator.close()
            self.btn_connect.setText('Closed')
            
            self.django_simulator = ''
            self.dj_reciver = ''
            
#     def onChanged(self, text):
#         self.ip = self.edit_ip.text()
#         self.port = int(self.edit_port.text())

    def init_log_btn(self):
        main_frame = read_log_state('all')
        self.django_simulator.send(main_frame)
        json_inst = self.dj_reciver.main_receivor()
        if json_inst['code'] == SUC:
            if json_inst['data']['communication'] == 'on':
                self.log_control_btn_cmc.setChecked(True)
                self.log_control_lbl_cmc.setText('ON')
            else:
                self.log_control_btn_cmc.setChecked(False)
                self.log_control_lbl_cmc.setText('OFF')
            if json_inst['data']['error'] == 'on':
                self.log_control_btn_err.setChecked(True)
                self.log_control_lbl_err.setText('ON')
            else:
                self.log_control_btn_err.setChecked(False)
                self.log_control_lbl_err.setText('OFF')
                
            if json_inst['data']['debug'] == 'on':
                self.log_control_btn_dbg.setChecked(True)
                self.log_control_lbl_dbg.setText('ON')
            else:
                self.log_control_btn_dbg.setChecked(False)
                self.log_control_lbl_dbg.setText('OFF')
            if json_inst['data']['work'] == 'on':
                self.log_control_btn_wrk.setChecked(True)
                self.log_control_lbl_wrk.setText('ON')
            else:
                self.log_control_btn_wrk.setChecked(False)
                self.log_control_lbl_wrk.setText('OFF')
                 
    def onReadController(self):
        room_id = self.controller_read_txt_1.text()
        controller_id = self.controller_read_txt_2.text()
        if room_id == '':
            self.controller_read_txt_1.setText('room id can not be null')
            return 0
        if controller_id == '':
            self.controller_read_txt_2.setText('controller id can not be null')
            return 0
        if self.btn_connect.text() == 'Connected':
            self.django_simulator.send(read_controller_state(int(room_id), int(controller_id)))
            dj_reciver = DjangoFrameMain(self.django_simulator)
            json_inst = dj_reciver.main_receivor()
            if json_inst['data']['state'] == ON:
                self.controller_read_txt_3.setText('ON')
            else: 
                self.controller_read_txt_3.setText('OFF')
        else:
            self.controller_read_txt_3.setText('Not connected yet')
                
    def onUpdateController(self):
        room_id = self.controller_update_txt_1.text()
        controller_id = self.controller_update_txt_2.text()
        state = self.controller_update_txt_3.text()
        
        if room_id == '':
            self.controller_update_txt_1.setText('room id can not be null')
            return 0
        if controller_id == '':
            self.controller_update_txt_2.setText('controller id can not be null')
            return 0
        if state != 'ON' and state != 'OFF':
            self.controller_update_txt_3.setText('state should be [ON, OFF]')
            return 0
        if self.btn_connect.text() == 'Connected':
            state = self.django_simulator.send(update_controller_state(int(room_id), int(controller_id),str(state)))
            dj_reciver = DjangoFrameMain(self.django_simulator)
            json_inst = dj_reciver.main_receivor()
            if json_inst['code'] == 0:
                self.controller_update_txt_3.setText('update succeed')
            else:
                self.controller_update_txt_3.setText('update failed')
        else:
            self.controller_update_txt_3.setText('Not connected yet')
    def onUpdateLog(self, pressed):
        sender = self.sender()
        if sender is self.log_control_btn_err:
            if self.log_control_btn_err.isChecked():
                if self.django_simulator == '':
                    self.log_control_lbl_err.setText('OFF \t Sorry not connected to server!')
                    self.log_control_btn_err.setChecked(False)
                    return FAI
                main_frame = update_log_state('error', ON)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_err.setText('ON')
                else:
                    self.log_control_btn_err.setChecked(False)
            else:
                if self.django_simulator == '':
                    self.log_control_lbl_err.setText('ON \t Sorry not connected to server!')
                    self.log_control_btn_err.setChecked(True)
                    return FAI
                main_frame = update_log_state('error', OFF)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_err.setText('OFF') 
                else:
                    self.log_control_btn_err.setChecked(True)
            pass
        elif sender is self.log_control_btn_cmc:
            
            if self.log_control_btn_cmc.isChecked():
                if self.django_simulator == '':
                    self.log_control_lbl_cmc.setText('OFF \t Sorry not connected to server!')
                    self.log_control_btn_cmc.setChecked(False)
                    return FAI
                main_frame = update_log_state('communication', ON)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_cmc.setText('ON')
                else:
                    self.log_control_btn_cmc.setChecked(False)
            else:
                if self.django_simulator == '':
                    self.log_control_lbl_cmc.setText('ON \t Sorry not connected to server!')
                    self.log_control_btn_cmc.setChecked(True)
                    return FAI
                main_frame = update_log_state('communication', OFF)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_cmc.setText('OFF') 
                else:
                    self.log_control_btn_cmc.setChecked(True)
                    
        elif sender is self.log_control_btn_wrk:
            if self.log_control_btn_wrk.isChecked():
                if self.django_simulator == '':
                    self.log_control_lbl_wrk.setText('OFF \t Sorry not connected to server!')
                    self.log_control_btn_wrk.setChecked(False)
                    return FAI
                main_frame = update_log_state('work', ON)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_wrk.setText('ON')
                else:
                    self.log_control_btn_wrk.setChecked(False)
            else:
                if self.django_simulator == '':
                    self.log_control_lbl_wrk.setText('ON \t Sorry not connected to server!')
                    self.log_control_btn_wrk.setChecked(True)
                    return FAI
                main_frame = update_log_state('work', OFF)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_wrk.setText('OFF') 
                else:
                    self.log_control_btn_wrk.setChecked(True)
                    
        elif sender is self.log_control_btn_dbg:
            if self.log_control_btn_dbg.isChecked():
                if self.django_simulator == '':
                    self.log_control_lbl_dbg.setText('OFF \t Sorry not connected to server!')
                    self.log_control_btn_dbg.setChecked(False)
                    return FAI
                main_frame = update_log_state('debug', ON)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_dbg.setText('ON')
                else:
                    self.log_control_btn_dbg.setChecked(False)
            else:
                if self.django_simulator == '':
                    self.log_control_lbl_dbg.setText('ON \t Sorry not connected to server!')
                    self.log_control_btn_dbg.setChecked(True)
                    return FAI
                main_frame = update_log_state('debug', OFF)
                self.django_simulator.send(main_frame)
                json_inst = self.dj_reciver.main_receivor()
                if json_inst['code'] == SUC:
                    self.log_control_lbl_dbg.setText('OFF') 
                else:
                    self.log_control_btn_dbg.setChecked(True)