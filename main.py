# print(1 < 2 < 3 == 3)
# a = [1,2,3]
# print(a*2)


def func(a, b=[]):
    b.append(a)
    return b

print(func(1))
print(func(2))