import sys
import struct
import os
import subprocess

delimiters = {'csv':',', 'tsv':'\t'}

class color:
   purple = '\033[95m'
   cyan = '\033[96m'
   darkcyan = '\033[36m'
   blue = '\033[94m'
   green = '\033[92m'
   yellow = '\033[93m'
   red = '\033[91m'
   grey = '\033[90m'
   bold = '\033[1m'
   dim = '\033[2m'
   underline = '\033[4m'
   blink = '\033[5m'
   inverse = '\033[7m'
   end = '\033[0m'

class InFile:
	def __init__(self, path):
		self.path = path
		self.file = open(path)
		self.fcs = path.split('.')[-1] == 'fcs'
		if self.fcs:
			self.fcs_init()
			return
		self.delim = delimiters[path.split('.')[-1]]
		self.headers = self.file.readline()[:-1].split(self.delim)
	
	def fcs_init(self):
		self.file = open(self.path)
		header = self.file.read(58).split()
		self.text_start = int(header[1])
		self.data_start = int(header[3])
		self.data_end = int(header[4])
		text = self.file.read(self.data_start-58)
		print self.text_start, self.data_start, header
		self.delim = text[0]
		params = text[1:].split(self.delim)
		params = dict(zip(params[::2], params[1::2]))
		assert self.data_start == int(params['$BEGINDATA']) # corrupted fcs file, different data start positions
		self.endian = '>' if eval(params['$BYTEORD']) == (4,3,2,1) else '<'
		self.datatype = params['$DATATYPE'].lower()
		assert int(params['$ENDDATA']) == self.data_end # different data end positions, file corrupt
		num_cols = int(params['$PAR'])
		self.params = {}
		self.headers = []
		self.line_bytes = 0
		self.template = self.endian + self.datatype*num_cols
		for i in range(1,num_cols+1):
			self.params[params['$P{}N'.format(i)]] = {
				'bits': params['$P{}B'.format(i)],
				'amplification': params['$P{}E'.format(i)],
				'range': params['$P{}R'.format(i)]
			}
			self.headers.append(params['$P{}N'.format(i)])
			self.line_bytes += int(params['$P{}B'.format(i)])/8
	
	def readline_fcs(self):
		data = self.file.read(self.line_bytes)
		if len(data) < self.line_bytes:
			return None
		nums = struct.unpack(self.template, data)
		return dict(zip(self.headers, nums))
	
	def readline(self):
		if (self.fcs):
			return self.readline_fcs()
		string = self.file.readline()
		if (string == ''):
			return None
		string = string[:-1]
		return dict(list(zip(self.headers, string.split(self.delim))))

class OutFile:
	def __init__(self, path, headers):
		self.path = path
		self.headers = headers
		self.file = open(path, 'w')
		self.fcs = path.split('.')[-1] == 'fcs'
		if self.fcs:
			self.fcs_init()
			return
		self.delim = delimiters[path.split('.')[-1]]
		self.file.write(self.delim.join(self.headers) + '\n')
	
	def fcs_init(self):
		self.params = {
			'$BEGINANALYSIS': 0,
			'$ENDANALYSIS': 0,
			'$BEGINDATA': sys.maxint,
			'$ENDDATA': sys.maxint,
			'$BEGINSTEXT': 0,
			'$ENDSTEXT': 0,
			'$BYTEORD': '4,3,2,1',
			'$DATATYPE': 'F',
			'$MODE': 'L',
			'$NEXTDATA': 0,
			'$PAR': len(self.headers),
			'$TOT': sys.maxint
		}
		for num,head in enumerate(self.headers):
			name = '$P' + str(num+1)
			self.params.update({
				name+'B': 32,
				name+'E': '0,0',
				name+'N': head,
				name+'R': -sys.maxint,
			})
		head = self.make_fcs_header()
		self.alloted = len(head)
		self.file.write(' ' * self.alloted)
		self.params['$TOT'] = 0
		self.template = '>' + 'f'*len(self.headers)
		self.line_bytes = len(self.headers) * 4
		self.params['$BEGINDATA'] = self.alloted
		
		self.string_mappings = []
	
	def make_fcs_header(self):
		pairs = ['|'.join(map(str,i)) for i in self.params.items()]
		txt = '|' + '|'.join(pairs) + '|'
		top = 'FCS3.0          58'
		top += str(len(txt) + 57).rjust(8, ' ')
		top += str(self.params['$BEGINDATA']).rjust(8, ' ')
		top += str(self.params['$ENDDATA']).rjust(8, ' ')
		top += str(self.params['$BEGINANALYSIS']).rjust(8, ' ')
		top += str(self.params['$ENDANALYSIS']).rjust(8, ' ')
		return top + txt
	
	def writeline_fcs(self, line):
		nums = []
		for i,head in enumerate(self.headers):
			if head in line:
				try:
					num = float(line[head])
				except ValueError:
					print line[head], self.string_mappings
					if line[head] in self.string_mappings:
						num = self.string_mappings.index(line[head])
					else:
						num = len(self.string_mappings)
						self.string_mappings.append(line[head])
			else:
				num = 0
			if (num > self.params['$P' + str(i+1) + 'R']):
				self.params['$P' + str(i+1) + 'R'] = num
			nums.append(num)
		print nums
		data = struct.pack(self.template, *nums)
		print [data]
		self.file.write(data)
		self.params['$TOT'] += 1

	def writeline(self, line):
		if self.fcs:
			return self.writeline_fcs(line)
		for head in self.headers:
			if head in line:
				self.file.write(str(line[head]) + self.delim)
			else:
				self.file.write(self.delim)
		self.file.write('\n')
	
	def close(self):
		if self.fcs:
			self.params['$ENDDATA'] = self.params['$BEGINDATA'] + self.line_bytes * self.params['$TOT']
			self.file.seek(0)
			self.file.write(self.make_fcs_header())
		self.file.close()

