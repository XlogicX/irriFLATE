# irriFLATE: Impractically Redundant Redundant Interactive DEFLATE crafting tool

import re	# There's no way I'm writing a script without being able to use RegEx
import argparse

class gziplen:
	def __init__(self):
		self.data = 0
	def grow(self,ammount):
		self.data += ammount
	def getint(self):
		return(self.data)
	def gethex(self):
		return('{:08x}'.format(int(self.data)))
	def gethexr(self):
		hexval = '{:08x}'.format(int(self.data))
		return(hexval[6:8] + hexval[4:6] + hexval[2:4] + hexval[0:2])		

class databuffer:
	'Full buffer of data that will eventually be processed and printed out'

	def __init__(self):
		self.data = []	

	def print(self,data,end):

		binary = []
		for i in data:
			binary = flatten(binary,i)
		self.data = binary

		# Needs 2-d array of fields (to reverse bits of)
		revfields = []
		bits = []
		# Reverses bits in each field
		for field in self.data:
			for bit in field[::-1]:
				revfields.append(bit)
		# Padded zeros if needed
		if len(revfields) % 8 != 0:
			[revfields.append(0) for i in range(0,9-(len(revfields)%8))]
		# Build out the bits
		for i in range(0,int(len(revfields)/8)):
			for j in range(0,8):
				bits.append(revfields[(i*8)+(7-j)])
		# Now convert individual bits to presentable ASCIIHex
		hexstring = ''
		for i in range(0,int(len(bits)/8)):
			ordval = 0
			for j in range(0,8):
				ordval += bits[(i*8)+j] << (7-j)
			hexstring += '{:02x}'.format(ordval)
		if args.colors: print('\033[0;37m',end='')
		if end:
			print(hexstring)
		else:
			print(hexstring,end='')

class nonprefix:
	'Structure for non-prefix codes, supposed to be huffman, but flexible...'
	'alphabet: all symbols for table'
	'bitlengths: amount of bits for each symbol in same order as alphabet'
	'table: the generated non-prefix code table, built be construct()'

	def __init__(self,alphabet,bitlengths):
		self.alphabet = alphabet
		self.bitlengths = bitlengths

	def construct(self):
		# Construction based on algorithm from RFC 1951
		self.table = {}
		# Step 1: Count the number of codes for each code length.  Let bl_count[N] be the number of codes of length N, N >= 1.

		# Initiliaze bl_count array with highest bitcount found in bitlengths
		MAX_BITS = max(self.bitlengths)
		bl_count = [0 for i in range(MAX_BITS+1)]
		for i in self.bitlengths:	# for each of the bit lengths
			bl_count[i] += 1	# 	tally them up

		# Find if it is oversubscribed (This might never be reached; there are other checks and balances)
		left = 1
		for i in range(1,MAX_BITS+1):
			left <<= 1
			left -= bl_count[i]
			if (left < 0):
				return left

		# Step 2: Find the numerical value of the smallest code for each
		code = 0
		bl_count[0] = 0
		next_code = [0 for i in range(MAX_BITS+1)]
		for i in range(1,MAX_BITS+1):
			code = (code + bl_count[i-1]) << 1
			next_code[i] = code

		# Step 3: Assign numerical values to all codes, using consecutive values for all codes of the same length with the base
		# 	values determined at step 2. Codes that are never used (which have a bit length of zero) must not be assigned a value.
		tree = [0 for i in range(len(self.alphabet))]
		for n in range(len(self.alphabet)):
			length = self.bitlengths[n]
			if length != 0:
				tree[n] = next_code[length]
				next_code[length] += 1

		for idx,i in enumerate(tree):
			code = '{num:0{width}b}'.format(num=i,width=self.bitlengths[idx])
			self.table[self.alphabet[idx]] = code

# Flatten to 2d
def getbinarray(bits):
	array = []
	for bit in bits:
		array.append(int(bit))
	return array

def flatten(arr,fields):
	for i in fields:
		arr.append(i)
	return arr

def int_to_binarray(number,w):
	bitarray = []
	binary = '{num:0{width}b}'.format(num=number, width=w)
	for bit in binary:
		bitarray.append(int(bit))
	return(bitarray)

