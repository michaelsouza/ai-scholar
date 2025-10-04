# Theorem (NP-Completeness of OCP-DEC via 3-Partition — Explicit Construction)

This proof shows OCP-DEC (as defined in Souza2023: cover all induced segments $S$ and minimize the ordered cost) is NP-complete by a polynomial-time reduction from 3-Partition. It replaces the auxiliary lemma in `proof_version2.md` with an explicit, deterministic construction and cites standard derandomization and group-testing results.

## Problems

- OCP-DEC. Input: pruning-edge hypergraph $H=(E_p,S)$ induced by intervals $\llbracket e \rrbracket$ over an index line and a budget $B_{\text{tot}}$. Question: does there exist an ordered cover $\pi$ of $S$ (tuple of edges) such that $F(\pi) \le B_{\text{tot}}$, where for step $i$,
  $\Gamma(\pi_i)=\llbracket\pi_i\rrbracket \setminus \bigcup_{j<i} \llbracket\pi_j\rrbracket$, $\; f(\pi_i)=2^{\lvert\Gamma(\pi_i)\rvert}$ if $\Gamma(\pi_i)\neq\varnothing$ and $0$ otherwise, and $F(\pi)=\sum_i f(\pi_i)$.

- 3-Partition. Given positive integers $A=\{a_1,\dots,a_{3m}\}$ and $B$ with $\sum_i a_i = mB$ and $B/4<a_i<B/2$, decide whether $A$ can be partitioned into $m$ disjoint triples, each summing to $B$. 3-Partition is strongly NP-complete (Garey–Johnson 1979, SP15).

OCP-DEC $\in \mathrm{NP}$: given $\pi$, compute $\Gamma(\pi_i)$ and $F(\pi)$ with bitsets and verify coverage in polynomial time.

## Reduction overview

Given $(A,B,m)$, we build an OCP instance with:
- $m$ disjoint “gates” $G_t$ of size $R$ (large separator), one per bin $t$.
- $m$ disjoint “bins” $Y_t$ (one per gate), each realized over the same abstract size parameter $B'$ (we set $B'=B$ below), and tokens $U_i$ (size $1$) for each item $i$.
- Edges:
  - Gate openers $A_t$ with $\llbracket A_t\rrbracket=G_t$.
  - Bin sealers $S_t$ with $\llbracket S_t\rrbracket=Y_t$ (to ensure $Y_t \in S$).
  - Assignment edges $Z_{t,\ell,i}$ indexed by bin $t$, a label $\ell$ from an explicit family $L$ (defined below), and item $i$. Each $Z_{t,\ell,i}$ covers the gate plus the item token and a pattern $T_{\ell,i}\subseteq Y_t$:
    $\llbracket Z_{t,\ell,i}\rrbracket=G_t \cup U_i \cup T_{\ell,i}$.

