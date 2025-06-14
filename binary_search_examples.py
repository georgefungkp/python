# Binary Search Examples and Implementations
# This file contains various implementations and applications of the binary search algorithm

def binary_search_standard(arr, target):
    """
    Standard binary search implementation to find a target in a sorted array.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Parameters:
        arr (list): Sorted array to search in
        target: Value to search for

    Returns:
        int: Index of target if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2  # Avoid potential overflow

        # Check if target is at mid
        if arr[mid] == target:
            return mid

        # If target is greater, ignore left half
        if arr[mid] < target:
            left = mid + 1
        # If target is smaller, ignore right half
        else:
            right = mid - 1

    # Target is not in array
    return -1


def binary_search_recursive(arr, target, left=None, right=None):
    """
    Recursive implementation of binary search.

    Time Complexity: O(log n)
    Space Complexity: O(log n) due to recursive call stack

    Parameters:
        arr (list): Sorted array to search in
        target: Value to search for
        left (int): Left boundary of search (default: 0)
        right (int): Right boundary of search (default: len(arr)-1)

    Returns:
        int: Index of target if found, -1 otherwise
    """
    # Initialize boundaries for first call
    if left is None: left = 0
    if right is None: right = len(arr) - 1

    # Base case: element not found
    if left > right:
        return -1

    # Find middle element
    mid = left + (right - left) // 2

    # Check if target is at mid
    if arr[mid] == target:
        return mid

    # Recursive cases
    if arr[mid] < target:
        # Search in right half
        return binary_search_recursive(arr, target, mid + 1, right)
    else:
        # Search in left half
        return binary_search_recursive(arr, target, left, mid - 1)


def binary_search_leftmost(arr, target):
    """
    Find the leftmost occurrence of target in a sorted array.
    Useful for arrays with duplicates.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Parameters:
        arr (list): Sorted array to search in
        target: Value to search for

    Returns:
        int: Index of leftmost occurrence if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1
    result = -1  # Store potential result

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            result = mid  # Store this index
            right = mid - 1  # Continue searching left side
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_rightmost(arr, target):
    """
    Find the rightmost occurrence of target in a sorted array.
    Useful for arrays with duplicates.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Parameters:
        arr (list): Sorted array to search in
        target: Value to search for

    Returns:
        int: Index of rightmost occurrence if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1
    result = -1  # Store potential result

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            result = mid  # Store this index
            left = mid + 1  # Continue searching right side
        elif arr[mid] < target:
            left = mid + 1
        else:
            right = mid - 1

    return result


def binary_search_range(arr, target):
    """
    Find the range (first and last positions) of target in a sorted array.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Parameters:
        arr (list): Sorted array to search in
        target: Value to search for

    Returns:
        tuple: (first_position, last_position), (-1, -1) if not found
    """
    first = binary_search_leftmost(arr, target)
    if first == -1:  # If target not found
        return (-1, -1)

    last = binary_search_rightmost(arr, target)
    return (first, last)


def binary_search_rotated(arr, target):
    """
    Find target in a rotated sorted array (e.g., [4,5,6,7,0,1,2]).
    No duplicates are allowed in the array.

    Time Complexity: O(log n)
    Space Complexity: O(1)

    Parameters:
        arr (list): Rotated sorted array to search in
        target: Value to search for

    Returns:
        int: Index of target if found, -1 otherwise
    """
    left, right = 0, len(arr) - 1

    while left <= right:
        mid = left + (right - left) // 2

        if arr[mid] == target:
            return mid

        # Check which half is sorted
        if arr[left] <= arr[mid]:  # Left half is sorted
            # Check if target is in left half
            if arr[left] <= target < arr[mid]:
                right = mid - 1
            else:
                left = mid + 1
        else:  # Right half is sorted
            # Check if target is in right half
            if arr[mid] < target <= arr[right]:
                left = mid + 1
            else:
                right = mid - 1

    return -1


# Test the binary search functions
if __name__ == "__main__":
    # Standard binary search test
    sorted_array = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
    print("\nStandard Binary Search:")
    for target in [5, 11, 20]:
        result = binary_search_standard(sorted_array, target)
        found_msg = f"Found at index {result}" if result != -1 else "Not found"
        print(f"Search for {target}: {found_msg}")

    # Binary search with duplicates
    array_with_duplicates = [1, 2, 2, 2, 3, 4, 5, 5, 5, 6]
    print("\nBinary Search with Duplicates:")
    for target in [2, 5]:
        left, right = binary_search_range(array_with_duplicates, target)
        if left != -1:
            print(f"Range of {target}: from index {left} to {right}")
            print(f"Number of occurrences: {right - left + 1}")
        else:
            print(f"Target {target} not found")

    # Rotated array binary search
    rotated_array = [7, 8, 9, 1, 2, 3, 4, 5, 6]
    print("\nRotated Array Binary Search:")
    for target in [3, 8, 10]:
        result = binary_search_rotated(rotated_array, target)
        found_msg = f"Found at index {result}" if result != -1 else "Not found"
        print(f"Search for {target} in rotated array: {found_msg}")
# products = ['coddle', 'coddles', 'code', 'codephone', 'codes']
products = ['mobile', 'moneypot', 'monitor', 'mouse', 'mousepad']
# products = ['mouse', 'mousepad']
# products = ['crkvwptcqpxixdxswlnbzqvegbkcrzyvqyfpivuqyvkwctpqxsvjzmdkxwkxrydzwdavrydzsenajijzxzruziraagmydnhukkpscglmgkjnslerwjwjiousltlcxpjqutgqwrfrzgyzdaxssjxqjvtqupmiqmjebsmwtkv',
#             'e',
#             'geukdsnoidgngoaeutlenbeacbkwvfsnaxpjzwyfaaxtgpuagsyihiiukpcqruacvpztqpfzjkqedrgawldrwsvoeckpbaxiewvsxgwfrvxwjporwmsdzrfgxsvhqtshdpiwugahibdxwapqgct',
#             'gmdipfdbrbpxtoguoczzylbvtwvkeizjzpkitxemlbpntgabfquceexutahhhtazajrvyebswsfcdmyzrbcuhbbomvfbigueneoxboixhmgadagvesvohhxikxpsgepomzrmgopjwcunqzweycsfzonuxjvseetopcwkqrxj',
#             'jemqslzvrbskvqvjwbivkxiwvzunyvyydicmnujacrzbomugingscfodfroyatsdwfbbktajyvbcwxusitnbbupjrjniemerrlujvfkbvzuzyysrunmwyftywgpybacbgvprybhhbymnc',
#             'jhljdprevkydjfzuynjkmaxnljentqvjxxmkguoaxpefhss',
#             'jhljdwmzajbejfyewkvhnpbenzedarvjstpywnqsrwbzrwsdiazferiliucjutqsriviycqgcycqgptbvxjpdmcszurlxynvjvlpmcsjvvuhwdwggxpkisfyjpgmunydqnkgdyvcycdcaeeqngkpqbuylneelpkmrtytqt',
#             'jhljdwmzajzhbzakqaljdrmlykjmnuxobohfrtkkfomnncrtyhnrmnktddhctwbmjdrbyewjtxlmvwwonjmurxatshntdvdmkyqmhsnjvykrydssnf',
#             'jhljdwmzajzhbzlnuvnzlypvdwelcnexkdfskoxkymborxnexhyctvminpdvdekwmokprwgskobsianemxeneuovowebrusncqutzhujgksw'
#             'iovoialiqokiwkmbybbjbeenxarwoxbupustfxqgpivsawecebesdyfvsknvlnt',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbcrmqovcdmysuiwudydsgndjtflykmzfvoawkkargexytjuihnomiqezyqujqalafxxcg',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfglaovojaskdmlzqdcpljyogaghonmtqlmkheawtgjfjjfxwepamg',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtoqqwlufsrshrqebujsztrldskcxywiiunzpvqztigbhsnf',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtyinanuoqxhrzpid',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytrpopmqtztvx',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjylhkiabzfarxcdfmnazomofjjovszxwsajkgjnnqgqhxbzfzkczmqdargeklvqphngmf',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyskqujjuoyergkhjiuetyuqmxlbrhvqccdojfuvxapxxmttcvkyhpwhnswbn',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzmdgvq',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgiclqgtjennjvmb',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltcjueumbdovisfkvoiaefajnbyqrvddajklehucxgvwgwltqwrwtljigyazlxgmlubt',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkhaeyrgeellxwuzdaa',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkhrfhyuqwrlprwdrztwncnfawbhmhizugfbykzjlmkorprcpmvaqnxollxjduplrpbpkoc',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdmglxthgqgkfdxwbhglifxgddbudyvzbstnzajtzxrwenpgxbbgnoopjlqmvksbrblqgpoau',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwmgeapqviocqlwxhwdrspdnvfwsueyflaqyugnaiaudyebelavrmcinpegwdkvasq',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdrrsydhaggrspsxqxjyamfzdjijwkkzlilzetrbhoufyjtvt',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthexbnznixtpktmxlxadnnjuzynvmcajkcopefw',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhahpb',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxktgckdmdknsghw',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxkthszqffcuanghx',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxkthszqffcuanqe',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxkthszqffcurmze',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxofu',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekymqswxnblzzdrsx',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruneluwssmtwondnulmnmcric',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvttiblsecbwbjiavybqjbubhqsosblxhjlazg',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoewiednmizszpecznfjvzgpkzmfkkavirmvzcosdzbtvlfbwbwwedxgpqcniqf',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfafumkcmonskgyuaffuitlxqxeubifkawlkqfntkfxxjomjuffcdprwzwzpltnxaritqqdtnmuhndokxnphlhdygvfcifg',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvjslklhoywcnkynwmpcsxqmffltmxerhqhftrggsxbdjywazmbcipemgiuge',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxqhqxshczwndevtdwdugkhjm',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprrziwvgzuwpysmnkfo',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzzgvnyvifeoconimcrvivomvcbxndlagodcreyjsujuujdtlggyqju',
#             'jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytylppbjczpsuzbiyuddxnxcjumqrmswhtkssqxdbmjyqpznmtb',
#             'jhljdwmzajzhbzlnuvnzlypvdwvlwblyfwchpsytymysowjgldscaabrrvzelklbcllnmpersjfezqmhhphq',
#             'jhljdwmzajzhrugyiyhfobthuolttcxhbabkgztyewftchcgnbdlfklinalsnbisnbauhavkklbstnljdabxjxrlfpzcwdvwqbuelrnpxwfyxkbsuwqhhavxjilscwsejepgeagioyuygvzeaosdydemiuzlxrrymgiipmhlrroacigbirotx',
#             'jyutgoofzhfhohyrtjnggsyboyfvvseghifejwcdmvzlnbvqoitmikuayaqjf',
#             'kidvqciatjrmmwmgufyjdnfiznohewcegbdcklsrtxlrjpskyyihjydbsmacyrbjgihxbwruhuzlzgqmwyqosvgrtzelkcwkfettntncocivaavgnyodrshepkpbjy',
#             'ksnkokylbndlrspqntlwkvzggnltumwgietvlntdtycnlfwtonlulrvkbwwalcbphlfyuklwaxepyykq',
#             'mrklrbtfxyyxkmreglnvsprvpcqeiabavruobchukroohjupgdfcid',
#             'mzkgksixdpjpjucbwcosbutjhqxbzrajlprvfyufivhsifkhqxzhskosssvazinljvqncpbibothtrmfkfrtxjgqvml',
#             'pgfelbqsbxstdvbwzwclelbcfuskheuguwevadhynw',
#             'qjkacgudpntqmnfjwajlvwflwujmzgumbmwnyxmidpxhjvbofutovdrxvsibvivvcpvahdlnvdpyrvkmqbodehmaos',
#             'sawxfkvjanqhwadpiftppejzh',
#             'swtiutizdsgfqoouqpqnfnymxozrkmifylc',
#             'tnhgepglkwouzzzuirpzblbiqiupywjoenrzgtneawycsvrmnsnthtpixftlvrhjfoohkcjttpdnmtergskgcywrnkhqbdclj',
#             'wmdynsfqafmwakfzgmmjv',
#             'znzriimpzgugozuixpdsqyxcuqsuwwwenchyemscgjwmchlctkbtkdjcbkgswfwxr']
search_word = "jhljdwmzajzhbzlnuvnzlypvdwelzenkmuekbfhhwrfgltwxtytyeifurnnvdjyzwzsqyprcqxatrfvfabwoeoybqfbtkgicltqtkzgdvpwsnzvvhgelwqqtdruknthfmpgekmnsnxbjtgkorweyotixwlcwyvjhsgjmcxkthszqffcuanggmjxvzykcfajvlbromoiaabgtihdkyxrfdlofvhsbdjlbyktpawxdwqgwlaxqjzdvvvvrksuhfuyjimkuiptxbkehzvgefavleaegbopivdhzpzhgehjorevmxvzivdigmldsrgtlptdorekere"
products.sort()
n = len(products)

def get_lower_bound(products, sub_search):
    start, end = 0, n - 1
    while start < end:
        mid = (end + start) // 2
        if products[mid] == sub_search:
            return mid
        elif products[mid] < sub_search:
            start = mid + 1
        else:
            end = mid - 1
    return start


print(get_lower_bound(products, 'j'))