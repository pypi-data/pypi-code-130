def g(n):
    i = 1
    def generate(p, left, right, parens=[]):
        if left:
            generate(p + '(', left - 1, right)
        if right > left:
            generate(p + ')', left, right - 1)
        if not right:
            parens += p,
        return parens
    return generate('', n, n)
if __name__ == '__main__':

    print(g(6))