def symbolize(table,symbol,disthuff):
	lengthdist = []
	length_bases = [3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258]
	extra_length = [0,0,0,0,0,0,0,0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4,  5,  5,  5,  5,  0]
	distance_bases = [1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,  32768];
	extra_distance = [0,0,0,0,1,1,2,2, 3, 3, 4, 4, 5, 5, 6,  6,  7,  7,  8,  8,  9,   9,   10,  10,  11,  11,  12,  12,   13,   13]

	# Process if it's a string of length,distance pair (i.e 90,11)...or the command to list tables
	if isinstance(symbol, str):
		if symbol == 'tables':
			print("\nLiteral/Length Table\nOrd\tChr\\Len\tBits")
			for key,value in table.items():			# Iterate through table
				meaning = ''						# Either a char, EOB, or a (calculated) length range
				if int(key) < 256:					# If it's a char
					meaning = chr(int(key))			# 	Attempt to print as one
				elif int(key) > 256:				# If it's a Length
					distcode = int(key)-257			# 	Zero the index back down
					if int(distcode) < 8 or int(distcode) == 28:	#	If it's lower than 8, than no range
						meaning = str(length_bases[int(distcode)])
					else:							#	Otherwise it's a range
						meaning = str(length_bases[int(distcode)]) + '-' + str(length_bases[int(distcode)+1]-1)
				else:
					meaning = 'EOB'
				print("{}\t{}\t{}".format(key,meaning,value))			# Print each entry
			print("\nDistance Table\nIndex\tRange\tBits")
			for key,value in disthuff.items():			# Iterate through table
				meaining = ''
				if int(key) < 4:				#	If it's lower than 4, than no range
					meaning = str(distance_bases[int(key)])
				else:							#	Otherwise it's a range
					meaning = str(distance_bases[int(key)]) + '-' + str(distance_bases[int(key)+1]-1)
				print("{}\t{}\t{}".format(key,meaning,value))			# Print each entry
			return ([])

		matches = re.match(r'(\d+),(\d+)',symbol)
		length = matches.group(1)
		distance = matches.group(2)
		# From Length, get index into length bases then calculate what extra length needs to be
		for idx,i in enumerate(length_bases):
			if int(length) < i:
				break
		if disthuff == 0:	# Fixed mode
			if idx < 24:
				lengthdist.append(int_to_binarray(idx,7)[::-1]) # This is the Length
			else:
				lengthdist.append(int_to_binarray(idx+168,8)[::-1]) # This is the Length				
		else:				# Dynamic mode
			symbol = 256+idx
			try:
				lengthdist.append(getbinarray(table[str(symbol)])[::-1])
			except:			# Not in Table
				print("Invalid Entry")
				return ([])
		# Do we need extra bits?
		if int(length) > 10:
			extra_needed = extra_length[idx-1]		# Get amount of bits needed
			diff = int(length)-length_bases[idx-1]	# Get diff (length - base)
			lengthdist.append(int_to_binarray(diff,extra_needed))	# Append Extra bits

		# From Distance, get index into distance bases then calculate what extra distance needs to be
		for idx,i in enumerate(distance_bases):
			if int(distance) < i:
				break
		# idx: index into distance bases, i: value of that index
		if disthuff == 0:	# Fixed mode
			lengthdist.append(int_to_binarray(idx-1,5)[::-1]) # This is the Length
		else:				# Dynamic mode
			bitarray = []
			for bit in disthuff[str(idx-1)]:
				bitarray.append(int(bit))
			lengthdist.append(bitarray[::-1])
		# Do we need extra bits?
		if int(distance) > 4:
			extra_needed = extra_distance[idx-1]		# Get amount of bits needed
			diff = int(distance)-distance_bases[idx-1]	# Get diff (length - base)
			lengthdist.append(int_to_binarray(diff,extra_needed))	# Append Extra bits
		return(lengthdist)


	# Process if it's an integer symbol (More Guided)
	elif (symbol < 257):
		# Return the Literal
		try:
			return getbinarray(table[str(symbol)])[::-1]
		except:		# Not in table
			print("Invalid Entry")
			return ([])
	else:
		# Length Base
		length = getbinarray(table[str(symbol)])
		lengthdist.append(length[::-1])
		# If extra bits are needed
		if (symbol > 263):
			extra_needed = extra_length[symbol-257]				# Ask for those extra bits
			extralength = getbinarray(getextra(extra_needed))	# Append the Extra bits	
			lengthdist.append(extralength)		

		# Distance
		if disthuff == 0:	# Fixed mode
			distbits,dist = getdist(0)								# Get 5 bit (0-29) Distance code
			lengthdist.append(getbinarray(distbits)[::-1])
			if dist > 4:
				extra_needed = extra_distance[dist]
				extradist = getbinarray(getextra(extra_needed))	# Append the Extra bits	
				lengthdist.append(extradist[::-1])
			return(lengthdist)
		else:				# Dynamic mode
			distbase,distbits = getdist(disthuff)						# Get variable bit distance code
			lengthdist.append(getbinarray(distbits)[::-1])		# Append the first part of the dist bits	

			# Do we need extra bits?
			distbase = int(distbase)
			if distbase > 4:
				extra_needed = extra_distance[distbase]					# Get amount of bits needed

				# Get the bits
				extradst = getbinarray(getextra(extra_needed))
				lengthdist.append(extradst)
			return(lengthdist)

