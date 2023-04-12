import sys

if len(sys.argv) == 2:
	try:
		number = int(sys.argv[1])
		if number == 0:
			print("The number is zero")
		elif number % 2 == 0:
			print("The number is even")
		else:
			print("The number is odd")
	except ValueError:
		print("Error: Please provide an integer as argument")
else:
	print("Error: Please provide one argument")
