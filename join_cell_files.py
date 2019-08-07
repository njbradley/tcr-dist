from csv_file_helper import *
from basic import *
from sys import argv

try:
    file1, file2, output_filename = argv[1:]
except:
    print 'usage: join_cell_files.py first_file.csv second_file.csv output_file.csv'
    exit(0)

data1, barcodes1, col1 = read_csv_file(file1, string = True)
data2, barcodes2, col2 = read_csv_file(file2, string = True)

print data1.shape, data2.shape

full_data = {}
data = np.empty((min(data1.shape[0], data2.shape[0]),data1.shape[1]+data2.shape[1]), dtype='|S30')

for i in range(len(barcodes1)):
    if barcodes1[i] in full_data:
        full_data[barcodes1[i]].append(data1[i,:])
    else:
        full_data[barcodes1[i]] = [data1[i,:]]

for i in range(len(barcodes2)):
    if barcodes2[i] in full_data:
        for j in range(len(full_data[barcodes2[i]])):
            if full_data[barcodes2[i]][j].shape[0] < data.shape[1]:
                break
        else:
            continue
        full_data[barcodes2[i]][j] = np.concatenate((full_data[barcodes2[i]][j],data2[i,:]))

new_barcodes = []
new_cols = col1+col2[1:]

all_data_list = []

for barcode, line in full_data.items():
    all_data_list.extend(zip([barcode]*len(line), line))

i = 0
for barcode, line in all_data_list:
    if line.shape[0] == data.shape[1]:
        new_barcodes.append(barcode)
        data[i,:] = line
        i += 1

data = data[:i,...]

print data.shape,len(new_barcodes), len(new_cols)
print new_cols

write_csv_file(output_filename, data, new_barcodes, new_cols)