#---------------------------#
# Routines for Getting Data #
#---------------------------#
def getlit(i):
	bitarray = []
	lit = ''
	while not re.match(r'^(0x[a-f0-9]{2}|0b[01]{8}|.)$', lit, re.I):
		lit = input("Enter Literal #{} (Acceptable Format examples: X, 0x58, 0b01011000): ".format(i+1))
	if lit.startswith('0x'):
		lit = chr(int(lit[2:4],16))
	elif lit.startswith('0b'):
		lit = chr(int(lit[2:10],2))
	lit = '{num:0{width}b}'.format(num=ord(lit), width=8)
	# Make it an array of 8-bits
	for bit in lit:
		bitarray.append(int(bit))
	return bitarray

def getsymbol(table):
	# Get token in many formats, but return ordinal/int value that represents it.
	# A full l,d pair will be an exception
	while True:
		token = input("Token: ")
		# Check to see if it's a literal character
		if re.match(r'^.$', token, re.I):
			glen.grow(1)
			return(ord(token))
		# Check to see if it's a literal encoded as hex
		if re.match(r'^0x[0-9a-f]{2}$', token, re.I):
			glen.grow(1)
			return(int(token[2:4],16))	

		if table == 0:
			# Check to see if it's 7-bit binary: 256 - 279 0000000 - 0010111
			if re.match(r'^0b[01]{7}$', token, re.I):
				value = int(token[2:9],2)
				if (value >= 0 and value < 24):
					glen.grow(1)
					return(value+256)
			# Check to see if it's 8-bit binary: 0 - 143 00110000 - 10111111 (48-191) and 280 - 287 11000000 - 11000111 (192-199)                                      
			if re.match(r'^0b[01]{8}$', token, re.I):
				value = int(token[2:10],2)
				if (value > 47 and value < 192):
					glen.grow(1)
					return(value-48)	
				if (value > 191 and value < 200):
					glen.grow(1)
					return(value+88)
			# Check to see if it's 9-bit binary: 144 - 255 110010000 - 111111111
			if re.match(r'^0b[01]{9}$', token, re.I):
				value = int(token[2:11],2)
				if (value > 399 and value < 512):
					glen.grow(1)
					return(value-256)
		else:
			if re.match(r'^0b[01]+$', token, re.I):
				token = token[2:]
				if token in table.values():
					glen.grow(1)
					return(int(list(table.keys())[list(table.values()).index(token)]))
				else:
					print("Binary Value not in table")

		# Check to see if length,dist pair (will need proper handling)
		if re.match(r'^\d+,\d+$', token, re.I):
			matches = re.match(r'^(\d+),(\d+)$', token, re.I)
			l = int(matches.group(1))
			d = int(matches.group(2))
			glen.grow(l)
			if ((l > 2 and l < 259) and (d > 0 and d < 32769)):
				return(token)

		if token == 'EOB':
			return(256)

		if token == 'tables':
			return(token)

def getextra(bitlength):
	example = '1010101010101'
	bits = ''
	while not (re.match(r'^0b[01]+$', bits, re.I) and len(bits) == (bitlength+2)):
		bits = input("Enter {} Extra Bits (Acceptable Format Example: 0b{}): ".format(bitlength, example[0:bitlength]))
	return(bits[2:bitlength+2])

def getdist(disthuff):
	bits = ''
	while True:
		if disthuff == 0:
			bits = input("Enter 5 Distance Bits (Acceptable Format Example: 0b00000-0b11101): ")
			if re.match(r'^0b[01]{5}$', bits, re.I):
				value = int(bits[2:7],2)
				if (value >= 0 and value < 29):
					return(bits[2:7],value)
		else:
			bits = input("Enter Distance Bits (prefix with 0b): ")
			if re.match(r'^0b[01]+$', bits, re.I):
				value = bits[2:]
				if value in disthuff.values():
					return(int(list(disthuff.keys())[list(disthuff.values()).index(value)]),value)
				else:
					print("Binary Value not in table")

def getcode(i):
	bitarray = []
	number = ''
	while not re.match(r'^0b[01]{3}|[0-7]|l$', number, re.I):
		number = input("Enter 3-bit Code for Symbol #{} (Acceptable input examples: 6, 0b110): ".format(i))
	if number.startswith('0b'):
		number = int(number[2:5],2)
	lit = '{num:0{width}b}'.format(num=int(number), width=3)
	# Make it an array
	for bit in lit:
		bitarray.append(int(bit))
	return bitarray,int(number)

