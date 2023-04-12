import sys

def my_function(x):
  return x[::-1]

print(my_function(" ".join(sys.argv[1:])).swapcase())
