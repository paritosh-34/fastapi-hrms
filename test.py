ids = [0, 1, 2, 3]

for element in ids:
	print(f"Element is {element}")

for i in range(0, 4):
	print(f"Element at {i} is {ids[i]}")

a = 2
b = 3

a, b = b, a

print(a, b)


# map function for doubling

doubled_ids = [x * 2 for x in ids]

print(doubled_ids)


# filter

even_ids = [x for x in ids if x % 2 == 0]
print("even ids", even_ids)

scores = {
	"aditya": 9,
	"paritosh": 10,
	"gaurav": 11,
}

for k, v in scores.items():
	print(f"key: {k} : {v}")

def doublee(num: int) -> int:
	return num * 2

doublee2 = lambda x : x * 2