def view(path, row = None, col = None):
	if row == None:
		row = slice(0,2)
	elif type(row) == str:
		if row.count(':') > 0:
			row = row.split(':')
			if row[0] == '':
				row[0] = 0
			if row[1] == '':
				row[1] = 3
			row = slice(int(row[0]), int(row[1]))
		elif row.count('=') > 0:
			equasion = row.split('=')
			row = lambda line: line[equasion[0]] == equasion[1]
		elif row.isdigit():
			row = slice(int(row)-1, int(row)+1)
	
	ifile = InFile(path)
	lines = []
	headers = ifile.headers
	linenums = []
	
	if type(col) == str:
		if col.count(',') > 0:
			headers = col.split(',')
		elif col.count(':') > 0:
			bounds = col.split(':')
			if bounds[0] == '':
				bounds[0] = headers[0]
			if bounds[1] == '':
				bounds[1] = headers[-1]
			s = slice(headers.index(bounds[0]), headers.index(bounds[1])+1)
			headers = headers[s]
		else:
			headers = [col]
	elif type(col) == slice:
		headers = headers[col]
	
	if type(row) == slice:
		for i in range(row.start):
			ifile.readline()
		for i in range(row.stop-row.start+1):
			line = ifile.readline()
			if line != None:
				vals = []
				for head in headers:
					vals.append(line[head])
				lines.append(vals)
				linenums.append(row.start+i)
	elif type(row) == type(lambda:0):
		line = ifile.readline()
		i = 0
		while line != None:
			if row(line):
				vals = []
				for head in headers:
					vals.append(line[head])
				lines.append(vals)
				linenums.append(i)
			line = ifile.readline()
			i += 1
	
	print color.inverse + path + ": " + ("rows " + str(row.start) + ':' + str(row.stop) if type(row) == slice else '') + color.end
	
	num = len(lines)
	if num == 0:
		print color.red + "Range is empty!" + color.end
		return
	longest = []
	vals = [[lines[j][i] for j in range(num)] for i in range(len(headers))]
	for i in range(len(headers)):
		longest.append(max([len(headers[i]), max(map(len, vals[i]))]))
		headers[i] += ' '*(longest[-1] - len(headers[i]))
		for j in range(num):
			vals[i][j] += ' '*(longest[-1] - len(vals[i][j]))
	index = 0
	linenum_longest = max(map(len,map(str,linenums))) + 2
	term_size = int(subprocess.check_output(['stty','size'], stderr=subprocess.PIPE).split()[1])
	need_to_print_cols = [True]*len(headers)
	while any(need_to_print_cols):
		most_on_screen = 0
		while index+most_on_screen <= len(headers) and sum(longest[index:index+most_on_screen]) + most_on_screen < term_size-linenum_longest - (4 if not all(need_to_print_cols) else 0):
			most_on_screen += 1
		if most_on_screen > 0:
			most_on_screen -= 1
		print ' '*(linenum_longest + (5 if not all(need_to_print_cols) else 0)),
		print color.green + (color.end+'|'+color.green).join(headers[index:index+most_on_screen]) + color.end
		for i in range(num):
			print color.grey + str(linenums[i]) + ":" + ' '*(linenum_longest - 1 - len(str(linenums[i]))) + color.end,
			if not all(need_to_print_cols):
				if i == 0:
					print "... ",
				else:
					print "    ",
			print '|'.join([j[i] for j in vals[index:index+most_on_screen]])
		for i in range(index,index+most_on_screen):
			need_to_print_cols[i] = False
		index += most_on_screen
		if any(need_to_print_cols):
			print ' '#*(term_size/2-2) + '...'
	print ''

def select_cols(inpath, outpath, cols):
	ifile = InFile(inpath)
	inheaders = ifile.headers
	newcols = []
	for i in range(len(cols)):
		if cols[i].count(':') > 0:
			bounds = cols[i].split(':')
			s = slice(inheaders.index(bounds[0]), inheaders.index(bounds[1])+1)
			newcols.extend(inheaders[s])
		else:
			newcols.append(cols[i])
	cols = newcols
	ofile = OutFile(outpath, cols)
	line = ifile.readline()
	while line != None:
		ofile.writeline(line)
		line = ifile.readline()
	ofile.close()