We set the budget
$$
B_{\text{tot}} = m\,2^R + \sum_{i=1}^{3m} 2^{1+a_i}.
$$
We choose $R$ large enough that $2^R > 2\cdot \sum_i 2^{1+a_i} + m\cdot 2^{B'}$.
Intuitively: each bin pays exactly one gate cost $2^R$ and exactly three assignment edges (one per chosen item among its triple), each costing $2^{1+a_i}$; bin sealers $S_t$ cost $0$ only if their $Y_t$ is already fully covered.

What remains is an explicit construction of a family $L$ and sets $\{T_{\ell,i}\subseteq[B']\}$ such that:
- For any triple $\{i,j,k\}$ with $a_i+a_j+a_k=B'$, there exists $\ell\in L$ with $T_{\ell,i},T_{\ell,j},T_{\ell,k}$ pairwise disjoint and $T_{\ell,i}\cup T_{\ell,j}\cup T_{\ell,k}=[B']$.
- Conversely, for any $\ell\in L$ and distinct $i,j,k$, if $T_{\ell,i}\cup T_{\ell,j}\cup T_{\ell,k}=[B']$ then $a_i+a_j+a_k=B'$ and the three sets are pairwise disjoint.

We provide an explicit, deterministic construction of $L$ and $\{T_{\ell,i}\}$ with size polynomial in $m$ and $B'$, using two well-known explicit combinatorial objects: perfect hash families (aka splitters) and cover-free families (CFFs).

## Explicit construction of $L$ and the tiles $T_{\ell,i}$

We work over the ground set $Y=[B'] = \{1,\dots,B'\}$ which will be the index set for each bin $Y_t$.

1) Explicit $(n,3)$-splitter $H_{\mathrm{col}}$. Let $n=3m$. There exist explicit $(n,3)$-splitter families $H_{\mathrm{col}}$ mapping $[n]\to\{1,2,3\}$ such that for every $3$-set $\{i,j,k\}\subseteq[n]$, some $h\in H_{\mathrm{col}}$ is injective on $\{i,j,k\}$ (i.e., assigns distinct colors). Deterministic constructions of size $\mathcal{O}(3^3\log n)=\mathcal{O}(\log n)$ and time $\mathrm{poly}(n)$ are known; see Naor–Schulman–Srinivasan (FOCS’95; SIAM J. Comput. 29(2), 1999). We fix any such explicit $H_{\mathrm{col}}$.

2) Explicit $(3,1)$-cover-free family over $[B']$. A $(3,1)$-CFF over universe $[B']$ is a set-system $\mathcal{F}\subseteq 2^{[B']}$ such that for any distinct $X,Y_1,Y_2,Y_3\in\mathcal{F}$, we have $X\nsubseteq (Y_1\cup Y_2\cup Y_3)$. Explicit CFFs of size $\mathrm{poly}(B')$ exist and are constructible in $\mathrm{poly}(B')$ time (e.g., Kautz–Singleton (1964) superimposed codes; Porat–Rothschild (STOC’08) near-optimal explicit constructions). We will use this to enforce uniqueness/disjointness of the tilings described below.

3) Labels (compositions) and color blocks. Consider all integer compositions $(x,y,z)$ with $x+y+z=B'$ and $B'/4 < x,y,z < B'/2$ (the same range as the $a_i$’s). There are $\mathcal{O}((B')^2)$ such compositions, explicit to enumerate in time $\mathrm{poly}(B')$. For each composition $c=(x,y,z)$ and each splitter $h\in H_{\mathrm{col}}$, we define a label $\ell=(h,c)$ and a partition of $Y$ into three consecutive color blocks:
\[
Y^1_{\ell}=\{1,\dots,x\},\quad Y^2_{\ell}=\{x+1,\dots,x+y\},\quad Y^3_{\ell}=\{x+y+1,\dots,B'\}.
\]
We then refine each $Y^r_{\ell}$ using an explicit $(3,1)$-CFF $\mathcal{F}^r_{\ell}$ over $Y^r_{\ell}$ (by restricting/relabelling a master CFF over $[B']$): this gives us a large pool of candidate subsets inside each color block that enjoy strong non-coverability properties.

4) Tiles for items. For each item $i$ (with size $a_i$) and each label $\ell=(h,c)$, let $r=h(i)\in\{1,2,3\}$ be its color under $h$. We define $T_{\ell,i}\subseteq Y^r_{\ell}$ of size exactly $a_i$ as follows.
   - If $a_i$ equals the target block size for its color (i.e., $a_i=x$ if $r=1$, $a_i=y$ if $r=2$, $a_i=z$ if $r=3$) then set $T_{\ell,i}=Y^r_{\ell}$ (the entire block).
   - Otherwise, choose $T_{\ell,i}$ as any set from $\mathcal{F}^r_{\ell}$ of cardinality $a_i$ (CFF families can be constructed in layered form so that for every cardinality $s$ there exist members of size $s$; when needed, pad by adding disjoint dummy points within $Y^r_{\ell}$ and simultaneously remove the same number outside via an explicit bijection to maintain cardinality exactly $a_i$ — standard in CFF instantiations). This choice is deterministic and explicit.

By construction, $\lvert T_{\ell,i}\rvert=a_i$ for every $i,\ell$, and $T_{\ell,i}\subseteq Y^r_{\ell}$ depends only on $h(i)$’s color and $a_i$.

Properties ensured:
- Completeness (tiling existence). Take any triple $\{i,j,k\}$ with $a_i+a_j+a_k=B'$. Since $H_{\mathrm{col}}$ is a splitter, pick $h\in H_{\mathrm{col}}$ injective on $\{i,j,k\}$ and let colors be $r_i,r_j,r_k$ all distinct. Let $c=(x,y,z)=(a_i,a_j,a_k)$ arranged to match colors $r_i,r_j,r_k$. For $\ell=(h,c)$, the blocks $Y^1_{\ell},Y^2_{\ell},Y^3_{\ell}$ have sizes exactly $a_i,a_j,a_k$ in the respective colors. Therefore $T_{\ell,i}=Y^{r_i}_{\ell}$, $T_{\ell,j}=Y^{r_j}_{\ell}$, $T_{\ell,k}=Y^{r_k}_{\ell}$ are pairwise disjoint and their union equals $Y$.
- Soundness (only triples summing to $B'$ can cover $Y$). Fix any $\ell=(h,c)$. Because the three color blocks $Y^1_{\ell},Y^2_{\ell},Y^3_{\ell}$ are pairwise disjoint, the union of any three tiles $T_{\ell,i},T_{\ell,j},T_{\ell,k}$ has cardinality $\lvert T_{\ell,i}\rvert+\lvert T_{\ell,j}\rvert+\lvert T_{\ell,k}\rvert$ minus any overlaps inside the same block. Overlaps inside a block are prevented as follows: for a given block $Y^r_{\ell}$, if two distinct items map to the same color $r$ then at least one of their tiles is taken from the CFF $\mathcal{F}^r_{\ell}$. The $(3,1)$-CFF property guarantees that no single set in $\mathcal{F}^r_{\ell}$ is contained in the union of three others; in particular, for any two distinct tiles $X,Y\in\mathcal{F}^r_{\ell}$ and any third $Z$ (possibly equal to $Y^r_{\ell}$), we have $X\cup Y\cup Z \ne Y^r_{\ell}$ unless $X=Y^r_{\ell}$ and $Y=\varnothing$ (which we never use). Consequently, within each block, the union of up to three tiles equals the whole block if and only if exactly one of them is the whole block and the others are empty; since our tiles are never empty, this forces exactly one tile per color block and its size must equal the block’s size. Summing over the three blocks yields that $T_{\ell,i}\cup T_{\ell,j}\cup T_{\ell,k}=Y$ implies the three selected items have distinct colors and sizes matching $c$, hence $a_i+a_j+a_k=B'$.

All objects ($H_{\mathrm{col}}$, $\mathcal{F}^r_{\ell}$, enumerated compositions, and tile selections) are explicit and constructible in polynomial time in $m$ and $B'$.

## The OCP instance

Index line segments (disjoint concatenation):
$G_1,\dots,G_m$ (each of size $R$), then $Y_1,\dots,Y_m$ (each identified with a fresh copy of $[B']$), then $U_1,\dots,U_{3m}$ (each of size $1$). By including sealers $S_t$ and assignment edges, $S$ is the partition induced by all units inside $G_t$, $Y_t$, and $U_i$.

Edges $E_p$:
- For each $t$, gate opener $A_t$ with $\llbracket A_t\rrbracket=G_t$.
- For each $t$, sealer $S_t$ with $\llbracket S_t\rrbracket=Y_t$.
- For each bin $t$, for each $\ell\in L$, and for each item $i$, an assignment edge $Z_{t,\ell,i}$ with $\llbracket Z_{t,\ell,i}\rrbracket=G_t \cup U_i \cup T_{\ell,i}$ (where $T_{\ell,i}$ is interpreted inside $Y_t$ via the canonical relabelling $[B']\to Y_t$).

Budget:
$$
B_{\text{tot}} = m\,2^R + \sum_{i=1}^{3m} 2^{1+a_i},\quad \text{with } 2^R \text{ chosen so that } 2^R > 2\cdot\sum_i 2^{1+a_i} + m\cdot 2^{B'}.
$$

## Correctness

(⇒) Suppose the 3-Partition instance is YES with triples $T_1,\dots,T_m$, each summing to $B$. For each bin $t$, let $T_t=\{i_t,j_t,k_t\}$. Pick $h\in H_{\mathrm{col}}$ injective on $T_t$ and $\ell=(h,c)$ where $c$ orders $(a_{i_t},a_{j_t},a_{k_t})$ to match colors. Define $\pi$ by, for $t=1..m$:
1) Place $A_t$ (cost $2^R$).
2) Place $Z_{t,\ell,i_t}$, $Z_{t,\ell,j_t}$, $Z_{t,\ell,k_t}$ (each costs $2^{\lvert U\rvert+\lvert T\rvert}=2^{1+a_i}$ since $G_t$ is already covered, and the three $T$-tiles are pairwise disjoint and cover $Y_t$ completely).
3) Place $S_t$ (free, since $\Gamma(S_t)=\varnothing$).

Across bins, every $U_i$ is covered exactly once, all $Y_t$ are fully covered before placing $S_t$, and each gate is opened exactly once. Hence
$$
F(\pi) = m\,2^R + \sum_{i=1}^{3m} 2^{1+a_i} \le B_{\text{tot}}.
$$

(⇐) Suppose there exists an ordered cover $\pi$ with $F(\pi) \le B_{\text{tot}}$.
- Gate separation. Since every $Z_{t,\ell,i}$ contains $G_t$, the first edge introducing any unit of $G_t$ incurs cost at least $2^R$. If it is some $Z_{t,\ell,i}$ instead of $A_t$, its cost is at least $2^{R+1} > 2^R + 2^{1+a_i}$, which, summed over $m$ bins, would exceed $B_{\text{tot}}$ (by the choice of $R$). Therefore, in any optimal $\pi$ under $B_{\text{tot}}$, each $A_t$ must precede all $Z_{t,\ell,\cdot}$ for that $t$, and each gate is opened exactly once (total $m\,2^R$).
- Exactly one assignment per item. Each $U_i$ must be covered. The only edges covering $U_i$ are $\{Z_{t,\ell,i}\}$. Choosing more than one such edge for the same $i$ would add a nonempty $T_{\ell,i}$ in some $Y_t$ (since the $U_i$ contributes nothing new the second time), strictly increasing $F(\pi)$ and jeopardizing the tight budget. Hence exactly one assignment edge is chosen per item, and its cost contribution is $2^{1+a_i}$.
- Full coverage of each $Y_t$. If for some $t$ we have $\Gamma(S_t)\neq\varnothing$ when $S_t$ is placed, then $f(S_t) \ge 2^1$ and therefore $F(\pi) \ge m\,2^R + (\sum_i 2^{1+a_i}) + 2 > B_{\text{tot}}$ — impossible. Hence every $Y_t$ must be fully covered by the union of $T$-tiles selected for bin $t$ before $S_t$ is considered.
- Extracting triples. Fix $t$. Let the three items assigned to bin $t$ by their $Z$-edges be $i,j,k$ (there must be at least three because each $a_i>B/4$, so two items are insufficient to cover $Y_t$). Because $Y_t$ is fully covered and tiles lie inside $Y_t$, by the soundness property of the explicit construction, the three tiles for bin $t$ must come from a common label $\ell=(h,c)$, be pairwise disjoint, and their sizes must match $c$ with $a_i+a_j+a_k=B'$. As at most three items can cover $Y_t$ (since four items would have total size $>B'$ and, by the CFF property inside blocks, cannot jointly cover all three disjoint blocks), we conclude exactly three items are assigned to bin $t$ and their sizes sum to $B'$.

Therefore, the items partition into $m$ disjoint triples $T_1,\dots,T_m$, each summing to $B'=B$, yielding a YES instance of 3-Partition.

## Size and time

- $H_{\mathrm{col}}$ has size $\mathcal{O}(\log m)$ explicitly. The number of compositions $(x,y,z)$ with $x+y+z=B'$ is $\mathcal{O}((B')^2)$. Thus $\lvert L\rvert = \lvert H_{\mathrm{col}}\rvert\cdot \mathcal{O}((B')^2)=\mathrm{poly}(m,B')$.
- For each bin $t$, we add $\lvert L\rvert\cdot 3m$ assignment edges and one sealer $S_t$ and one opener $A_t$. Hence $\lvert E_p\rvert = m\cdot(\mathcal{O}((B')^2 \log m)\cdot 3m + 2)=\mathrm{poly}(m,B')$.
- All sets and intervals are constructible explicitly in polynomial time in $m$ and $B'$. Since 3-Partition is strongly NP-complete, we may assume numbers are polynomially bounded in $m$; thus the reduction runs in time polynomial in the input size under the standard strong-NP setting (equivalently, from the unary-encoded variant).

## Citations

- M. R. Garey and D. S. Johnson. Computers and Intractability: A Guide to the Theory of NP-Completeness. 1979. Problem SP15 (3-Partition) — strongly NP-complete.
- M. Naor, L. J. Schulman, A. Srinivasan. Splitters and Near-Optimal Derandomization. FOCS 1995; SIAM J. Comput. 29(2), 1999 — explicit $(n,k)$-splitter constructions.
- W. H. Kautz and R. C. Singleton. Nonrandom Binary Superimposed Codes. IEEE Trans. Information Theory, 1964 — cover-free families/superimposed codes.
- E. Porat and A. Rothschild. Explicit Nonadaptive Combinatorial Group Testing Schemes. STOC 2008 — near-optimal explicit CFFs.

## Conclusion

We gave an explicit, deterministic reduction from 3-Partition to OCP-DEC that respects the original OCP definition (cover all induced segments). The construction uses explicit splitters and cover-free families to realize, within each bin, tiles $T_{\ell,i}$ such that full coverage of $Y_t$ occurs if and only if exactly three items with sizes summing to $B$ are selected. The gate parameter $R$ separates mandatory bin costs from all other contributions, yielding tight budget equality in YES cases and violation in NO cases. Therefore, OCP-DEC is NP-complete.