def getdatacode(codehuff,bitlengths,symbol,total,exceeded,valid_lengths):

	length_bases = [3,4,5,6,7,8,9,10,11,13,15,17,19,23,27,31,35,43,51,59,67,83,99,115,131,163,195,227,258]
	extra_length = [0,0,0,0,0,0,0,0, 1, 1, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 4, 4, 4, 4,  5,  5,  5,  5,  0]
	distance_bases = [1,2,3,4,5,7,9,13,17,25,33,49,65,97,129,193,257,385,513,769,1025,1537,2049,3073,4097,6145,8193,12289,16385,24577,  32768];
	extra_distance = [0,0,0,0,1,1,2,2, 3, 3, 4, 4, 5, 5, 6,  6,  7,  7,  8,  8,  9,   9,   10,  10,  11,  11,  12,  12,   13,   13]
	symbol_meaning = ''

	if not exceeded:
		if symbol < 32:
			symbol_meaning = '0x{:02X}'.format(symbol)
		elif symbol < 128:
			symbol_meaning = chr(symbol)
		elif symbol < 256:
			symbol_meaning = '0x{:02X}'.format(symbol)
		elif symbol == 256:
			symbol_meaning = 'stop'
		else:
			distcode = symbol-257			# 	Zero the index back down
			if int(distcode) < 8 or int(distcode) == 28:	#	If it's lower than 8, than no range
				symbol_meaning = "Length: " + str(length_bases[int(distcode)])
			else:							#	Otherwise it's a range
				symbol_meaning = "Lengths: " + str(length_bases[int(distcode)]) + '-' + str(length_bases[int(distcode)+1]-1)
	else:
		if symbol < 4:					#	If it's lower than 4, than no range
			symbol_meaning = "Distance: " + str(distance_bases[symbol])
		else:							#	Otherwise it's a range
			symbol_meaning = "Distances: " + str(distance_bases[symbol]) + '-' + str(distance_bases[symbol+1]-1)

	# Re-org Huffman table
	print("\nValid Codes in Table")
	valid_ints = []								# List of valid choices for integers from table
	valid_bins = []								# List of valid choices for binary from table
	symbols_left = total - symbol
	for key,value in codehuff.items():			# Iterate through table
		# Make sure we have enough symbols left for the repetition/zero codes
		if not (key == '18' and symbols_left < 11) and not ((key == '17' or key == '16') and symbols_left < 3): # and int(key) in valid_lengths:
			print("{}\t{}".format(key,value))			# Print each entry
			valid_ints.append(key)						# Also note as valid integer
			valid_bins.append("0b" + value)				# and binary

	# We need user input here, integer or binary input is acceptable
	# From valid user input, we will have both an integer and binary code representation
	int_code,bin_code = '',''
	while True:
		val = input("Enter value for symbol {} ({}) from Codes Table (prefix binary with 0b): ".format(symbol,symbol_meaning))
		if val == 'repeat' or val == 'rep':
			val = '16'
		if val == 'somezeros':
			val = '17'
		if val == 'manyzeros':
			val = '18'
		if val in valid_ints:			# If input is valid integer
			int_code = int(val)				# its the int code
			bin_code = codehuff[val]		# which is the key into table for bit pattern
			break
		if val in valid_bins:			# If input is bit pattern
			bin_code = val[2:]			# Trim the '0b' prefix and it's the bin code
			int_code = int([i for i in codehuff if codehuff[i]==bin_code][0])	# also get int value from that as key
			break

	bitarray = []
	extrabits = []

	# if int_code is 0-15, that value is literally the bit length
	if int_code < 16:
		bitlengths.append(int_code)
		for bit in bin_code:
			bitarray.append(int(bit))
		bitarray = bitarray[::-1]
		return(bitarray,int_code,bitlengths,1)

	# if int_code is 16: Copy the previous code length 3 - 6 times (need 2 more bits)
	if int_code == 16:
		# Get the previous Code
		try:
			bitlength = bitlengths[-1]
		except:
			bitlength = 0 	# There are no previous codes, just default to 0 bitlength

		left = total-symbol
		if left > 6:
			left = 6

		val = -1
		bits = ''

		# While we don't have the right format or range
		while not (re.match(r'^(0b[01]{2}|\d+)$', str(val), re.I) and val > -1 and val < 4):
			val = input("How many of the next symbols will be 0 (3-{}) (if binary input it's 2-bit prefixed with 0b): ".format(left))
			if val.startswith('0b'):
				bits = val[2:]
				val = int(bits,2)
			else:
				val = int(val) - 3
				bits = '{num:0{width}b}'.format(num=val, width=2)

		for i in range(val+3):
			bitlengths.append(bitlength)

		for bit in bin_code:
			bitarray.append(int(bit))
		for bit in bits:
			extrabits.append(int(bit))
		bitarray = extrabits + bitarray[::-1]

		return(bitarray,int_code,bitlengths,val+3)

	# if int_code is 17: Repeat a code length of 0 for 3 - 10 times (need 3 more bits)
	if int_code == 17:
		left = total-symbol
		if left > 10:
			left = 10

		val = -1
		bits = ''

		# While we don't have the right format or range
		while not (re.match(r'^(0b[01]{3}|\d+)$', str(val), re.I) and val > -1 and val < 8):
			val = input("How many of the next symbols will be 0 (3-{}) (if binary input it's 3-bit prefixed with 0b): ".format(left))
			if val.startswith('0b'):
				bits = val[2:]
				val = int(bits,2)
			else:
				val = int(val) - 3
				bits = '{num:0{width}b}'.format(num=val, width=3)

		for i in range(val+3):
			bitlengths.append(0)

		for bit in bin_code:
			bitarray.append(int(bit))
		for bit in bits:
			extrabits.append(int(bit))
		bitarray = extrabits + bitarray[::-1]

		return(bitarray,int_code,bitlengths,val+3)

	# if int_code is 18: Repeat a code length of 0 for 11 - 138 times (need 7 more bits)
	if int_code == 18:
		left = total-symbol
		if left > 138:
			left = 138

		val = -1
		bits = ''

		# While we don't have the right format or range
		while not (re.match(r'^(0b[01]{7}|\d+)$', str(val), re.I) and val > -1 and val < 128):
			val = input("How many of the next symbols will be 0 (11-{}) (if binary input it's 7-bit prefixed with 0b): ".format(left))
			if val.startswith('0b'):
				bits = val[2:]
				val = int(bits,2)
			else:
				val = int(val) - 11
				bits = '{num:0{width}b}'.format(num=val, width=7)

		for i in range(val+11):
			bitlengths.append(0)

		for bit in bin_code:
			bitarray.append(int(bit))
		for bit in bits:
			extrabits.append(int(bit))
		bitarray = extrabits + bitarray[::-1]

		return(bitarray,int_code,bitlengths,val+11)

	quit()

