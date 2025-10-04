# Ordered Covering Problem (OCP) — Definitions

This document contains the formal definitions of the Ordered Covering Problem (OCP) and all related concepts, extracted from Souza et al. (2023).

## 1. Edge Interval

**Definition 1 (Edge Interval).**
Given a graph $G=(V,E)$ with a vertex ordering $v_1, \ldots, v_n$, for each edge $e=\{i,j\} \in E$ with $i < j$, we define the **edge interval**

$$
\llbracket e \rrbracket = \{i+3, i+4, \ldots, j\}.
$$

For a set of edges $E$, we define

$$
\llbracket E \rrbracket = \bigcup_{e \in E} \llbracket e \rrbracket.
$$

---

## 2. Equivalence Relation and Segments

**Definition 2 (Equivalence Relation in $\llbracket E \rrbracket$).**
Given $i, j \in \llbracket E \rrbracket$, we say that

$$
i \sim j \iff \{e \in E : i \in \llbracket e \rrbracket\} = \{e \in E : j \in \llbracket e \rrbracket\}.
$$

In other words, two indices are equivalent if they belong to exactly the same set of edge intervals.

**Definition 3 (Segment).**
Let $S = \{\sigma_1, \ldots, \sigma_k\}$ be the partition of $\llbracket E \rrbracket$ induced by the equivalence relation $\sim$ of Definition 2. Each element $\sigma_i \in S$ is called a **segment**.

**Example.**
If $E = \{e_1, e_2, e_3, e_4\}$ with
- $e_1 = \{1, 8\}$, so $\llbracket e_1 \rrbracket = \{4,5,6,7,8\}$
- $e_2 = \{5, 15\}$, so $\llbracket e_2 \rrbracket = \{8,9,10,11,12,13,14,15\}$
- $e_3 = \{6, 14\}$, so $\llbracket e_3 \rrbracket = \{9,10,11,12,13,14\}$
- $e_4 = \{11, 15\}$, so $\llbracket e_4 \rrbracket = \{14,15\}$

then the partition is
$$
S = \{\{4,5,6,7\}, \{8\}, \{9,10,11,12,13\}, \{14\}, \{15\}\}.
$$

---

## 3. Pruning Edge Hypergraph

**Definition 4 (Pruning Edge Hypergraph).**
Given a set of edges $E_p = \{e_1, \ldots, e_m\}$ and a segment partition $S = \{\sigma_1, \ldots, \sigma_k\}$, we define the **hypergraph** $H = (E_p, S)$, where:
- The **vertices** are the edges $E_p$.
- For each segment $\sigma_i \in S$, there is a **hyperedge** given by

$$
\tau_i = \{e \in E_p : \sigma_i \subseteq \llbracket e \rrbracket\}.
$$

In other words, each hyperedge $\tau_i$ is the set of all edges whose intervals contain the segment $\sigma_i$.

For simplicity, we identify each hyperedge $\tau_i$ with its corresponding segment $\sigma_i$ and write $H = (E_p, S)$.

---

## 4. Vertex Cover

**Definition 5 (Vertex Cover).**
A hypergraph $H = (E_p, S)$ is **covered** by $W \subseteq E_p$ if every hyperedge (segment) in $S$ has at least one element in $W$. That is, for every $\sigma \in S$, there exists $e \in W$ such that $\sigma \subseteq \llbracket e \rrbracket$.

---

## 5. Ordered Vertex Cover

**Definition 6 (Ordered Vertex Cover).**
Given a pruning edge hypergraph $H = (E_p, S)$, a tuple $\pi = (\pi_1, \ldots, \pi_\ell)$ with $\pi_i \in E_p$ is an **ordered vertex cover** if the set $\{\pi_1, \ldots, \pi_\ell\}$ covers $H$.

**Example.**
For the hypergraph in the previous example, both $\pi = (e_1, e_2)$ and $\pi' = (e_1, e_3, e_4)$ are ordered vertex covers. However, $(e_1, e_3)$ is not an ordered cover because segment $\{15\}$ is not covered.

---

## 6. Cost of an Ordered Cover

**Definition 7 (Residual Variables and Partial Cost).**
Given an ordered tuple $\pi = (\pi_1, \ldots, \pi_\ell)$ of edges, for each $i = 1, \ldots, \ell$, define the **residual set**

