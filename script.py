val = 0

for _ in range(10):
	val += 1
	print(val)
	while True:
		inp = input("Press ENTER to continue.")
		if inp == '\n':
			break
print("Goodbye")
