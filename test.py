import os
import xlrd
filelist=[]
 
for root, dirs, files in os.walk("./data/test", topdown=False):
    for name in files:
        str=os.path.join(root, name)
        
        if str.split('.')[-1]=='xlsx':
            str=str.replace('\\','/')
            filelist.append(str)

workbooks = [xlrd.open_workbook(filelist[i]) for i in range(len(filelist))]