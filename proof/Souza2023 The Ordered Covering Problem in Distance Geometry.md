# The Ordered Covering Problem in Distance Geometry

Michael Souza ${ }^{1(\boxtimes)}$ (D) Nilton Maia ${ }^{1}$, and Carlile Lavor ${ }^{2}$ (D)<br>${ }^{1}$ Federal University of Ceará, Fortaleza 60440-900, Brazil<br>\{michael,nilton\}@ufc.br<br>${ }^{2}$ IMECC, University of Campinas, Campinas 13081-970, Brazil<br>clavor@unicamp.br


#### Abstract

This study is motivated by the Discretizable Molecular Distance Geometry Problem (DMDGP), a specific category in Distance Geometry, where the search space is discrete. We address the challenge of ordering the DMDGP constraints, a critical factor in the performance of the state-of-the-art SBBU algorithm. To this end, we formalize the constraint ordering problem as a vertex cover problem, which diverges from traditional covering problems due to the substantial importance of the sequence of vertices in the covering. In order to solve the covering problem, we propose a greedy heuristic and compare it to the ordering of the SBBU. The computational results indicate that the greedy heuristic outperforms the SBBU ordering by an average factor of $1,300 \times$.


## 1 Introduction

The Discretizable Molecular Distance Geometry Problem (DMDGP) is a notable combinatorial optimization problem encountered in the determination of threedimensional molecular structures using a set of interatomic distances [3]. This problem has attracted growing attention in computational chemistry and structural biology due to its extensive applications in molecular modeling [5].

The primary goal of the DMDGP is to identify a protein conformation that adheres to a collection of distance constraints, which are usually obtained from experimental data such as Nuclear Magnetic Resonance (NMR) spectroscopy [8]. The computational complexity of the DMDGP persists as a challenge, especially for large and flexible molecules.

The graph representation of the DMDGP offers valuable insights into the problem's structure and has proven useful in developing efficient solution techniques [3]. There is considerable research on vertex ordering in DMDGP instances [1]. However, research on the importance of edge ordering is still incipient. Recently, researchers have examined the connections between the DMDGP and the edge ordering of the associated graph, discovering that the problem becomes more manageable when the graph edges are ordered in a particular manner [2].

The formal definition of the DMDGP can be given as follows [3].

Definition 1 (DMDGP). Given a simple, undirected, weighted graph $G=$ $(V, E, d),|V|=n$, with weight function $d: E \rightarrow(0, \infty)$ and a vertex order $v_{1}, \ldots, v_{n} \in V$, such that

- $\left\{v_{1}, v_{2}, v_{3}\right\}$ is a clique;
- For every $i>3, v_{i}$ is adjacent to $v_{i-3}, v_{i-2}, v_{i-1}$ and

$$
d\left(v_{i-1}, v_{i-3}\right)<d\left(v_{i-1}, v_{i-2}\right)+d\left(v_{i-2}, v_{i-3}\right)
$$

the DMDGP consists in finding a realization $x: V \rightarrow \mathbb{R}^{3}$, such that

$$
\forall\{u, v\} \in E,\left\|x_{u}-x_{v}\right\|=d(u, v)
$$

where $\|\cdot\|$ denotes the Euclidean norm, $x_{v}:=x(v)$, and $d(u, v):=d(\{u, v\})$ (each equation in (1) is called a distance constraint).

Assuming the vertex ordering of the DMDGP definition and denoting the edge $e=\left\{v_{i}, v_{j}\right\}$ by $e=\{i, j\}$, we define the discretization edges by

$$
E_{d}=\{\{i, j\} \in E:|i-j| \leq 3\}
$$

and the pruning edges by

$$
E_{p}=E-E_{d}
$$

The origin of the adjectives "pruning" and "discretization" in edge classification is linked to the Branch-and-Prune (BP) method, the first algorithm proposed for solving the DMDGP [4]. In the BP, the discretization edges are used to represent the search space as a binary tree, and the pruning edges, on the other hand, are used as pruning in a depth-first search for viable realizations.

