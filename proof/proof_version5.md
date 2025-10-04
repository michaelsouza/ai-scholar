# Theorem (NP-Completeness of OCP-DEC on General Hypergraphs)

This note proves that the decision version of the Ordered Covering Problem (OCP-DEC) is NP-complete when the instance is a general set system (i.e., not restricted to DMDGP-induced contiguous intervals). The cost model and “ordered cover” semantics are exactly those in Souza2023, and the only change is that the covering sets are arbitrary subsets of the segment universe.

We give a direct, explicit polynomial-time reduction from 3-Partition. No contiguity or geometric constraints are used.

## Problem definition (generalized OCP)

- Instance: a finite universe of segments `S`, a finite family of covering sets `E_p` where each edge `e ∈ E_p` induces a subset `cov(e) ⊆ S`, and a budget `B`.
- Ordered cover and cost: for an ordered tuple `π=(π_1, …, π_k)` with each `π_i ∈ E_p`, define
  \[
  \Gamma(\pi_i) \;=\; \operatorname{cov}(\pi_i)\setminus \bigcup_{j<i} \operatorname{cov}(\pi_j),\qquad
  f(\pi_i) \;=\; \begin{cases}
  2^{\lvert\Gamma(\pi_i)\rvert}, & \Gamma(\pi_i)\neq\varnothing,\\[2pt]
  0, & \Gamma(\pi_i)=\varnothing,
  \end{cases}
  \quad F(\pi)=\sum_i f(\pi_i).
  \]
- Decision question (OCP-DEC): does there exist an ordered tuple `π` such that `⋃_i cov(π_i) = S` and `F(π) ≤ B`?

Membership in NP is immediate: given `π`, we can compute each `Γ(π_i)`, the sum `F(π)`, and verify coverage using bitsets in time polynomial in `|E_p|·|S|`. We may assume w.l.o.g. that `π` contains each edge at most once and no 0-increment edges (drop repeats and edges with `Γ(π_i)=∅`); thus `|π| ≤ |E_p|` and the certificate is polynomially bounded.

## 3-Partition

3-Partition is strongly NP-complete. The input is a multiset of integers `A={a_1,…,a_{3m}}` and a bound `B` such that `\sum_i a_i = mB` and `B/4 < a_i < B/2` for all `i`. The question is whether `A` can be partitioned into `m` disjoint triples each summing exactly to `B`.

We reduce from 3-Partition under the standard strong NP-completeness setting where `B` is polynomially bounded in `m` (equivalently, unary encoding is allowed). Our construction is polynomial in `m` and `B`.

## Reduction

Given a 3-Partition instance `(A,B,m)`, construct an OCP instance `(S,E_p,B_\text{tot})` as follows.

- Segments:
  - Item tokens: for each item `i∈{1,…,3m}`, add a single segment `τ_i`.
  - Bins: for each bin `t∈{1,…,m}` add a bin body `Y_t` consisting of exactly `B` segments, and a gate block `G_t` of `R` segments (a large separator; `R` is fixed later).
  - Disjointness: tokens `{τ_i}` are pairwise disjoint and disjoint from all `Y_t` and `G_t`; the bin bodies `{Y_t}` are pairwise disjoint; the gates `{G_t}` are pairwise disjoint and disjoint from all `Y_t`.

- Edges:
  - Gate opener `A_t`: `cov(A_t) = G_t` (one per bin).
  - Assignment edges: for each bin `t` and for each triple `ℓ={i,j,k}` with `a_i+a_j+a_k=B`, add three edges that partition `Y_t`:
    \[
    Z_{t,ℓ,i}: \quad \operatorname{cov}(Z_{t,ℓ,i}) = G_t \;\cup\; T_{t,ℓ,i} \;\cup\;\{τ_i\},\quad \lvert T_{t,ℓ,i}\rvert=a_i;\\
    Z_{t,ℓ,j}: \quad \operatorname{cov}(Z_{t,ℓ,j}) = G_t \;\cup\; T_{t,ℓ,j} \;\cup\;\{τ_j\},\quad \lvert T_{t,ℓ, j}\rvert=a_j;\\
    Z_{t,ℓ,k}: \quad \operatorname{cov}(Z_{t,ℓ,k}) = G_t \;\cup\; T_{t,ℓ,k} \;\cup\;\{τ_k\},\quad \lvert T_{t,ℓ, k}\rvert=a_k;\\
    \]
    where, for this fixed `t` and `ℓ`, the three tile sets `T_{t,ℓ,i}, T_{t,ℓ,j}, T_{t,ℓ,k}` are pairwise disjoint and form a partition of `Y_t` (their union equals `Y_t`). Across different `ℓ`, tile sets may overlap.

- Budget:
  \[
  B_\text{tot} \;=\; m\,2^R \; + \; \sum_{i=1}^{3m} 2^{\,1+a_i}.
  \]
  Choose `R` so that
  \[
  2^R \;>\; 2\,\sum_{i=1}^{3m} 2^{\,1+a_i} \; + \; m\,2^{\,B}.
  \]
  This choice is possible with `R = \mathcal O(B + \log m + \log \sum_i 2^{1+a_i})`.

Intuition.
- Opening a bin (first coverage of `G_t`) costs `2^R` once; paying this via `A_t` is cheapest. Paying it through an assignment edge first would cost `2^{R+1+a_i}` which is far larger than `2^R + 2^{1+a_i}` (by the choice of `R`).
- Covering each item token `τ_i` exactly once costs `2^{1+a_i}` via its unique assignment edge (after the gate is open). Reusing the same item in a second bin would add an extra `2^{a_i}` (since the token is already covered), exceeding budget.

### Correctness

We prove that the 3-Partition instance is a YES-instance iff the constructed OCP-DEC instance admits an ordered cover `π` with `F(π) ≤ B_\text{tot}`.

