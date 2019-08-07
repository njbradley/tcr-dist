from basic import *
from csv_file_helper import *
from sys import argv

if len(argv) != 2:
    print 'usage: sanitize_for_r.py filename_for_sanitization.csv\nremoves all columms that are not numeric so r doesnt crash'

filename = argv[1]
new_file = filename.replace('.csv','_sanitized.csv')

data,_,col = read_csv_file(filename, rownames = False, string = True)

new_data = np.zeros(data.shape,dtype=data.dtype)
new_col = []
new_data_index = 0
for y in range(data.shape[1]):
    try:
        float(data[1,y])
    except ValueError:
        continue
    new_col.append(col[y])
    new_data[:,new_data_index] = data[:,y]
    new_data_index += 1

new_data = new_data[:,:new_data_index]
print new_data.shape, len(new_col)


write_csv_file(new_file, new_data, None, new_col)