For many years, BP was the most efficient approach for solving DMDPG, but recently the SBBU algorithm has taken over this position [2]. However, its performance is strongly dependent on the order given to the pruning edges and this issue is an open problem [2].

Given a permutation $\pi=\left(e_{1}, \ldots, e_{m}\right)$ of the pruning edges, the central idea of the SBBU is to reduce the DMDGP to a sequence $\left(P\left(e_{1}\right), \ldots, P\left(e_{m}\right)\right)$ of feasibility subproblems, each of them associated with a different pruning edge. The set of (binary) variables of each subproblem $P(e)$ is given by $[e]=[\{i, j\}]=$ $\left\{b_{i+3}, \ldots, b_{j}\right\}$ and its computational cost grows exponentially with the number of variables. The subproblems may share variables and the efficiency of the SBBU comes from the fact that the variables of each solved subproblem can be removed from all subsequent subproblems.

In the following, we give an example that will be used throughout the paper to facilitate understanding of the concepts presented.

Example 1: Let $G=(V, E, d)$ be a DMDGP instance given by

$$
V=\left\{v_{1}, v_{2}, \ldots, v_{15}\right\} \text { and } E_{p}=\left\{e_{1}, e_{2}, e_{3}, e_{4}\right\}
$$

where

$$
\begin{aligned}
& e_{1}=\left\{v_{1}, v_{8}\right\} \\
& e_{2}=\left\{v_{5}, v_{15}\right\} \\
& e_{3}=\left\{v_{6}, v_{14}\right\} \\
& e_{4}=\left\{v_{11}, v_{15}\right\}
\end{aligned}
$$

If we take the permutation $\pi=\left(e_{1}, e_{2}, e_{3}, e_{4}\right)$, the SBBU will solve the sequence of subproblems $\left(P\left(e_{1}\right), P\left(e_{2}\right), P\left(e_{3}\right), P\left(e_{4}\right)\right)$, whose the sets of variables are $\left\{b_{4}, b_{5}, \ldots, b_{8}\right\},\left\{b_{8}, b_{9}, \ldots, b_{15}\right\},\left\{b_{9}, b_{10}, \ldots, b_{14}\right\}$, and $\left\{b_{14}, b_{15}\right\}$, respectively.

After solving the first subproblem $P\left(e_{1}\right)$, built from the edge $e_{1}=\{1,8\}$, we can remove the variable $b_{8}$ from the set of variables of remaining subproblems. For the same reason, after solving the second subproblem, i.e., $P\left(e_{2}\right)$, there will be no more available variables and the remaining subproblems are already solved.

In the worst case scenario, the cost of solving the sequence of subproblems $\left(P\left(e_{1}\right), P\left(e_{2}\right), P\left(e_{3}\right), P\left(e_{4}\right)\right)$ will be

$$
\begin{aligned}
F(\pi) & =2^{\left|\left\{b_{4}, b_{5}, b_{6}, b_{7}, b_{8}\right\}\right|}+2^{\left|\left\{b_{9}, b_{10}, b_{11}, b_{12}, b_{13}, b_{14}, b_{15}\right\}\right|} \\
& =2^{5}+2^{7} \\
& =160
\end{aligned}
$$

Another permutation, given by $\hat{\pi}=\left(e_{4}, e_{3}, e_{2}, e_{1}\right)$, has cost

$$
\begin{aligned}
F(\hat{\pi}) & =2^{\left|\left\{b_{14}, b_{15}\right\}\right|}+2^{\left|\left\{b_{9}, b_{10}, b_{11}, b_{12}, b_{13}\right\}\right|}+2^{\left|\left\{b_{8}\right\}\right|}+2^{\left|\left\{b_{4}, b_{5}, b_{6}, b_{7}\right\}\right|} \\
& =2^{2}+2^{5}+2^{1}+2^{4} \\
& =54
\end{aligned}
$$

