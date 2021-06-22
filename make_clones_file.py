import csvfile
import sys

def make_clones_file(inpath, outpath):
    ifile = csvfile.InFile(inpath)
    outheaders = ifile.headers[:]
    if not 'clone_size' in outheaders:
        outheaders.insert('clone_size',1)
    outheaders[0] = 'clone_id'
    ofile = csvfile.OutFile(outpath,outheaders)
    id = ifile.headers[0]
    clones = {}
    count = {}
    clones2barc = {}
    line = ifile.readline()
    while line != None:
        index = line[id]
        del line[id]
        if line in clones.values():
            for key in clones:
                if clones[key] == line:
                    break
            count[key] += 1
            clones2barc['clonotype' + str(key)].append(index)
        else:
            clones[index] = line
            count[index] = 1
            clones2barc['clonotype' + str(index)] = [index]
        line = ifile.readline()
    for index, line in clones.items():
        line['clone_size'] = count[index]
        line['clone_id'] = 'clonotype' + str(index)
        ofile.writeline(line)
    ofile.close()
    with open('clonotype2barcodes.json','w') as f:
        f.write(str(clones2barc))
        f.close()

if __name__ == "__main__":
    if len(sys.argv) == 3:
        make_clones_file(sys.argv[1], sys.argv[2])
        csvfile.view(sys.argv[2])
    else:
        print "usage: python make_clones_file.py input_cell_file.csv output_clones_file.csv"