def join_row_id(paths, out_path):
	infiles = []
	outheaders = []
	indexes = {}
	for path in paths:
		infiles.append(InFile(path))
		outheaders.extend(infiles[-1].headers[1:])
		indexes[path] = infiles[-1].headers[0]
	all_lines = {}
	done = False
	while not done:
		outline = {}
		done = True
		for file in infiles:
			line = file.readline()
			if (line == None):
				continue
			done = False
			cell_index = line[indexes[file.path]]
			del line[indexes[file.path]]
			#print [cell_index], all_lines
			if cell_index in all_lines:
				all_lines[cell_index].update(line)
			else:
				all_lines[cell_index] = line
	outfile = OutFile(out_path, [indexes[infiles[0].path]] + outheaders)
	for cell_index,line in all_lines.items():
		line[indexes[infiles[0].path]] = cell_index
		outfile.writeline(line)
	outfile.close()

def clones_to_cells(in_path, out_path, jsonfile = 'clonotype2barcodes.json'):
    ifile = InFile(in_path)
    inheaders = ifile.headers
    cloneid_header = inheaders[0]
    ofile = OutFile(out_path, ['barcode'] + inheaders)
    json = eval(open(jsonfile).read())
    line = ifile.readline()
    while line != None:
        for barc in json[line[cloneid_header]]:
            outline = line
            outline['barcode'] = barc
            ofile.writeline(outline)
        line = ifile.readline()
    ofile.close()

def join_coll(paths, out_path):
	first = InFile(paths[0])
	outfile = OutFile(out_path, first.headers)
	for path in paths:
		infile = InFile(path)
		line = infile.readline()
		while (line != None):
			outfile.writeline(line)
			line = infile.readline()
	outfile.close()

def convert(inpath, outpath):
	infile = InFile(inpath)
	outfile = OutFile(outpath, infile.headers)
	line = infile.readline()
	while (line != None):
		outfile.writeline(line)
		line = infile.readline()
	outfile.close()

def convert_string(inpath, outpath):
    ifile = InFile(inpath)
    headers = ifile.headers
    ofile = OutFile(outpath, headers)
    number_replacements = {head:{} for head in headers}
    line = ifile.readline()
    while line != None:
        for head in line:
            if line[head] in number_replacements[head]:
                line[head] = number_replacements[head][line[head]]
            else:
                try:
                    line[head] = float(line[head])
                except ValueError:
                    number_replacements[head][line[head]] = len(number_replacements[head])
                    line[head] = number_replacements[head][line[head]]
        ofile.writeline(line)
        line = ifile.readline()
    ofile.close()
                

if __name__ == "__main__":
	try:
		mode = sys.argv[1]
		if mode == 'view':
			file = sys.argv[2]
			row = None
			col = None
			i = 3
			while i < len(sys.argv):
				if sys.argv[i] == '--row':
					i += 1
					row = sys.argv[i]
				elif sys.argv[i] == '--col':
					i += 1
					col = sys.argv[i]
				i += 1
			if row == None and len(sys.argv) > 3 and sys.argv[3] != '--col':
				row = sys.argv[3]
			if col == None and len(sys.argv) > 4 and sys.argv[3] != '--row':
				col = sys.argv[4]
			view(file, row, col)
		if mode == 'join-row':
			join_row_id(sys.argv[2:-1], sys.argv[-1])
			view(sys.argv[-1])
		if mode == 'join-col':
			join_coll(sys.argv[2:-1], sys.argv[-1])
			view(sys.argv[-1])
		if mode == 'convert':
			convert(sys.argv[2], sys.argv[3])
		if mode == 'select':
			select_cols(sys.argv[2], sys.argv[3], sys.argv[4:])
			view(sys.argv[3])
		if mode == 'clones-to-cells':
			clones_to_cells(sys.argv[2], sys.argv[3])
			view(sys.argv[3])
		if mode == 'convert-string':
			convert_string(sys.argv[2], sys.argv[3])
			view(sys.argv[3])
	except IndexError:
		print """usage: csv.py <mode> <input files> ... <output file> <optional args>
mode is one of:
	join-row: joins two or more files by cell index, matching them together by the first collumn
	join-col: joins two files by collum, simple, just appends one file on the bottom of the other
	convert: takes in one file, and converts the data to the output file, useful for converting between filetypes
	select: takes in one input file, one output file, and a list of collumn names. the output file only contains the collumns in the list. ie:
		csvfile.py select input_file.fcs output_file.tsv cell_id clone_size va_gene
		output file will have the collums cell_id clone_size va_gene
	view: display one file. optional args can be given to display specific points in the file. ie:
		csvfile.py view input_file.tsv --row 5 --col barcode,id
		csvfile.py view input_file.tsv --row id=523  (the row can be specified by a specific collum, and all spots that match will be shown)
		csvfile.py view input_file.tsv --row 3:9 --col barcode:counts    (a slice can be taken, which will display all collums/rows between)
		csvfile.py view input_file.tsv 5:10 barcode  (without labels, it is assumed the first arg refers to rows and the second refers to cols)
input files and output file are either .csv .fcs or .tsv files"""