$$
\Gamma(\pi_i) = \llbracket \pi_i \rrbracket \setminus \bigcup_{j < i} \llbracket \pi_j \rrbracket,
$$

i.e., the indices in $\llbracket \pi_i \rrbracket$ that have not been covered by earlier edges in the sequence.

The **partial cost** of edge $\pi_i$ is

$$
f(\pi_i) = \begin{cases}
2^{|\Gamma(\pi_i)|}, & \text{if } \Gamma(\pi_i) \neq \emptyset, \\
0, & \text{if } \Gamma(\pi_i) = \emptyset.
\end{cases}
$$

**Definition 8 (Total Ordered Covering Cost).**
The **total cost** of the ordered cover $\pi = (\pi_1, \ldots, \pi_\ell)$ is

$$
F(\pi) = \sum_{i=1}^\ell f(\pi_i).
$$

**Example.**
For $\pi = (e_1, e_2)$ with $e_1 = \{1,8\}$ and $e_2 = \{5,15\}$:
- $\Gamma(\pi_1) = \llbracket e_1 \rrbracket = \{4,5,6,7,8\}$, so $f(\pi_1) = 2^5 = 32$
- $\Gamma(\pi_2) = \llbracket e_2 \rrbracket \setminus \{4,5,6,7,8\} = \{9,10,11,12,13,14,15\}$, so $f(\pi_2) = 2^7 = 128$
- $F(\pi) = 32 + 128 = 160$

For $\hat{\pi} = (e_4, e_3, e_2, e_1)$ with $e_4 = \{11,15\}$, $e_3 = \{6,14\}$:
- $\Gamma(\hat{\pi}_1) = \{14, 15\}$, so $f(\hat{\pi}_1) = 2^2 = 4$
- $\Gamma(\hat{\pi}_2) = \{9,10,11,12,13\}$, so $f(\hat{\pi}_2) = 2^5 = 32$
- $\Gamma(\hat{\pi}_3) = \{8\}$, so $f(\hat{\pi}_3) = 2^1 = 2$
- $\Gamma(\hat{\pi}_4) = \{4,5,6,7\}$, so $f(\hat{\pi}_4) = 2^4 = 16$
- $F(\hat{\pi}) = 4 + 32 + 2 + 16 = 54$

---

## 7. The Ordered Covering Problem (OCP)

**Definition 9 (Ordered Covering Problem — Optimization Version).**
Given a set of edges $E_p$, a segment partition $S$, and the induced hypergraph $H = (E_p, S)$, the **Ordered Covering Problem (OCP)** is to find

$$
\pi^* = \arg\min_{\pi \in \Pi(H)} F(\pi),
$$

where $\Pi(H)$ is the set of all ordered vertex covers of $H$.

**Definition 10 (OCP Decision Version — OCP-DEC).**
Given a hypergraph $H = (E_p, S)$ and a budget $B \in \mathbb{N}$, decide whether there exists an ordered vertex cover $\pi$ such that $F(\pi) \leq B$.

---

## 8. General Hypergraph Formulation

The above definitions assume edge intervals from a DMDGP-induced graph. For the **general hypergraph** version (used in complexity proofs), we relax the interval structure:

**Definition 11 (General OCP).**
Given:
- A finite universe of segments $S$,
- A family of edges $E_p$ where each $e \in E_p$ has an associated covering set $\operatorname{cov}(e) \subseteq S$,
- A budget $B$,

an **ordered cover** is a tuple $\pi = (\pi_1, \ldots, \pi_\ell)$ with $\pi_i \in E_p$ such that $\bigcup_{i=1}^\ell \operatorname{cov}(\pi_i) = S$. The cost is defined analogously:

$$
\Gamma(\pi_i) = \operatorname{cov}(\pi_i) \setminus \bigcup_{j<i} \operatorname{cov}(\pi_j),
$$

$$
f(\pi_i) = \begin{cases}
2^{|\Gamma(\pi_i)|}, & \Gamma(\pi_i) \neq \emptyset, \\
0, & \Gamma(\pi_i) = \emptyset,
\end{cases}
$$

$$
F(\pi) = \sum_{i=1}^\ell f(\pi_i).
$$

The decision problem **OCP-DEC** asks: does there exist $\pi$ with $F(\pi) \leq B$?

---

## References

Souza, M., Maia, N., & Lavor, C. (2023). *The Ordered Covering Problem in Distance Geometry.* Proceedings of the conference on Distance Geometry and related topics.
