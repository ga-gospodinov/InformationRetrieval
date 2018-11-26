def code(numbers):
	varbyte_string = ''
	for number in numbers:
		chunks = []
		while number >= 128:
			number, chunk = divmod(number, 128)
			chunks.append(chunk)
		chunks.append(number)

		coded_string = ''

		coded_string += chr(chunks[0] ^ 128)

		for chunk in chunks[1:]:
			coded_string += chr(chunk)

		varbyte_string += coded_string[::-1]

	return varbyte_string

def decode(varbyte_string):
	numbers = []
	chunks = []
	for byte in varbyte_string:
		chunk = ord(byte)
		if chunk >= 128:
			chunk -= 128
			chunks.append(chunk)
			number = sum([chunk * 128 ** index for index, chunk in enumerate(reversed(chunks))])
			numbers.append(number)
			chunks = []
		else:
			chunks.append(chunk)
	return numbers

if __name__ == '__main__':
	a = [3141592653589, 271828459045]
	print decode(code(a))