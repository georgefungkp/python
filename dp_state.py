from functools import lru_cache
from typing import List


"""
Iterative Dynamic Programming with state machine 
"""
from typing import List


def maxProfit_backwardDP(prices: List[int], k: int) -> int:
    n = len(prices)
    if n < 2 or k == 0:
        return 0

    # dp[i][t][s]: max profit at day i, t transactions used, state s
    dp = [[[-float('inf')] * 3 for _ in range(k + 1)] for _ in range(n + 1)]

    # Base case: after last day, profit is 0 if no position
    for t in range(k + 1):
        dp[n][t][0] = 0

    for i in range(n - 1, -1, -1):
        for t in range(k + 1):
            # State 0: No position
            dp[i][t][0] = dp[i + 1][t][0]  # Do nothing
            if t < k:  # Can use another transaction
                # Start long (buy)
                dp[i][t][0] = max(dp[i][t][0], dp[i + 1][t + 1][1] - prices[i])
                # Start short (sell)
                dp[i][t][0] = max(dp[i][t][0], dp[i + 1][t + 1][2] + prices[i])

            # State 1: Holding long
            dp[i][t][1] = dp[i + 1][t][1]  # Keep holding
            dp[i][t][1] = max(dp[i][t][1], dp[i + 1][t][0] + prices[i])  # Sell

            # State 2: Holding short
            dp[i][t][2] = dp[i + 1][t][2]  # Keep holding
            dp[i][t][2] = max(dp[i][t][2], dp[i + 1][t][0] - prices[i])  # Cover

    return dp[0][0][0]  # Start with 0 transactions used, no position

def maxProfit_forwardDP(prices: List[int], k: int) -> int:
    n = len(prices)
    dp = [[[-float('inf')] * 3 for _ in range(k + 1)] for _ in range(n + 1)]

    for txn in range(k + 1):
        dp[0][txn][0] = 0

    for day in range(1, n + 1):
        for txn in range(k + 1):
            # print('{},{}'.format(day, txn))
            dp[day][txn][0] = max(
                dp[day - 1][txn][0],
                dp[day - 1][txn][1] + prices[day - 1],
                dp[day - 1][txn][2] - prices[day - 1],
            )

            if txn > 0:
                dp[day][txn][1] = max(
                    dp[day-1][txn][1],
                    dp[day - 1][txn - 1][0] - prices[day - 1]
                )

                dp[day][txn][2] = max(
                    dp[day-1][txn][2],
                    dp[day - 1][txn - 1][0] + prices[day - 1],
                )

    return dp[n][k][0]

def maxProfit_recursive(prices: List[int], k: int) -> int:
    n = len(prices)
    # dp[i][t][s]: max profit at day i, t transactions used, state s
    dp = [[[-float('inf')] * 3 for _ in range(k + 1)] for _ in range(n + 1)]

    @lru_cache(maxsize=None)
    def recursive(day, txn, status):
        hold = -float('inf')
        long = -float('inf')
        short = -float('inf')

        if day == n:
            if status == 0:
                return 0
            else:
                return -float('inf')

        if status == 0:
            hold = recursive(day + 1, txn, 0)
            if txn < k:
                long = recursive(day + 1, txn + 1, 1) - prices[day]
                short = recursive(day + 1, txn + 1, 2) + prices[day]

        elif status == 1:
            hold = recursive(day + 1, txn, 0) + prices[day]
            long = recursive(day + 1, txn, 1)

        elif status == 2:
            hold = recursive(day + 1, txn, 0) - prices[day]
            short = recursive(day + 1, txn, 2)

        value =  max(hold, long, short)
        dp[day][txn][status] = value
        return value

    return recursive(0, 0, 0)


# prices = [12,16,19,19,8,1,19,13,9]
# prices = [1,7,9,8,2]
prices=[1,2,3]
k = 2
print(maxProfit_forwardDP(prices, k))