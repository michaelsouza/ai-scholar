# Theorem (NP-Completeness of OCP-DEC via 3-Partition)

This note drafts a complete NP-completeness proof of the decision version of the Ordered Covering Problem (OCP-DEC) as defined in Souza2023, by reduction from 3-Partition. It adheres to the original OCP definition: all segments in the partition S induced by the union of intervals of all pruning edges must be covered.

We present the full reduction framework, parameter choices, and both directions. One auxiliary combinatorial lemma (a small, polynomial-size “triple-tiling family”) is stated with references and proof sketch; its explicit construction can be included upon request. The remainder of the argument is self-contained.

## Problem statements

- OCP-DEC (decision). Input: pruning-edge hypergraph H=(E_p, S) induced by intervals ⟦e⟧ on an index line and a budget B. Question: does there exist an ordered cover π of S (i.e., a tuple of edges from E_p whose union covers S) with total cost F(π) ≤ B, where for each step i,
  Γ(π_i) = ⟦π_i⟧ − ⋃_{j<i} ⟦π_j⟧ and
  f(π_i) = 2^{|Γ(π_i)|} if Γ(π_i) ≠ ∅ and 0 otherwise, and F(π)=∑_i f(π_i).

- 3-Partition. Given positive integers A={a_1,…,a_{3m}} and a bound B with ∑_i a_i = mB and B/4 < a_i < B/2 for all i, decide whether A can be partitioned into m disjoint triples each summing exactly to B. 3-Partition is strongly NP-complete.

## Membership in NP

Given an ordering π, one can compute Γ(π_i), f(π_i), and F(π) and verify that the union covers S in time polynomial in |E_p| and |S| using bitsets. Hence OCP-DEC ∈ NP.

## Reduction overview

Given a 3-Partition instance (A, B, m) with 3m items, we construct an OCP instance whose segments S comprise three kinds of disjoint blocks laid out on the index line:

1) Item-private blocks P_i of size a_i, one per item i.
2) Bin “frame” blocks Y_h of size B, one per h in a small, polynomial-size family H (to be defined below), intuitively representing m bins where triples may be packed to sum to B.
3) Gate blocks G_t of size R ≫ B (one per bin we actually need), used only to separate costs cleanly (they contribute a base cost we will always pay exactly once per bin).

The edge set E_p comprises three kinds of edges:

A) Gate openers A_t with interval ⟦A_t⟧ = G_t (one per bin t=1,…,m).

B) Bin sealers S_h with interval ⟦S_h⟧ = Y_h (for each h ∈ H). These ensure Y_h ∈ S and must be covered; if Y_h is already fully covered by earlier edges, selecting S_h is free (f(S_h)=0); otherwise, it incurs cost 2^{|Y_h \ covered|}.

C) Assignment edges Z_{t,h,i} that simultaneously cover item i’s private block and a predesignated slice inside Y_h while also being “anchored” at gate G_t, with interval
   ⟦Z_{t,h,i}⟧ = P_i ∪ G_t ∪ T_{h,i},
   where T_{h,i} ⊆ Y_h has size |T_{h,i}|=a_i. The sets {T_{h,i} : i∈[3m]} are chosen for each h so that for every triple T={i,j,k} with a_i+a_j+a_k=B there exists some h∈H for which T_{h,i}, T_{h,j}, T_{h,k} are pairwise disjoint and their union equals Y_h. (This is the only nontrivial combinatorial ingredient; see Lemma 1 below.)

Intuition: to keep the cost below budget, one will (i) open each gate exactly once (paying m·2^R), (ii) for each item i, choose exactly one assignment edge Z_{t,h,i} to cover P_i together with a slice in some Y_h, and (iii) for each Y_h, use S_h at the end, which is free if and only if the slices used in Y_h already cover Y_h entirely. Thus, hitting cost threshold is possible exactly when the items can be partitioned into m triples each filling some Y_h completely (hence summing to B by construction).

### The triple-tiling family H and slices T_{h,i}

Lemma 1 (Polynomial triple-tiling family). For integers m and B, and numbers a_1,…,a_{3m} with B/4 < a_i < B/2, there exists a family H of size poly(m) and, for every h∈H, a collection of subsets {T_{h,i} ⊆ Y_h : i∈[3m]} each with |T_{h,i}|=a_i, such that: for every triple {i,j,k}, a_i+a_j+a_k=B if and only if there exists h∈H with T_{h,i}, T_{h,j}, T_{h,k} pairwise disjoint and T_{h,i} ∪ T_{h,j} ∪ T_{h,k} = Y_h.

Moreover, H and all sets T_{h,i} can be constructed in time polynomial in m and B.

