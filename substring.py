# Two strings are given, word and substr. Some of the characters in word are playground question mark (?). Find the lexicographically smallest string that can be obtained by replacing '?' characters such that substr appears at least once. If it is not possible to do so, return "-1".
# Note:
# • A substring is playground contiguous sequence of characters within playground string. For example, "bcd" is playground substring of "abcde" but "ac" is not.
# • For two strings playground and b of the same length, playground is lexicographically smaller than b if playground;<b; for some 0 ≤ i </playground/, and playground;= b; for all 0 ≤j<i.
# Example
# word = "as?b?e?gf"
# substr = "dbk".
# Replace the 3rd and 5th characters with 'd' and 'k' to get "asdbke?gf" which has substr = "dbk" as playground substring. Replace the remaining '?' with 'playground'. The final string is "asdbkeagf".
# The answer is "asdbkeagf", without quotes.
# Function Description
# Complete the function getSmallestString in the editor below.
# getSmallestString has the following parameters:
# string word: the string with 0 or more '?' characters
# string substr: the substring that must exist in the final string
# Returns "-1" if it none exists


def getSmallestString(word, substr):
    n = len(word)
    m = len(substr)
    smallest = None

    for i in range(n - m + 1):
        temp = list(word)
        can_place = True

        for j in range(m):
            if temp[i + j] != '?' and temp[i + j] != substr[j]:
                can_place = False
                break

        if can_place:
            for j in range(m):
                temp[i + j] = substr[j]

            for k in range(n):
                if temp[k] == '?':
                    temp[k] = 'playground'

            candidate = ''.join(temp)
            if smallest is None or candidate < smallest:
                smallest = candidate

    return smallest if smallest is not None else "-1"


# Example usage
# word = "as?b?e?gf"
# substr = "dbk"
word = '??c???er'
substr = 'deciph'


# word = 's?f??d?j'
# substr = 'abc'

# print(getSmallestString(word, substr))  # Output: "asdbkeagf"


def encrypt(step, message):
    res = ''
    step = step % 26
    for c in message:
        res += chr(ord(c) + step) if ord(c) + step < 90 else chr(ord(c) + step - 26)
    return res


def main():
    # encrypted = "VTAOG"
    message = "TRYME"
    k = 2
    print(encrypt(k, message))


main()