#-----------------------------#
# Routines for Getting Fields #
#-----------------------------#
def getlast():
	last = '2'
	while (last != '0' and last != '1'):
		last = input("First/Last Block (0-1): ")
	return [[int(last)]]

def gettype():
	ftype = ''
	while not re.match(r'^([0-3]|0b[01]{2})$', ftype, re.I):
		ftype = input("Compression type (0-3 or 0b00-0b11): ")
	if ftype.startswith('0b'):
		ftype = int(ftype[2:4],2)
	return([int_to_binarray(int(ftype),2)])

def getlengths():
	lbytes = -1
	while (lbytes < 0 or lbytes > 65535):
		lbytes = int(input("Total Bytes in Block (0-65535): "))
	length = int_to_binarray(lbytes,16)
	nlength = []
	[nlength.append(1-i) for i in length]
	return([length],[nlength],lbytes)

def getcounts(data):
	if args.colors: print('\033[0;31m',end='')	# Red
	subdata = list(data)
	hlit = '0'
	while not (re.match(r'^(\d{1,3}|0b[01]{5})$', hlit, re.I) and int(hlit) > 256 and int(hlit) < 287):
		hlit = input("# of Literal/Length codes (257-286 or 0b00000-0b11101): ")
		if re.match(r'^0b[01]{5}$', hlit, re.I):
			hlit = str(int(hlit[2:7],2)+257)
	lit = int(hlit)
	hlit = int_to_binarray(int(hlit)-257,5)
	subdata.append([hlit])
	blocks.print(subdata,True)

	if args.colors: print('\033[0;31m',end='')	# Red
	subdata = list(data)
	hdist = '0'
	while not (re.match(r'^(\d{1,2}|0b[01]{5})$', hdist, re.I) and int(hdist) > 0 and int(hdist) < 31):
		hdist = input("# of Distance codes (1-30 or 0b00000-0b11110): ")
		if re.match(r'^0b[01]{5}$', hdist, re.I):
			hdist = str(int(hdist[2:7],2)+1)
	dist = int(hdist)
	hdist = int_to_binarray(int(hdist)-1,5)
	subdata.append([hlit,hdist])
	blocks.print(subdata,True)

	if args.colors: print('\033[0;31m',end='')	# Red
	hclen = '0'
	while not (re.match(r'^(\d{1,2}|0b[01]{4})$', hclen, re.I) and int(hclen) > 3 and int(hclen) < 20):
		hclen = input("# of Code Length codes (4-19 or 0b0000-1111): ")
		if re.match(r'^0b[01]{4}$', hclen, re.I):
			hclen = str(int(hclen[2:7],2)+4)
	clen = int(hclen)
	hclen = int_to_binarray(int(hclen)-4,4)

	return([hlit,hdist,hclen],lit,dist,clen,data)
	
def getcodealphabet(entries,data):
	alphabet = []
	bitlengths = []
	codes = [16,17,18,0,8,7,9,6,10,5,11,4,12,3,13,2,14,1,15]
	order = [3,17,15,13,11,9,7,5,4,6,8,10,12,14,16,18,0,1,2]
	bincodes = []
	left = (2 ** 8)

	# Get values for table, showing valid available options left, while not accepting invalid ones
	for i in range(0,entries):
		if args.colors: print('\033[0;32m',end='')	# Green	
		subdata = list(data)

		valid_lengths = {}
		number = -1
		for k in range(1,8):
			if int(left / (256 >> k)) > 0:
				valid_lengths[k] = int(left / (256 >> k))
		print("Length\tLeft\tPoints")
		for key,value in valid_lengths.items():
			print("{}\t{}\t{}".format(key,valid_lengths[key],1<<(8-key)))
		print("INF\t0\t0")
		print("Points Left:\t{}".format(left))
		print("Codes Left:\t{}".format(entries-i))
		valid_lengths[0] = 'a lot'
		if args.errors:
			bits, number = getcode(codes[i])
		else:
			while number not in valid_lengths:
				bits, number = getcode(codes[i])
		bincodes.append(bits)
		alphabet.append(str(codes[i]))
		bitlengths.append(number)
		if number != 0:
			left -= 256 >> number

		subdata.append(bincodes)
		blocks.print(subdata,True)

	if left > 0 and not args.errors:
		print("You didn't use ALL of the points, this would make the table 'incomplete.' You had {} points left".format(left))
		quit()

	alternatealpha = []
	alternatebits = []
	for i in range(19):
		if order[i] < entries:
			if bitlengths[order[i]] != 0:
				alternatealpha.append(str(codes[order[i]]))
				alternatebits.append(bitlengths[order[i]])
	codehuff = nonprefix(alternatealpha,alternatebits)
	codehuff.construct()
	return (codehuff.table, bincodes, data)

