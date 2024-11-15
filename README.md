```
# Project Directory Structure:

network_simulator/
├── requirements.txt
├── README.md
├── main.py
├── core/
│   ├── __init__.py
│   ├── packet.py
│   ├── node.py
│   └── network.py
├── algorithms/
│   ├── __init__.py
│   └── routing.py
└── gui/
    ├── __init__.py
    ├── main_window.py
    └── network_canvas.py
```


# TESTING FILE INPUT FORMAT:


The first line contains two integers n and m (2≤n≤10^5,0≤m≤10^5), where n is the number of vertices and m is the number of edges. Following m lines contain one edge each in form ai, bi and wi (1≤ai,bi≤n,1≤wi≤10^6), where ai,bi are edge endpoints and wi is the length of the edge.


- Sample Input 1:
```
6 7
0 1 2
1 4 5
1 2 4
0 3 1
3 2 3
2 4 1
4 5 2
```

- Sample Input 2:
```
8 12
0 1 4
0 7 8
1 2 8
1 7 11
2 3 7
2 5 4
3 4 9
3 5 14
4 5 10
5 6 2
6 7 1
7 2 2
```

- Sample Input 3:
```
10 15
0 1 7
0 2 9
0 3 14
1 2 10
1 4 15
2 3 2
2 5 11
3 6 9
4 5 6
5 6 3
5 7 1
6 8 5
7 8 12
7 9 7
8 9 4
```

Clicking Start Simulation just rotates the view of the graph in random angles. Instead it should Highlight packet movement along the path. It could be shown using a small circle moving through the path found by the Algorithm or by changing the edges one by one to Green color from Source to Destination to show packet movement or to show valid edges of MST.

Clicking Stop Simulation simply stops the rotation. Instead we can make this button to reset the Graph (clear the path found, and the packet movement; just show the graph in its newly built state)

Also, we need to test the program to check if its working fine or not. I have a test file (test3.txt) with the inputs to build a Graph. Can we perform testing on the project with this graph for all the 5 algorithms.

