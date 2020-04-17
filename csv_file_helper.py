import numpy as np
import os

class CsvFile:
    def __init__(self,filename):
        self.file = filename
        self.indices = [[0]]
        f = file(filename,'r')
        f.seek(0,os.SEEK_END)
        length = f.tell()
        f.seek(0)
        for i in range(length):
            char = f.read(1)
            if char == ',':
                self.indices[-1].append(i)
            if char == '\n':
                self.indices[-1].append(i)
                self.indices.append([i])

    def __getitem__(self,t):
        x,y = t
        f = file(self.file,'r')
        f.seek(self.indices[x][y])
        length = self.indices[x][y] - self.indices[x][y+1]
        return f.read(length)


def read_csv_file(path, rownames = True, colnames = True, string = False):
    txt = open(path).read()
    txt = txt.replace('\r','')
    lines = txt.split('\n')
    for i in range(len(lines)):
        if lines[i] == '':
            lines.pop(i)
    if colnames:
        colnames = lines.pop(0)
        colnames = colnames.split(',')
    if rownames:
        rownames = []
        for i in range(len(lines)):
            rowname = lines[i].split(',')[0]
            lines[i] = lines[i][len(rowname)+1:]
            rownames.append(rowname)
    if not string:
        data = '[[' + '],['.join(lines) + ']]'
        try:
            array = np.array(eval(data))
        except:
            string = True
    if string:
        data = []
        for l in lines:
            data.append(l.split(','))
        array = np.array(data)
    return array,rownames,colnames

def write_csv_file(path, data, rownames = None, colnames = None):
    file = open(path, 'w')
    list = data.tolist()
    lines = []
    for i in range(len(list)):
        lines.append(','.join([str(j) for j in list[i]]))
    if rownames != None:
        assert len(rownames) == data.shape[0]
        for i in range(len(lines)):
            lines[i] = rownames[i]+','+lines[i]
    if colnames != None:
        print colnames, rownames, data.shape
        assert len(colnames) == data.shape[1] + (1 if rownames != None else 0)
        lines.insert(0,','.join(colnames))
    file.write('\n'.join(lines))
    file.close()
