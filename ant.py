import random
from dataclasses import dataclass, field
from typing import Dict, List, Set, Tuple, Optional

# Reproducible results
random.seed(42)


# =========================================
# Utility functions
# =========================================
def compute_edge_desirability(pheromones: float, cost: float, alpha: float, beta: float) -> float:
    """
    Compute how attractive an edge is for an ant.
    Higher pheromones and lower cost make the edge more desirable.
    """
    return (pheromones ** alpha) * ((1 / cost) ** beta)


def roulette_wheel_selection(probabilities: Dict[str, float]) -> str:
    """
    Select one node using roulette wheel selection.
    Nodes with higher probability are more likely to be chosen.
    """
    pick = random.random()
    current = 0.0

    for node, probability in probabilities.items():
        current += probability
        if current >= pick:
            return node

    # Safety fallback
    return list(probabilities.keys())[-1]


# =========================================
# Graph API
# =========================================
class GraphApi:
    def __init__(self, graph: Dict[str, Dict[str, Dict[str, float]]], evaporation_rate: float):
        """
        graph format:
        {
            "A": {
                "B": {"cost": 2, "pheromones": 1.0},
                "H": {"cost": 2, "pheromones": 1.0}
            },
            ...
        }
        """
        self.graph = graph
        self.evaporation_rate = evaporation_rate

        # Make sure every edge has a pheromone value
        for u in self.graph:
            for v in self.graph[u]:
                if "pheromones" not in self.graph[u][v]:
                    self.graph[u][v]["pheromones"] = 1.0

    def get_all_nodes(self) -> List[str]:
        nodes = set(self.graph.keys())
        for u in self.graph:
            for v in self.graph[u]:
                nodes.add(v)
        return list(nodes)

    def get_neighbors(self, node: str) -> List[str]:
        return list(self.graph.get(node, {}).keys())

    def get_edge_cost(self, u: str, v: str) -> float:
        return self.graph[u][v]["cost"]

    def get_edge_pheromones(self, u: str, v: str) -> float:
        return self.graph[u][v]["pheromones"]

    def set_edge_pheromones(self, u: str, v: str, value: float) -> None:
        self.graph[u][v]["pheromones"] = value

    def evaporate_all_edges(self) -> None:
        """
        Apply pheromone evaporation to all edges in the graph.
        """
        for u in self.graph:
            for v in self.graph[u]:
                self.graph[u][v]["pheromones"] *= (1 - self.evaporation_rate)
                self.graph[u][v]["pheromones"] = max(self.graph[u][v]["pheromones"], 1e-13)

    def deposit_pheromones(self, u: str, v: str, pheromone_amount: float) -> None:
        """
        Add pheromones to one edge.
        """
        self.graph[u][v]["pheromones"] += pheromone_amount


# =========================================
# Ant
# =========================================
@dataclass
class Ant:
    graph_api: GraphApi
    source: str
    destination: str
    alpha: float = 0.7
    beta: float = 0.3
    visited_nodes: Set[str] = field(default_factory=set)
    path: List[str] = field(default_factory=list)
    path_cost: float = 0.0
    is_fit: bool = False
    is_solution_ant: bool = False

    def __post_init__(self) -> None:
        # The ant starts at the source node
        self.current_node = self.source
        self.path.append(self.source)

    def reached_destination(self) -> bool:
        """
        Return True if the ant reached the destination node.
        """
        return self.current_node == self.destination

    def take_step(self) -> None:
        """
        Move the ant one step in the graph.
        """
        self.visited_nodes.add(self.current_node)

        next_node = self._choose_next_node()

        # If no move is possible, the ant stops
        if next_node is None:
            return

        self.path.append(next_node)
        self.path_cost += self.graph_api.get_edge_cost(self.current_node, next_node)
        self.current_node = next_node

    def deposit_pheromones_on_path(self) -> None:
        """
        Deposit pheromones on every edge of the ant's path.
        Shorter paths deposit more pheromones.
        """
        if self.path_cost == 0:
            return

        pheromone_amount = 1 / self.path_cost

        for i in range(len(self.path) - 1):
            u = self.path[i]
            v = self.path[i + 1]
            self.graph_api.deposit_pheromones(u, v, pheromone_amount)

    def _choose_next_node(self) -> Optional[str]:
        """
        Choose the next node for the ant.
        The solution ant is greedy and only follows the strongest pheromone trail.
        """
        unvisited_neighbors = self._get_unvisited_neighbors()

        if self.is_solution_ant:
            if len(unvisited_neighbors) == 0:
                raise Exception(f"No path found from {self.source} to {self.destination}")

            return max(
                unvisited_neighbors,
                key=lambda neighbor: self.graph_api.get_edge_pheromones(self.current_node, neighbor)
            )

        if len(unvisited_neighbors) == 0:
            return None

        probabilities = self._calculate_edge_probabilities(unvisited_neighbors)
        return roulette_wheel_selection(probabilities)

    def _get_unvisited_neighbors(self) -> List[str]:
        """
        Return all neighbors that the ant has not visited yet.
        """
        return [
            node
            for node in self.graph_api.get_neighbors(self.current_node)
            if node not in self.visited_nodes
        ]

    def _calculate_edge_probabilities(self, unvisited_neighbors: List[str]) -> Dict[str, float]:
        """
        Compute transition probabilities for all allowed outgoing edges.
        """
        probabilities: Dict[str, float] = {}
        total_desirability = self._compute_all_edges_desirability(unvisited_neighbors)

        for neighbor in unvisited_neighbors:
            edge_pheromones = self.graph_api.get_edge_pheromones(self.current_node, neighbor)
            edge_cost = self.graph_api.get_edge_cost(self.current_node, neighbor)

            desirability = compute_edge_desirability(
                edge_pheromones,
                edge_cost,
                self.alpha,
                self.beta
            )

            probabilities[neighbor] = desirability / total_desirability

        return probabilities

    def _compute_all_edges_desirability(self, unvisited_neighbors: List[str]) -> float:
        """
        Compute the denominator of the transition probability formula.
        """
        total = 0.0

        for neighbor in unvisited_neighbors:
            edge_pheromones = self.graph_api.get_edge_pheromones(self.current_node, neighbor)
            edge_cost = self.graph_api.get_edge_cost(self.current_node, neighbor)

            total += compute_edge_desirability(
                edge_pheromones,
                edge_cost,
                self.alpha,
                self.beta
            )

        return total