def resetleftcheck(number,inc,last,left,codes_left,current_code,exceeded,dist,bitlengths,subtract):
	if codes_left == 1 and exceeded == False:
		if subtract:
			left -= 65536 >> bitlengths[-1]	# Just for incompleteness checking (as it gets thrown away below)
		if left > 0 and not args.errors:
			print("You didn't use ALL of the points, this would make the table 'incomplete.' You had {} points left".format(left))
			quit()
		exceeded = True
		last = dist
		left = (2**16)
		codes_left = dist
		current_code = 0
	else:
		if subtract:
			left -= 65536 >> bitlengths[-1]	
		if number == 16:
			codes_left -= 1
			current_code += 1
		else:
			codes_left -= inc
			current_code += inc

	return(exceeded,last,left,codes_left,current_code)

def getdatalengths(lit,dist,codehuff,data):
	alphabet = []
	distalpha = []
	total = lit+dist
	[alphabet.append(str(i)) for i in range(0,lit)]		# create alphabet names literals
	[distalpha.append(str(i)) for i in range(0,dist)]	# and distances
	bitlengths = []
	bincodes = []
	left = (2 ** 16)
	i = 0
	last = lit
	codes_left = lit
	current_code = 0
	exceeded = False
	while i < total:
		if args.colors: print('\033[0;33m',end='')	# Yellow
		subdata = list(data)
		# Shows valid options, Kicks out of program if oversubscribed
		valid_lengths = {}
		number = -1
		for k in range(1, 16):
			if (int(left / (65536 >> k)) > 0) and (str(k) in codehuff):
				valid_lengths[k] = int(left / (65536 >> k))
		print("Length\tLeft\tPoints")
		for key, value in valid_lengths.items():
			print("{}\t{}\t{}".format(key,valid_lengths[key],1<<(16-key)))
		print("0\tINF\t0")
		print("Points Left:\t{}".format(left))
		print("Codes Left:\t{}".format(codes_left))
		valid_lengths[0] = 'a lot'
		bits, number, bitlengths, inc = getdatacode(codehuff, bitlengths, current_code, last, exceeded, valid_lengths)
		bincodes.append(bits)

		# Handle multiples (16/17/18)
		if number == 16:
			for j in range(inc):
				exceeded,last,left,codes_left,current_code = resetleftcheck(number,inc,last,left,codes_left,current_code,exceeded,dist,bitlengths,True)
		elif number not in [0,17,18]:
			exceeded,last,left,codes_left,current_code = resetleftcheck(number,inc,last,left,codes_left,current_code,exceeded,dist,bitlengths,True)
		else:
			exceeded,last,left,codes_left,current_code = resetleftcheck(number,inc,last,left,codes_left,current_code,exceeded,dist,bitlengths,False)
		i += inc

		if left < 0 and not args.errors:
			print("You exceeded your points (oversubscribed), keep an eye on 'Points Left' next time")
			quit()

		subdata.append(bincodes)
		blocks.print(subdata,True)

	# lit+1 means the first dist code, it is okay to be incomplete for this one. You should pick bitlen of 1,
	# 	but picking a larger length gets accepted as well
	if left > 0 and (i != lit+1) and not args.errors:
		print("You didn't use ALL of the points, this would make the table 'incomplete.' You had {} points left".format(left))
		quit()


	# Build Tables and don't include entries with 0-length bitlengths
	litlens = bitlengths[:lit]
	distlens = bitlengths[lit:]
	litlens_reduced = []
	distlens_reduced = []
	l_alph_redu = []
	d_alph_redu = []

	for idx,i in enumerate(litlens):
		if i != 0:
			litlens_reduced.append(i)
			l_alph_redu.append(alphabet[idx])
	for idx,i in enumerate(distlens):
		if i != 0:
			distlens_reduced.append(i)
			d_alph_redu.append(distalpha[idx])
	lithuff = nonprefix(l_alph_redu,litlens_reduced)
	disthuff = nonprefix(d_alph_redu,distlens_reduced)
	lithuff.construct()
	disthuff.construct()
	return(lithuff.table,disthuff.table,bincodes,data)

