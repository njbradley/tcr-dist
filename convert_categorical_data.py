from basic import *
from csv_file_helper import *
from sys import argv

if len(argv) != 2:
    print 'usage: convert_categorical_data.py filename_for_sanitization.csv\nremoves all columms that are not numeric so r doesnt crash'

filename = argv[1]
new_file = filename.replace('.csv','_converted.csv')

data,_,colnames = read_csv_file(filename, rownames = False, string = True)

new_data = np.zeros(data.shape,dtype=data.dtype)
for y in range(data.shape[1]):
    print y
    if colnames[y] != 'barcode':
        try:
            float(data[1,y])
        except ValueError:
            colnames[y] += '_to_int'
            col = data[:,y]
            categories = list(set(col.tolist()))
            if categories == ['TRUE','FALSE']:
                categories = ['FALSE','TRUE']
            if(len(categories) > data.shape[0]/2):
                col[:] = 0
                print colnames[y]
            else:
                for i in range(len(categories)):
                    col[col==categories[i]] = i
        else: 
            col = data[:,y]
    else: 
        col = data[:, y]
    new_data[:,y] = col

print new_data.shape


write_csv_file(new_file, new_data, None, colnames)