# =========================================
# ACO
# =========================================
@dataclass
class ACO:
    graph: Dict[str, Dict[str, Dict[str, float]]]
    ant_max_steps: int
    num_iterations: int
    ant_random_spawn: bool = True
    evaporation_rate: float = 0.1
    alpha: float = 0.7
    beta: float = 0.3
    search_ants: List[Ant] = field(default_factory=list)

    def __post_init__(self):
        # Create the graph API
        self.graph_api = GraphApi(self.graph, self.evaporation_rate)

        # Initialize all edges with pheromone value 1.0
        for u in self.graph:
            for v in self.graph[u]:
                self.graph_api.set_edge_pheromones(u, v, 1.0)

    def find_shortest_path(self, source: str, destination: str, num_ants: int) -> Tuple[List[str], float]:
        """
        Run the full ACO process and return the best path from source to destination.
        """
        self._deploy_search_ants(source, destination, num_ants)
        solution_ant = self._deploy_solution_ant(source, destination)
        return solution_ant.path, solution_ant.path_cost

    def _deploy_search_ants(self, source: str, destination: str, num_ants: int) -> None:
        """
        Spawn several waves of search ants.
        Each iteration has:
        1. evaporation
        2. forward search
        3. backward pheromone deposit
        """
        for _ in range(self.num_iterations):
            self.search_ants.clear()

            # Evaporate pheromones before the new wave of ants
            self.graph_api.evaporate_all_edges()

            for _ in range(num_ants):
                spawn_point = (
                    random.choice(self.graph_api.get_all_nodes())
                    if self.ant_random_spawn
                    else source
                )

                ant = Ant(
                    self.graph_api,
                    spawn_point,
                    destination,
                    alpha=self.alpha,
                    beta=self.beta
                )
                self.search_ants.append(ant)

            self._deploy_forward_search_ants()
            self._deploy_backward_search_ants()

    def _deploy_forward_search_ants(self) -> None:
        """
        Let every ant move through the graph trying to reach the destination.
        """
        for ant in self.search_ants:
            for _ in range(self.ant_max_steps):
                if ant.reached_destination():
                    ant.is_fit = True
                    break

                ant.take_step()

            if ant.reached_destination():
                ant.is_fit = True

    def _deploy_backward_search_ants(self) -> None:
        """
        Fit ants deposit pheromones on the path they used.
        """
        for ant in self.search_ants:
            if ant.is_fit:
                ant.deposit_pheromones_on_path()

    def _deploy_solution_ant(self, source: str, destination: str) -> Ant:
        """
        Deploy a greedy ant that follows the strongest pheromone trail
        from source to destination.
        """
        ant = Ant(
            self.graph_api,
            source,
            destination,
            alpha=1.0,
            beta=0.0,
            is_solution_ant=True
        )

        for _ in range(self.ant_max_steps):
            if ant.reached_destination():
                break
            ant.take_step()

        if not ant.reached_destination():
            raise Exception(f"No solution path found from {source} to {destination}")

        return ant


# =========================================
# Example graph
# =========================================
G = {
    "A": {
        "B": {"cost": 2},
        "H": {"cost": 2}
    },
    "B": {
        "C": {"cost": 2}
    },
    "C": {
        "F": {"cost": 1},
        "D": {"cost": 10}
    },
    "D": {},
    "E": {
        "D": {"cost": 2}
    },
    "F": {
        "G": {"cost": 1},
        "C": {"cost": 1}
    },
    "G": {
        "F": {"cost": 1},
        "E": {"cost": 2}
    },
    "H": {
        "G": {"cost": 2}
    }
}

aco = ACO(
    graph=G,
    ant_max_steps=100,
    num_iterations=100,
    ant_random_spawn=True,
    evaporation_rate=0.1,
    alpha=0.7,
    beta=0.3
)

aco_path, aco_cost = aco.find_shortest_path(
    source="A",
    destination="D",
    num_ants=100
)

print("ACO path:", " -> ".join(aco_path))
print("ACO path cost:", aco_cost)