since the related subproblems $P_{4}, P_{3}, P_{2}, P_{1}$ would have, respectively, the variables $\left\{b_{14}, b_{15}\right\},\left\{b_{9}, b_{10}, \ldots, b_{13}\right\},\left\{b_{8}\right\}$, and $\left\{b_{4}, b_{5}, b_{6}, b_{7}\right\}$.

Our primary contribution is to formulate the SBBU pruning edge ordering problem as a graph covering problem. In addition to that, we propose a greedy heuristic to find such ordering and compare it to the ordering of the SBBU algorithm.

# 2 Preliminary Definitions

This section provides the definitions necessary to formalize the SBBU pruning edge ordering problem, called the Ordered Covering Problem (OCP).

## Definition 2 (Edge Interval).

Given a graph $G=(V, E)$, for each $e=\{i, j\} \in E$, we define the edge interval

$$
\llbracket e \rrbracket=\{i+3, \ldots, j\}
$$

and

$$
\llbracket E \rrbracket=\bigcup_{e \in E} \llbracket e \rrbracket
$$

## Definition 3 (Equivalence Relation in $\llbracket E \rrbracket$ ).

Given $i, j \in \llbracket E \rrbracket$, we say that

$$
i \sim j \Longleftrightarrow\left\{e \in E_{p}: i \in \llbracket e \rrbracket\right\}=\left\{e \in E_{p}: j \in \llbracket e \rrbracket\right\}
$$

In the Example 1, the vertex $u=9$ is equivalent to vertex $v=10$, because both belong to the same edge intervals, namely $\llbracket e_{2} \rrbracket$ and $\llbracket e_{3} \rrbracket$. However, $w=14$ is not equivalent to $u=9$, because $u=9 \notin \llbracket e_{4} \rrbracket$, but $w=14 \in \llbracket e_{4} \rrbracket$.

## Definition 4 (Segment).

Let $S=\left\{\sigma_{1}, \ldots, \sigma_{k}\right\}$ be the partition of $\llbracket E \rrbracket$ induced by the equivalence relation of Definition 3. A segment is any element of the partition $S$.

In the Example 1, we have the partition $S=\left\{\sigma_{1}, \sigma_{2}, \sigma_{3}, \sigma_{4}, \sigma_{5}\right\}$ (see Fig. 1), where

$$
\begin{aligned}
\sigma_{1} & =\{4,5,6,7\} \\
\sigma_{2} & =\{8\} \\
\sigma_{3} & =\{9,10,11,12,13\} \\
\sigma_{4} & =\{14\} \\
\sigma_{5} & =\{15\}
\end{aligned}
$$

Definition 5 (Pruning Edge Hypergraph). Given a DMDGP instance with pruning edges $E_{P}=\left\{e_{1}, \ldots, e_{m}\right\}$ and a segment partition $S=\left\{\sigma_{1}, \ldots, \sigma_{k}\right\}$, we define the hypergraph of the pruning edges by $H=\left(E_{P}, T\right)$, where the set of vertices is $E_{P}$ and, for each segment $\sigma_{i}$ in $S$, there is an hyperedge $\tau_{i} \in T$ given by $\tau_{i}=\left\{e \in E_{P}: \sigma_{i} \subset \llbracket e \rrbracket\right\}$.

In other words, the vertices of the pruning edge hypergraph are the pruning edges of the DMDGP graph and each of its hyperedge $\tau_{i}$ is the set of pruning edges whose intervals contain the segment $\sigma_{i}$. Also, note that there is a bijection between the set $T$ of hyperedges in $H$ and the set of segments in $S$. For simplicity, we will replace $\tau_{i}$ by $\sigma_{i}$ in all representations and $H=\left(E_{p}, T\right)$ by $H=\left(E_{p}, S\right)$. Figure 2 illustrates the concepts given in Definition 5 associated to Example 1.

