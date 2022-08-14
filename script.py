string = """
9
9
0
6
4
7
6
6
2
10
7
2
4
5
6
0
5
7
6
4
4
5
5
2
1
2
5
7
1
0
2
8
1
0
1
0
1
0
1
"""

dict = {
        0: "FUNCTION",
        1: "END_FUNCTION",
        2: "RETRIEVE",
        3: "STRING",
        4: "INTEGER",
        5: "INVOKE",
        6: "DECLARE",
        7: "ASSIGN",
        8: "RETURN",
        9: "STRUCTURE",
        10: "POINTER",
}

for character in string.splitlines():
    try:
        print(dict[int(character)])
    except ValueError:
        pass
