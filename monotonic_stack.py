# next greater element for each item in an array
nums = [3, 1, 4, 5]
stack = []
result = [-1] * len(nums)

for i in range(len(nums)):
    while stack and nums[stack[-1]] < nums[i]:
        index = stack.pop()
        result[index] = nums[i]
    stack.append(i)
print(result)