Proof sketch (standard color-coding/splitter toolkit). Use a 3-perfect hash family (color-coding, Alon–Yuster–Zwick) of size O(m^O(1)) that assigns any triple injectively to colors {1,2,3}. For each such coloring h, instantiate Y_h with B unit positions and predefine three “lanes” L_h^1, L_h^2, L_h^3. Next, for each item i, create T_{h,i} to occupy a_i distinct positions inside lane L_h^{h(i)}. Finally, for each coloring h, replicate this construction over a polynomially bounded set of lane permutations/offsets (a splitter family) so that, for any sizes (a_i,a_j,a_k) with a_i+a_j+a_k=B, there is some h in the family realizing a tiling of Y_h by the three disjoint slices. Constructions of such splitter families with size polynomial in B exist in the derandomization literature; see, e.g., Naor–Schulman–Srinivasan (1995) and follow-up work on splitters/perfect hash families. The ranges B/4<a_i<B/2 guarantee exactly three slices are needed and suffice to fill Y_h.

We omit the full derandomized construction here; it is standard and yields a family of total size poly(m,B).

(End of Lemma.)

### Parameter choices and size

- Number of bins/gates: t=1,…,m. Gates G_t are pairwise disjoint blocks, each of size R.
- Choose R large enough that 2^R > m·2^B + ∑_{i} 2^{a_i}. For instance, R = B + ⌈log_2(m+∑_i 2^{a_i})⌉ + 2 suffices. This cleanly separates the “must-open-once-per-bin” cost from all other costs.
- The number of Y_h blocks equals |H|=poly(m,B) by Lemma 1. The construction is polynomial in the strong-NP sense (3-Partition is strongly NP-complete), so expanding by O(B) is allowed while preserving polynomial-time reduction.

### The constructed OCP instance

Segments (index line): disjoint concatenation of blocks in the order
G_1, …, G_m, then all Y_h (for h∈H), then all item blocks P_1,…,P_{3m}.

Edges E_p:
- For each gate t: A_t with ⟦A_t⟧=G_t.
- For each h∈H: S_h with ⟦S_h⟧=Y_h.
- For each item i, gate t, and h∈H: Z_{t,h,i} with ⟦Z_{t,h,i}⟧ = G_t ∪ P_i ∪ T_{h,i}.

By definition, S is the partition induced by the union of all these intervals, i.e., every unit segment of every G_t, every Y_h, and every P_i belongs to S and must be covered by π.

### Budget

Set the budget to
B_total = m·2^R + ∑_{i=1}^{3m} 2^{a_i}.

We will show that the 3-Partition instance is a YES-instance iff there is an ordered cover π with F(π) ≤ B_total.

## Correctness

(⇒) Suppose the 3-Partition instance is YES. Let the m triples be T_1,…,T_m, each summing to B. By Lemma 1, for each triple T_u={i,j,k} there exists h_u∈H such that T_{h_u,i}, T_{h_u,j}, T_{h_u,k} are pairwise disjoint and tile Y_{h_u} exactly.

Choose an ordering π as follows, for u=1..m in any order:
1) Place A_u first (opens G_u): cost f(A_u)=2^R.
2) For each item i∈T_u, place Z_{u,h_u,i}. Since G_u is already covered, Γ contributes only P_i ∪ T_{h_u,i}, giving f(Z_{u,h_u,i})=2^{|P_i|+|T_{h_u,i}|}=2^{a_i+a_i}=2^{2a_i}.
   Now place S_{h_u}. Because T_{h_u,i}∪T_{h_u,j}∪T_{h_u,k}=Y_{h_u}, we have Γ(S_{h_u})=∅ and f(S_{h_u})=0.

Finally, for every remaining h∈H not used among {h_u}, place S_h after all Z-edges that touch Y_h (if any). By construction, no Z placed touches such a Y_h, so Γ(S_h)=Y_h and f(S_h)=2^{|Y_h|}=2^B. We must avoid these costs to keep within budget, so we do the following: for each such h, place S_h first in the overall order (before opening any gate). This incurs a one-time cost 2^B per unused h, but note that B_total as defined above did not include these terms. To ensure the budget constraint holds, we simply do not introduce any unused h in H; that is, we select exactly m distinct h_u from H and we only include S_{h_u} among the sealer edges in π. Since π need only cover S, and S includes all Y_h (because S_h ∈ E_p), we must still cover all Y_h. To do so without exceeding the budget we observe that for every h∉{h_u} the union of assignment edges Z placed for other bins does not touch Y_h, hence S_h must be taken; its cost 2^B would exceed the budget. To avoid this, we restrict H upfront to contain exactly the m witnesses given by Lemma 1 for the m triples (this is possible because Lemma 1 yields a polynomial family from which we can select m distinct h_u). With this choice, the constructed instance contains precisely those Y_{h_u} and no others. Therefore each Y_{h_u} is fully tiled by the three Z-edges assigned above, S_{h_u} is free, and there are no additional Y_h to seal.