| $E_{p}$ | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 | 12 | 13 | 14 | 15 |
| :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: | :--: |
| $e_{1}=\{1,8\}$ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| $e_{2}=\{5,15\}$ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| $e_{3}=\{6,14\}$ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| $e_{4}=\{11,15\}$ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| $S$ |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
|  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |

Fig. 1. Segments of the graph defined in Example 1.
![img-0.jpeg](img-0.jpeg)

Fig. 2. Graph of Example 1 (restricted to the pruning edges) and the related hypergraph $H=\left(E_{P}, S\right)$.

# 3 The Ordered Covering Problem (OCP)

Before the definition of the OCP, we need additional concepts.

## Definition 6 (Vertex Cover).

A hypergraph $H=\left(E_{P}, S\right)$ is said to be covered by $W \subset E_{p}$ if every hyperedge in $S$ has at least one element in $W$.

In a conventional context, a vertex cover is a subset of vertices. However, in our application, the sequential arrangement of elements within the cover holds significance. Therefore, rather than a subset of vertices, our interest lies in an ordered list.

## Definition 7 (Ordered Vertex Cover).

Given a pruning edge hypergraph $H=\left(E_{p}, S\right)$, a tuple $\pi=\left(\pi_{1}, \ldots, \pi_{k}\right)$ is an ordered vertex cover if $H$ is covered by $\pi$.

For instance, considering the graph $G=(V, E)$ of Example 1, possible ordered covers are $\left(e_{1}, e_{2}\right)$ or $\left(e_{1}, e_{3}, e_{4}\right)$. However, $\left(e_{1}, e_{3}\right)$ is not a cover, since the segment $\sigma_{5}=\{15\}$ remains uncovered (see Fig. 2).

In the SBBU algorithm, every pruning edge $e_{i}$ gives rise to a subproblem on binary variables. Each binary variable within this subproblem is uniquely associated with an element from $\llbracket e_{i} \rrbracket$. Leveraging DMDGP symmetries [7], binary variables from resolved subproblems can be eliminated, thereby retaining only those associated with vertices not included in earlier subproblems.

So, given a tuple $\pi=\left(\pi_{1}, \ldots, \pi_{k}\right)$ of pruning edges, we define

$$
\Gamma\left(\pi_{i}\right)=\llbracket \pi_{i} \rrbracket-\bigcup_{j<i} \llbracket \pi_{j} \rrbracket
$$

and the size of the search space for the subproblem corresponding to edge $\pi_{i}$ is given by:

$$
f\left(\pi_{i}\right)=\left\{2^{\left|\Gamma\left(\pi_{i}\right)\right|}, \text { if } \Gamma\left(\pi_{i}\right) \neq\{ \} \text { and } 0, \text { otherwise }\right\}
$$

Revisiting the Example 1, for the tuple $\pi=\left(\pi_{1}, \pi_{2}\right)=\left(e_{1}, e_{2}\right)$, the cost associated with each edge is computed as follows:

$$
\begin{aligned}
& f\left(\pi_{1}\right)=2^{|\{4,5,6,7,8\}|}=2^{5} \\
& f\left(\pi_{2}\right)=2^{|\{9,10,11,12,13,14,15\}|}=2^{7}
\end{aligned}
$$

Likewise, the size of the search space for $\hat{\pi}=\left(e_{4}, e_{3}, e_{2}, e_{1}\right)$ is given by

$$
\begin{aligned}
& f\left(\hat{\pi}_{1}\right)=2^{|\{14,15\}|}=2^{2} \\
& f\left(\hat{\pi}_{2}\right)=2^{|\{9,10,11,12,13\}|}=2^{5} \\
& f\left(\hat{\pi}_{3}\right)=2^{|\{8\}|}=2^{1} \\
& f\left(\hat{\pi}_{4}\right)=2^{|\{4,5,6,7\}|}=2^{4}
\end{aligned}
$$

The example above suggests the following definition.

# Definition 8 (Ordered Covering Cost).

Given a segment hypergraph $H=\left(E_{p}, S\right)$, the total cost associated with the tuple $\pi=\left(\pi_{1}, \ldots, \pi_{k}\right)$ of pruning edges is calculated as:

