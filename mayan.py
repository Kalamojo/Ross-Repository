
def palindromeAble(word):
    if len(word) <= 1:
        return True
    startStr = word[0]

    for i in range(1, len(word)):
        currStr = word[i]

        if currStr == startStr:
            newStr = word[1:i] + word[i+1:]
            return palindromeAble(newStr)

    newStr = word[1:]
    return palindromeAble(newStr)


def palindromeAble2(word):
    if len(word) <= 1:
        return True
    startStr = word[0]
    endStr = word[len(word)-1]

    for i in range(1, len(word)):
        currStrFromStart = word[i]
        currStrFromEnd = word[len(word)-i-1]

        if currStrFromStart == startStr:
            newStrStart = word[1:i] + word[i+1:]
            return palindromeAble(newStrStart)
        
        if currStrFromEnd == endStr:
            newStrEnd = word[:len(word)-i-1] + word[len(word)-i+1:len(word)-1]
            return palindromeAble(newStrEnd)

    return False

print(palindromeAble("tacocat"))
print(palindromeAble("abcd"))

print(palindromeAble2("tacocat"))
print(palindromeAble2("abcd"))