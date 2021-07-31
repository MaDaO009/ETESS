# -*- coding: utf-8 -*-
"""
Updated on Tue SEP 16 11:05:38 2018

@author: Zeyuan Feng
"""

import time
import xlsxwriter
import random
from collections import deque
import os


class data_writer:
    def __init__(self,cycle=0.1,N=1,mission='input your mission'):
        self.sensor_time=0
        self.cycle=cycle
        self.N=N
        self.DataPoints = [deque(maxlen=None) for i in range(N)]
        self.mission=mission

    def add_data(self,poses,twists,commands,true_wind,current,voltage):
        poses=[[float('{0:.2f}'.format(i)) for i in pos_and_orientation] for pos_and_orientation in poses]
        twists=[[float('{0:.2f}'.format(i)) for i in v_and_angular_v] for v_and_angular_v in twists]
        commands=[[float('{0:.2f}'.format(i)) for i in command] for command in commands]
        true_wind=str([float('{0:.2f}'.format(i)) for i in true_wind])
        current=float('{0:.2f}'.format(current))
        voltage=float('{0:.2f}'.format(voltage))
        for i in range(self.N):
            self.DataPoints[i].append([self.sensor_time,*poses[i],*twists[i],*commands[i],true_wind,current,voltage])
        self.sensor_time+=self.cycle

    def write_data_points(self):
        print('Start writing data')
        file_name=input('Please input file name')
    
        runDate = time.ctime() 
    
        # workbook = xlsxwriter.Workbook('/data/%s.xlsx'%file_name,{'constant_memory': True})
        workbooks = [xlsxwriter.Workbook('data/%sboat%d.xlsx'%(file_name,i+1),{'constant_memory': True}) for i in range(self.N)]
        for book_number in range(self.N):
            worksheet = workbooks[book_number].add_worksheet() # Generating worksheet
            bold = workbooks[book_number].add_format({'bold':True}) # Formating for Bold text

            worksheet.write('A1', 'Time', bold) # Writing Column Titles
            worksheet.write('B1', 'x', bold)
            worksheet.write('C1', 'y', bold)
            worksheet.write('D1', 'roll', bold)
            worksheet.write('E1', 'yaw', bold)
            worksheet.write('F1', 'v', bold)
            worksheet.write('G1', 'u', bold)
            worksheet.write('H1', 'p', bold)
            worksheet.write('I1', 'w', bold)
            worksheet.write('J1', 'command0', bold)
            worksheet.write('K1', 'command1', bold)
            worksheet.write('L1', 'true wind', bold)
            worksheet.write('M1', 'Current (mA)', bold)
            worksheet.write('N1', 'Voltage (v)', bold)
            worksheet.write('O1', 'mission', bold)
            worksheet.write('O2', self.mission,bold)
            worksheet.write('P1', 'Start Time', bold)
            worksheet.write('P2', runDate)

            row = 1 # Starting Row (0 indexed)
            col = 0 # Starting Column (0 indexed) 
        
            print('Total number of rows: ',len(self.DataPoints[book_number]))

            print('Writing Data into Worksheet')
        
            for values in (self.DataPoints[book_number]):
                # Writing Data in XLSX file
                i=0
                col=0
                for value in values:
                    worksheet.write(row, col+i, value)
                    i+=1
                row+=1
            workbooks[book_number].close() # Closing Workbook 
        time.sleep(1)
        print('Sensor Writing successfull \n')
    