$$
F(\pi)=\sum_{i=1}^{k} f\left(\pi_{i}\right)
$$

where $f$ is the partial cost function defined in Eq. (3).
Finally, we can now define the Minimum Ordered Covering Problem.

## Definition 9 (Ordered Covering Problem (OCP)).

Given a DMDGP instance $G=(V, E)$, with a pruning edge set $E_{P}$ and a segment hypergraph $H=\left(E_{P}, S\right)$, the goal is to find:

$$
\pi^{\star}=\arg \min _{\pi \in \Pi(H)} F(\pi)
$$

where $\Pi(H)$ represents all possible ordered vertex covers in $H$.
In the context of the graph represented in Fig. 2, the optimal solution is $\pi^{\star}=\left(e_{4}, e_{3}, e_{2}, e_{1}\right)$, with a total cost $F\left(\pi^{\star}\right)=2^{2}+2^{5}+2^{1}+2^{4}=54$.

# 4 A Greedy Heuristic for the OCP

In this section, we propose a greedy heuristic (GD) to the OCP. GD is a sequential algorithm which begins by calculating the costs associated with each available pruning edge. The pruning edge with the lowest cost is selected, and its incident hyperedges are removed. The costs of the remaining available pruning edges are updated and the process repeats, each time selecting the pruning edge with the lowest cost until no edges remain. The pseudo-code for the GD heuristic is provided in Algorithm 1.

```
Algorithm 1. GD heuristic
    procedure \(\mathrm{GD}\left(E_{p}\right)\)
        Let \(W=E_{p}, \pi=(), i=1\)
        while \(|W|>0\) do \# While \(W\) is not empty
            \(\breve{c}_{i}=\infty\)
            for \(e \in W\) do \#Select the edge with the minimal cost
                \(\pi_{i}=e, c_{i}=f\left(\pi_{i}\right)\)
                if \(c_{i}<\breve{c}_{i}\) then
                    \(\breve{e}=e, \breve{c}_{i}=c_{i}\)
                end if
            end for
                \(W=W-\{\breve{e}\}\)
                \(\pi_{i}=\hat{e}, i=i+1\)
            end while
            return \(\pi\) \# \(\pi\) is a permutation of \(E_{p}\)
end procedure
```

Figure 3 offers a visual representation of the GD heuristic in action. Initially, the algorithm picks the pruning edge with the lowest current cost, specifically edge $e_{4}$ with a cost of 4 . After removing the segments $\sigma_{5}=\{15\}$ and $\sigma_{4}=\{14\}$, and updating the costs, edges $e_{1}$ and $e_{3}$ are now the cheapest, both carrying a cost of 32 . The algorithm, adhering to its greedy strategy, selects edge $e_{1}$, as it comes first among the lowest-cost options. Upon removing the segments $\sigma_{1}=\{4,5,6,7\}$ and $\sigma_{2}=\{8\}$, the remaining edges, namely $e_{2}$ and $e_{3}$, now bear a cost of 32 . The algorithm sticks to its strategy and selects the pruning edge $e_{2}$. Since all segments are now covered, the remaining edge costs nothing. Consequently, the sequence generated by the GD heuristic is $\left(e_{4}, e_{1}, e_{2}, e_{3}\right)$ with a total cost of 68 , which equals the sum of $4,32,32$, and 0 .

## 5 Analyzing Results and Discussion

This section presents a comparative analysis of the GD heuristic (see Algoritm 1) and the pruning edge ordering implemented in the SBBU algorithm as introduced by [2]. To provide a comprehensive comparison, we also include the exact solution obtained by brute force (BF), i.e., derived from scrutinizing all conceivable permutations of pruning edges.

![img-1.jpeg](img-1.jpeg)

Fig. 3. Edge selection of GD heuristic, with steps (A), (B), (C), and (D).