#-----------------------------#
#     Gzip MetaData Entry     #
#-----------------------------#

def gettime():
	bitarray1,bitarray2,bitarray3,bitarray4 = [],[],[],[]
	stamp = ''
	while not re.match(r'^(0x[a-f0-9]{8}|\d+)$', stamp, re.I):
		stamp = input("Enter 4 byte (Epoch) Timestamp (Acceptable Format examples: 0x4EBD02CF or 1321009871): ")
	if stamp.startswith('0x'):
		stamp1,stamp2,stamp3,stamp4 = chr(int(stamp[2:4],16)),chr(int(stamp[4:6],16)),chr(int(stamp[6:8],16)),chr(int(stamp[8:10],16))
	elif int(stamp) < 4294967296:
		stamp = '{:08x}'.format(int(stamp))
		stamp1,stamp2,stamp3,stamp4 = chr(int(stamp[0:2],16)),chr(int(stamp[2:4],16)),chr(int(stamp[4:6],16)),chr(int(stamp[6:8],16))
	else:
		print('Wrong Format')
		gettime()
	stamp1 = '{num:0{width}b}'.format(num=ord(stamp1), width=8)
	stamp2 = '{num:0{width}b}'.format(num=ord(stamp2), width=8)
	stamp3 = '{num:0{width}b}'.format(num=ord(stamp3), width=8)
	stamp4 = '{num:0{width}b}'.format(num=ord(stamp4), width=8)			
	# Make them arrays of 8-bits
	for bit in stamp1:
		bitarray1.append(int(bit))
	for bit in stamp2:
		bitarray2.append(int(bit))
	for bit in stamp3:
		bitarray3.append(int(bit))
	for bit in stamp4:
		bitarray4.append(int(bit))						
	return (bitarray4,bitarray3,bitarray2,bitarray1)

def getOS():
	bitarray = []
	operatingsystem = ''
	print("List of RFC Valid Operating Systems:")
	print("\t0 - FAT filesystem (MS-DOS, OS/2, NT/Win32)")
	print("\t1 - Amiga")
	print("\t2 - VMS (or OpenVMS)")
	print("\t3 - Unix")
	print("\t4 - VM/CMS")
	print("\t5 - Atari TOS")
	print("\t6 - HPFS filesystem (OS/2, NT)")
	print("\t7 - Macintosh")
	print("\t8 - Z-System")
	print("\t9 - CP/M")
	print("\t10 - TOPS-20")
	print("\t11 - NTFS filesystem (NT)")
	print("\t12 - QDOS")
	print("\t13 - Acorn RISCOS")	
	while not re.match(r'^(0x[a-f0-9]{2}|\d+)$', operatingsystem, re.I):
		operatingsystem = input("Enter Operating System (Acceptable Format examples: 0x03 or 3): ")
	if operatingsystem.startswith('0x'):
		operatingsystem = chr(int(operatingsystem[2:4],16))
	elif int(operatingsystem) < 256:
		operatingsystem = '{:02x}'.format(int(operatingsystem))
		operatingsystem = chr(int(operatingsystem[0:2],16))
	else:
		print('Wrong Format')
		getOS()
	operatingsystem = '{num:0{width}b}'.format(num=ord(operatingsystem), width=8)
	# Make them arrays of 8-bits
	for bit in operatingsystem:
		bitarray.append(int(bit))
	return(bitarray)

def getgzlen():
	gzlen = ''
	while not re.match(r'^(0x[a-f0-9]{8}|\d+)$', gzlen, re.I):
		gzlen = input("Enter 4 byte length (Acceptable Format examples: {} or 0x{} (<---Suggested Value)): ".format(glen.getint(),glen.gethex()))
	if gzlen.startswith('0x'):
		gzlen = gzlen[8:10] + gzlen[6:8] + gzlen[4:6] + gzlen[2:4]
	elif int(gzlen) < 4294967296:
		gzlen = '{:08x}'.format(int(gzlen))
	else:
		print('Wrong Format')
		getgzlen()					
	return (gzlen)

def getgzcrc():
	gzcrc = ''
	while not re.match(r'^(0x[a-f0-9]{8}|\d+)$', gzcrc, re.I):
		gzcrc = input("Enter 4 byte CRC value (Acceptable Format examples: 4294967295 or 0xFFFFFFFF): ")
	if gzcrc.startswith('0x'):
		gzcrc = gzcrc[8:10] + gzcrc[6:8] + gzcrc[4:6] + gzcrc[2:4]
	elif int(gzcrc) < 4294967296:
		gzcrc = '{:08x}'.format(int(gzcrc))
		gzcrc = gzcrc[6:8] + gzcrc[4:6] + gzcrc[2:4] + gzcrc[0:2]
	else:
		print('Wrong Format')
		getgzlen()					
	return (gzcrc)

#-------------------#
# Compression Types #
#-------------------#

