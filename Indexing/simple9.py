import struct

payload = 28
code_length = 4

def code(numbers):
	simple9_struct = [(28,  1, 0,  1<<1),
					  (14,  2, 1,  1<<2),
					  ( 9,  3, 2,  1<<3),
					  ( 7,  4, 3,  1<<4),
					  ( 5,  5, 4,  1<<5),
					  ( 4,  7, 5,  1<<7),
					  ( 3,  9, 6,  1<<9),
					  ( 2, 14, 7, 1<<14),
					  ( 1, 28, 8, 1<<28)]

	simple9_string = ''
	coded_numbers = 0
	last_numbers = len(numbers)

	while last_numbers > 0:
		for count, width, code, max_number in simple9_struct:
			if count > last_numbers:
				continue

			large_numbers = False
			for number in numbers[coded_numbers:coded_numbers+count]:
				if number > max_number:
					large_numbers = True
					break

			if large_numbers:
				continue

			simple9_container = code << payload
			shift = payload - width
			for index, number in enumerate(numbers[coded_numbers:coded_numbers+count]):
				simple9_container |= number << shift
				shift -= width

			simple9_string += struct.pack('>I', simple9_container)

			coded_numbers += count

			last_numbers -= count

			break

	return simple9_string

def decode(simple9_string):
	code2width_count = [(1,28),
					    (2,14),
					    (3, 9),
					    (4, 7),
					    (5, 5),
					    (7, 4),
					    (9, 3),
					    (14,2), 
					    (28,1)]

	numbers = []

	def mask(width):
		a = 1 << width - 1
		return (a - 1) ^ a

	for byte in [struct.unpack('>I', simple9_string[i:i+code_length])[0] for i in range(0, len(simple9_string), code_length)]:
		code = byte >> payload
		width, count = code2width_count[code]
		shift = payload - width
		for i in range(count):
			numbers.append((byte >> shift) & mask(width))
			shift -= width
	
	return numbers

if __name__ == '__main__':
	a = [314, 314, 314, 271, 271, 271]
	print decode(code(a))