These experiments were performed on a system equipped with an Intel Core i7-3770 CPU running at a clock speed of 3.40 GHz , supported by 8 GB of RAM, and utilizing Ubuntu 20.04.6 LTS. The heuristic was implemented in Python 3.10.6.

Our tests involved 5,000 randomly generated instances, each with 30 vertices and 5 pruning edges, where one of them was $\{1,30\}$ and the remaining four edges were randomly generated. For each random pruning edge $\{i, j\}$, we selected vertex $i$ from the set $\{1,2, \ldots, 26\}$ and $j$ from the range $\{i+4, \ldots, 30\}$ at random. The edge $\{1,30\}$ is the hardest constraint, since it has the largest search space [6].

We assessed the algorithms' efficiency using the following metric:

$$
\operatorname{gap}(\pi)=\frac{F(\pi)-F\left(\pi^{\star}\right)}{F\left(\pi^{\star}\right)}
$$

where $\pi$ represents a permutation of pruning edges and $\pi^{\star}$ indicates the optimal permutation of pruning edges computed via brute force (BF).

Table 1 illustrates the results for all instances, summarizing details about the number of vertices, pruning edges, and segments of each instance, alongside the cost of the optimal solution and the gaps related to the GD heuristic (gapGD) and the SSBU ordering (gapSB).

These results highlight the sub-optimality of GD and the SBBU ordering, showing their potential to produce solutions inferior to the optimal ones. The GD heuristic generated results that were, in the worst scenario, about $1.5 \times$ the optimal solution's cost (gapGD $=0.5$ ). The performance of the SBBU ordering was much worse, with over a quarter of its results costing more than twice as much as the optimal solution, with some even reaching nearly $6,500 \times$.

Table 1. Algorithmic cost comparison.

|  | -V- | -Ep- | -S- | costBF | gapGD | gapSB |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| mean | 30 | 5 | 7.62 | $4.6 \mathrm{E}+4$ | $1.0 \mathrm{E}-3$ | $1.3 \mathrm{E}+1$ |
| std | 0 | 0 | 0.94 | $2.9 \mathrm{E}+5$ | $1.5 \mathrm{E}-2$ | $1.4 \mathrm{E}+2$ |
| min | 30 | 5 | 5 | $2.6 \mathrm{E}+2$ | 0 | 0 |
| $25 \%$ | 30 | 5 | 7 | $9.0 \mathrm{E}+2$ | 0 | 0 |
| $50 \%$ | 30 | 5 | 8 | $2.2 \mathrm{E}+3$ | 0 | $1.0 \mathrm{E}-3$ |
| $75 \%$ | 30 | 5 | 8 | $8.5 \mathrm{E}+3$ | 0 | $9.9 \mathrm{E}-1$ |
| max | 30 | 5 | 9 | $8.4 \mathrm{E}+6$ | $5.3 \mathrm{E}-1$ | $6.5 \mathrm{E}+3$ |

Despite the clear GD heuristic's average advantage, it only outperformed the SBBU ordering slightly over half of the 5 K instances (in exact 2742 instances). That is, the SBBU ordering low average performance is the result of extreme gaps such as its maximum value of 6.5 K . So, we can say that the great advantage of GD heuristic is its robustness.

Table 2 showcases the four instances where the GD heuristic produced the worst results. The instance labeled as test650 is noteworthy because the GD heuristic's gap was larger than the SBBU ordering gap. Figure 4 represents the hypergraph $H\left(E_{p}, S\right)$ for each of the instances highlighted in Table 2.

Table 2. Worst results of the GD heuristic.

| ID | -V- | -Ep- | -S- | costBF | gapGD | gapSB |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| test374 | 30 | 5 | 8 | 720 | 0.525 | 0.525 |
| test3007 | 30 | 5 | 7 | 2310 | 0.345 | 0.345 |
| test3267 | 30 | 5 | 9 | 624 | 0.314 | 0.314 |
| test650 | 30 | 5 | 9 | 2374 | 0.301 | 0.000 |