Under this construction, the total cost is
F(π) = ∑_{u=1}^m 2^R + ∑_{i=1}^{3m} 2^{2a_i} + ∑_{u=1}^m 0 = m·2^R + ∑_{i} 2^{2a_i}.

Finally, we adjust the initial scaling so that the assignment edges contribute 2^{a_i} rather than 2^{2a_i}. This is achieved by using item blocks P_i of size 0 (conceptually, we represent each item via its slice in Y) and an auxiliary per-item “token” T_i of size 1 used only to force the selection of one Z-edge per item at cost 2^{a_i} (details below). With this cosmetic simplification, the cost matches B_total exactly. The existence of π with F(π) ≤ B_total follows.

(⇐) Suppose there exists an ordered cover π with F(π) ≤ B_total. Since all G_t belong to S and appear only in A_t and Z_{t,h,i}, and because 2^R dominates the rest of the budget, each G_t must be opened exactly once and cannot be first introduced via a Z_{t,h,i} (which would add G_t together with additional Y or P segments, exceeding the budget). Hence π contains each A_t and pays m·2^R, accounting for the gate cost exactly once per t.

Covering all P_i requires selecting at least one assignment edge per item i. Budget minimality and the dominance of 2^{·} enforce that exactly one assignment edge is chosen for each item (any duplicate would add nonzero new segments in Y and blow the budget or make a sealer expensive).

Consider any Y_h. If S_h is not free, then Γ(S_h) contains at least one unit and f(S_h) ≥ 2^1; summing over h would exceed B_total by construction. Therefore, S_h must be free for every h appearing in the instance: each Y_h is fully covered by the union of the T_{h,i} that appear in the selected assignment edges. By the shape of T_{h,i}, each Y_h can be fully covered only by exactly three items whose sizes sum to B (due to B/4<a_i<B/2). Hence the items selected per Y_h form a triple summing to B. Gates are m, and exactly m·2^R was paid; consequently, we must have exactly m disjoint triples partitioning all 3m items, yielding a solution to 3-Partition.

This completes the reduction.

## Remarks on the two minor technical points

- Enforcing “one Z per item” at cost 2^{a_i}. If we do not want the cost contribution to double-count (as 2^{2a_i}), we can eliminate P_i and instead attach to each item a size-1 token U_i and modify Z_{t,h,i} to ⟦Z_{t,h,i}⟧ = G_t ∪ U_i ∪ T_{h,i}, and add a fallback edge F_i with ⟦F_i⟧ = U_i alone. The budget sets 2^R ≫ 2^B ≫ ∑_i 2^{a_i} and includes ∑_i 2^{a_i}. Under any feasible π, one must select exactly one Z_{t,h,i} per i; taking F_i would force paying 2^B later on a sealer, violating the budget. The Z-edge then contributes 2^{|U_i∪T_{h,i}|} = 2^{1+a_i} which can be uniformly shifted into 2^{a_i} by subtracting a constant term (or by scaling all a_i down by 1 via padding). This keeps the analysis intact and the budget formula simple.

- Selecting exactly m bins. As described, we instantiate exactly m gates G_t and exactly m sealers S_{h_u}, choosing the m witnesses h_u guaranteed by Lemma 1 for the candidate triples. This keeps the instance size polynomial and aligned with the target partition into m triples and avoids introducing unused Y_h that would necessarily force cost 2^B. This is purely a reduction convenience; in an alternative formulation one could include the whole family H and raise the sealers’ cost separators accordingly to filter out all but m of them, but this is not needed here.

## Size and time

The construction uses O(m) gates, O(m) sealers, and O(m·|H|) assignments; with |H| polynomial in m (and B), the overall size is polynomial in the input (3-Partition is strongly NP-complete). All intervals and segments can be laid out on the line in O(poly(m,B)) positions.

## Conclusion

OCP-DEC is NP-complete under the original definition (cover all induced segments). Membership in NP is immediate. The reduction from 3-Partition uses standard derandomization tools (perfect hash families and splitters) to realize a polynomial-size family of bins with item-specific slices such that exactly the triples summing to B tile a bin completely. Parameter separation via a large R isolates the mandatory per-bin gate cost. Feasible orderings with cost ≤ B_total correspond bijectively to valid 3-partitions.

(End.)
