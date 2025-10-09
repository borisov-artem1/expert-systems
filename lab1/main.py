import graphviz
from copy import deepcopy

from bfs import GraphBFS
from dfs import GraphDFS
from node import Edge
from data import *


def buildGraph(edges: list[Edge]) -> None:
    dot = graphviz.Digraph(
        comment='Граф для поиска в глубину и ширину'
    )
    nodes = []
    for edge in edges:
        nodes.append(str(edge.start.number))
        nodes.append(str(edge.end.number))
        dot.edge(
            str(edge.start.number),
            str(edge.end.number),
            constraint='true',
        )
    for node in list(dict.fromkeys(nodes)):
        dot.node(node)

    dot.render('./docs/graph.gv').replace('\\', '/')


def searchInDepth(edgeList: list[Edge], start: int, goal: int) -> None:
    print("\n\tПОИСК В ГЛУБИНУ\n")
    print(f'Путь: {start} -> {goal}')
    res = GraphDFS(edgeList).find(
        start=start,
        goal=goal,
    )
    GraphDFS.showResult(res)


def searchInWidth(edgeList: list[Edge], start: int, goal: int) -> None:
    print("\n\tПОИСК В ШИРИНУ\n")
    print(f'Путь: {start} -> {goal}')
    res = GraphBFS(edgeList).find(
        start=start,
        goal=goal,
    )
    GraphBFS.showResult(res)


def main(edgeList: list[Edge], start: int, goal: int) -> None:

    buildGraph(edgeList)
    searchInDepth(
        edgeList=deepcopy(edgeList),
        start=start,
        goal=goal,
    )
    searchInWidth(
        edgeList=deepcopy(edgeList),
        start=start,
        goal=goal,
    )


if __name__ == "__main__":

    main(edgeList=EDGE_LIST, start=0, goal=9)


















    # nodes = set()
    # for edge in EDGE_LIST:
    #     nodes.add(edge.start.number)
    #     nodes.add(edge.end.number)
    # nodes = sorted(list(nodes))
    #
    # for start in nodes:
    #     for goal in nodes:
    #         if start == goal:
    #             continue
    #         main(
    #             edgeList=EDGE_LIST,
    #             start=start,
    #             goal=goal,
    #         )