def stored(last,ftype,data):
	pad = [[0,0,0,0,0]]						# 5-bits of padding for 1st byte
	data.append(last)
	data.append(ftype)
	data.append(pad)
	blocks.print(data,True)
	if args.colors: print('\033[0;31m',end='')	# Red
	length,nlength,lbytes = getlengths()	# Get how many bytes (in all formats)
	data.append(length)
	data.append(nlength)
	blocks.print(data,True)
	literals = []
	for i in range(lbytes):				# Get user supplied amount of literals
		if args.colors: print('\033[0;34m',end='')	# Blue
		subdata = list(data)				# Temporary data	
		lit = getlit(i)							# Get one literal
		literals.append(lit)					# And append it
		subdata.append(literals)			# Append the temporary state
		blocks.print(subdata,True)				# 	and print it for now
		glen.grow(1)
	data.append(literals)
	return(data)

def fixed(last,ftype,data):
	data.append(last)
	data.append(ftype)
	blocks.print(data,True)
	# Get token and see if valid (format), then convert to appropriate int or l,d
	symbol = 0
	sym_data = []
	while symbol != 256:
		if args.colors: print('\033[0;34m',end='')	# Blue
		subdata = list(data)				# Temporary data	

		symbol = getsymbol(0)

		alphabet = []
		for i in range (0,288):
			alphabet.append(str(i))
		bitlengths = [8] * 144 + [9] * 112 + [7] * 24 + [8] * 8
		fixedhuff = nonprefix(alphabet,bitlengths)
		fixedhuff.construct()

		bits = symbolize(fixedhuff.table,symbol,0)
		if isinstance(bits[0], list):
			for entry in bits:
				sym_data.append(entry)
		else:
			sym_data.append(bits)

		subdata.append(sym_data)			# Append the temporary state
		blocks.print(subdata,True)				# 	and print it for now

	data.append(sym_data)
	return(data)

def dynamic(last,ftype,data):
	data.append(last)
	data.append(ftype)
	blocks.print(data,True)
	count,lit,dist,clen,data = getcounts(data)
	data.append(count)
	blocks.print(data,True)
	codehuff, codes, data = getcodealphabet(clen,data)
	data.append(codes)	
	datahuff, disthuff, lengths,data = getdatalengths(lit,dist,codehuff,data)
	data.append(lengths)

	# Now get data
	symbol = 0
	sym_data = []
	while symbol != 256:
		if args.colors: print('\033[0;34m',end='')	# Blue
		subdata = list(data)				# Temporary data
		bits = []
		while not bits:
			symbol = getsymbol(datahuff)
			bits = symbolize(datahuff,symbol,disthuff)
		if isinstance(bits[0], list):
			for entry in bits:
				sym_data.append(entry)
		else:
			sym_data.append(bits)
		subdata.append(sym_data)			# Append the temporary state
		blocks.print(subdata,True)				# 	and print it for now

	data.append(sym_data)

	return(data)


print('######################################################################################')
print('# irriFLATE: the Impractically Redundant Redundant Interactive DEFLATE crafting tool #')
print('######################################################################################\n')

parser = argparse.ArgumentParser(prog='irriFLATE')
parser.add_argument('--errors', help='Allow Huffman table error conditions', action="store_true")
parser.add_argument('--colors', help='Color code similar to infgen fork', action="store_true")
parser.add_argument('--gzip', help='Add gzip header nonsense', action="store_true")
args = parser.parse_args()

blocks = databuffer()
glen = gziplen()
data = []					# Unprocessed list form of data

if args.gzip:
	magic1 = [0,0,0,1,1,1,1,1]
	magic2 = [1,0,0,0,1,0,1,1]
	method = [0,0,0,0,1,0,0,0]
	flag =   [0,0,0,0,0,0,0,0]	# No Flags
	time1, time2, time3, time4 = gettime()
	xfl =    [0,0,0,0,0,0,0,0]	# No Extra Flags
	os = getOS()
	data.append([magic1,magic2,method,flag,time1,time2,time3,time4,xfl,os])

last = [[0]]				# Init 'last?' block
while (last == [[0]]):		# So long as we have more blocks, keep processing

	if args.colors: print('\033[0;35m',end='')	# Purple
	last = getlast()		# Is this the last block and what kind of compression?
	if args.colors: print('\033[0;36m',end='')	# Cyan
	ftype = gettype()		# What kind of compression (Stored,Fixed,Dynamic,Invalid)
	# If it's stored, do suff for that
	if ftype == [[0,0]]: data = stored(last,ftype,data)
	elif ftype == [[0,1]]: data = fixed(last,ftype,data)
	elif ftype == [[1,0]]: data = dynamic(last,ftype,data)
	else: print("Invalid")

if args.colors: print('\033[0;37m',end='')
if args.gzip:
	getgzlen()
	crc = getgzcrc()
print("\nFinal Result:")
blocks.print(data,False)
if args.gzip: print(crc + glen.gethexr())