Table 3 outlines the four instances in which the SBBU ordering yielded its worst results. Figure 5 provides a graphical representation of the hypergraph $H\left(E_{p}, S\right)$ for each of the instances in Table 3.

![img-2.jpeg](img-2.jpeg)

Fig. 4. Hypergraphs $H\left(E_{p}, S\right)$ for the instances test374, test3007, test3267, and test650 of Table 2.
![img-3.jpeg](img-3.jpeg)

Fig. 5. Hypergraphs $H\left(E_{p}, S\right)$ for the instances test1675, test4351, test213, and test 4562 .

Table 3. Worst results of the SBBU ordering.

| ID | -V- | -Ep- | -S- | costBF | gapGD | gapSB |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| test1675 | 30 | 5 | 8 | 2586 | 0.000 | 6486.71 |
| test4351 | 30 | 5 | 8 | 416 | 0.000 | 5040.28 |
| test213 | 30 | 5 | 8 | 652 | 0.000 | 3215.51 |
| test4562 | 30 | 5 | 8 | 4168 | 0.000 | 2011.62 |

# 6 Conclusion

Despite the SBBU marked superiority over the BP algorithm, it is strongly dependent on the ordering of pruning edges [2]. We have formalized the pruning edge ordering problem associated with the SBBU algorithm, framing it as a vertex cover problem.

Distinct from traditional covering problems, the sequence of vertices in our cover problem holds significant relevance. To address this, we have introduced a greedy heuristic specifically designed to tackle this pruning edge ordering problem.

Through a series of computational experiments conducted on over 5,000 instances, we evaluated the efficiency of the proposed heuristic in comparison with the ordering used in the SBBU algorithm. The results were promising: on average, the cost of solutions derived from our heuristic was a mere $0.1 \%$ higher than the optimal solutions, with a standard deviation of $1.5 \%$. Conversely, the average cost of the solutions derived from the SBBU ordering was staggering: $1,300 \times$ higher than the optimal cost with an alarming deviation of $14,200 \%$.

These results are highly encouraging, suggesting the considerable potential of our proposed heuristic to enhance the performance of the SBBU algorithm. As we move forward, our future work will focus on examining the performance of the SBBU algorithm using our proposed heuristic in scenarios with larger and more intricate instances.

Acknowledgements. We thank the Brazilian research agencies FAPESP and CNPq, and the comments made by the reviewers.

Conflict of interest. No conflict of interest.

## References

1. Cassioli, A., Günlük, O., Lavor, C., Liberti, L.: Discretization vertex orders in distance geometry. Disc. Appl. Math. 197, 27-41 (2015)
2. Gonçalves, D.S., Lavor, C., Liberti, L., Souza, M.: A new algorithm for the k dmdgp subclass of distance geometry problems with exact distances. Algorithmica 83(8), $2400-2426(2021)$
3. Lavor, C., Liberti, L., Maculan, N., Mucherino, A.: The discretizable molecular distance geometry problem. Comput. Optim. Appl. 52, 115-146 (2012)
4. Liberti, L., Lavor, C., Maculan, N.: A branch-and-prune algorithm for the molecular distance geometry problem. Int. Trans. Oper. Res. 15(1), 1-17 (2008)
5. Liberti, L., Lavor, C., Maculan, N., Mucherino, A.: Euclidean distance geometry and applications. SIAM Rev. 56(1), 3-69 (2014)
6. Liberti, L., Masson, B., Lee, J., Lavor, C., Mucherino, A.: On the number of realizations of certain henneberg graphs arising in protein conformation. Disc. Appl. Math. 165, 213-232 (2014)
7. Mucherino, A., Lavor, C., Liberti, L.: Exploiting symmetry properties of the discretizable molecular distance geometry problem. J. Bioinf. Comput. Biol. 10(03), 1242009 (2012)
8. Wüthrich, K.: Protein structure determination in solution by nuclear magnetic resonance spectroscopy. Science 243, 4887 (1989)