Lemma 1 (Gate discipline). In any `π` with `F(π) ≤ B_\text{tot}`, for each bin `t`, the first edge touching `G_t` must be `A_t`. Moreover, exactly one such opener per bin is used.

Proof. If `Z_{t,ℓ,i}` is the first edge to cover any element of `G_t`, then the increment includes `R + (1+a_i)` fresh segments, so its cost is `2^{R+1+a_i}`. Replacing that move by opening with `A_t` first (cost `2^R`) and applying `Z_{t,ℓ,i}` later (cost `2^{1+a_i}`) strictly reduces the total (by the choice of `R`). Thus any solution with `F(π) ≤ B_\text{tot}` must open via `A_t` first. Since `G_t` is already fully covered after `A_t`, subsequent openers add `0`; using more than one opener per bin is never beneficial, and we can w.l.o.g. assume exactly one opener per bin. ∎

Lemma 2 (Each item used exactly once). In any `π` with `F(π) ≤ B_\text{tot}`, for every item `i`, exactly one assignment edge among `{Z_{t,ℓ,i}}` appears.

Proof. The only edges covering `τ_i` are the assignments `{Z_{t,ℓ,i}}`. If none is chosen, `τ_i` remains uncovered, contradicting feasibility. If two or more are chosen, the first contributes `2^{1+a_i}` (after the gate is open), and each additional one contributes at least `2^{a_i}` (the token is already covered and `G_t` is already open) on some bin (tile sets lie inside disjoint `Y_t`). Since the budget already exactly sums `\sum_i 2^{1+a_i}`, any extra `2^{a_i}>0` violates `F(π) ≤ B_\text{tot}`. ∎

Lemma 3 (Full coverage of each bin). In any feasible `π`, for every bin `t`, `Y_t` is fully covered.

Proof. Feasibility requires `⋃_i cov(π_i) = S`, which contains all segments in every `Y_t`. The only edges that cover elements of `Y_t` are the assignment edges for bin `t`, hence their union over `π` must equal `Y_t`. ∎

Lemma 4 (Exactly three items per bin, summing to `B`). In any `π` with `F(π) ≤ B_\text{tot}`, each bin `t` receives exactly three items whose sizes sum to `B`.

Proof. By Lemma 2, each item `i` is assigned to exactly one bin, and by Lemma 3 the `m` bins’ bodies are fully covered. The bin bodies are pairwise disjoint and have total size `mB`. The assignment edges add exactly `\sum_i a_i = mB` body segments across all bins (token and gate portions are disjoint). Hence there is no overlap between tile contributions within each bin, and the contributions to bin `t` sum exactly to `B`. Because `B/4<a_i<B/2`, it is only possible for the sum to be `B` if each bin gets exactly three items. ∎

Lemma 5 (Triples come from the allowed list). For each bin `t`, the three items placed in `t` form some triple `ℓ={i,j,k}` with `a_i+a_j+a_k=B`.

Proof. By Lemma 4, the three items’ sizes sum to `B`. By construction, the edge family includes assignment edges for every triple `ℓ` with sum `B`. If the chosen three assignments for bin `t` happen to come from different labels, we can replace them, w.l.o.g. and without changing costs or coverage, by the three assignment edges indexed by the triple `ℓ={i,j,k}` that exactly partitions `Y_t` (the bodies and tokens touched are the same sizes; costs depend only on `a_i`). Thus we obtain a solution that uses one triple label per bin. ∎

We now conclude both directions.

- (⇒) If the 3-Partition instance is a YES-instance, fix a partition into `m` disjoint triples `ℓ_t={i_t,j_t,k_t}`. For each bin `t`, order `A_t` first, then place `Z_{t,ℓ_t,i_t}, Z_{t,ℓ_t,j_t}, Z_{t,ℓ_t,k_t}`. This covers all segments. Each bin contributes `2^R + 2^{1+a_{i_t}} + 2^{1+a_{j_t}} + 2^{1+a_{k_t}}`, so the total equals `B_\text{tot}`.

- (⇐) If there is an ordered cover `π` with `F(π) ≤ B_\text{tot}`, by Lemmas 1–5 each bin contains exactly one triple `ℓ_t` and the `m` chosen triples are pairwise disjoint and cover all `3m` items. Hence they yield a valid 3-Partition of `A`.

Therefore, OCP-DEC is NP-hard. Combined with membership in NP, OCP-DEC is NP-complete on general hypergraphs. ∎

## Size and time bounds

- Number of segments: `|S| = (3m) + mB + mR = \mathcal O(m(B+R))`.
- Edges: `m` openers `A_t`, and for each bin `t` and for each triple `ℓ` with sum `B` (at most `\binom{3m}{3} = \mathcal O(m^3)`), exactly 3 assignment edges. Hence `|E_p| = \mathcal O(m^4)`.
- Construction time: enumerate all triples with sum `B` in `\mathcal O(m^3)` time and instantiate the corresponding sets; overall time is polynomial in `m` and `B`.
- Parameter choice: choose `R = \Theta(B + \log m + \log \sum_i 2^{1+a_i})`, which is polynomial in the input size under the standard strongly-NP-hard 3-Partition setting (e.g., unary encoding or bounded `B`).

## Remarks

- This result isolates the source of hardness in the ordered-cost objective itself: the instance uses arbitrary set systems and does not rely on interval geometry. When OCP instances are constrained to come from DMDGP-induced contiguous intervals (as in Souza2023), additional structural work is needed to carry hardness through.
- The reduction uses only basic gadgets (gates, tokens, bin bodies) and an explicit enumerator of valid triples; no derandomization or cover-free-family machinery is required in the general-hypergraph setting.
