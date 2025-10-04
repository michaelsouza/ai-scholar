# Lean 4 Quickstart Guide
## Concepts and Features Used in OCP-DEC Formalization

This document explains the Lean 4 concepts and features used in the NP-completeness proof formalization of the Ordered Covering Problem (OCP-DEC) found in `proof/proof_version5.lean`.

---

## Table of Contents

1. [Basic Type System](#basic-type-system)
2. [Structures](#structures)
3. [Inductive Types](#inductive-types)
4. [Functions and Definitions](#functions-and-definitions)
5. [Propositions and Proofs](#propositions-and-proofs)
6. [Namespaces](#namespaces)
7. [Dependent Types](#dependent-types)
8. [Pattern Matching](#pattern-matching)
9. [Mathlib Integration](#mathlib-integration)
10. [Proof Tactics](#proof-tactics)

---

## Basic Type System

Lean 4 is a dependently-typed functional programming language and theorem prover. Every expression has a type.

### Type Aliases

```lean
def Segment := ℕ
def Edge := ℕ
```

**Purpose**: Creates type aliases for natural numbers to represent segments and edges. This improves code readability while maintaining type safety.

**Usage in OCP proof**: Distinguishes between segment identifiers and edge identifiers even though both are implemented as natural numbers.

---

## Structures

Structures are Lean's way to define records with named fields.

### Basic Structure

```lean
structure SegmentUniverse where
  segments : Finset Segment
```

**Components**:
- `structure` keyword defines a new type
- `where` introduces the fields
- Each field has a name and type

**Usage in OCP proof**:
- `SegmentUniverse`: Encapsulates the universe of segments
- `CoveringFunction`: Stores edges and their covering function
- `OCP_DEC`: The complete problem instance with segments, covering function, and budget

### Structures with Constraints

```lean
structure ThreePartition where
  m : ℕ
  B : ℕ
  items : Fin (3 * m) → ℕ
  sum_constraint : (Finset.univ.sum items) = m * B
  size_bounds : ∀ i, B / 4 < items i ∧ items i < B / 2
```

**Key feature**: Fields can be propositions (proofs) that constrain other fields.

**Usage in OCP proof**: Encodes the 3-Partition problem with its mathematical constraints as part of the type definition.

---

## Inductive Types

Inductive types define data structures by their constructors (similar to algebraic data types in functional programming or enums in Rust).

### Basic Inductive Type

```lean
inductive SegmentType
  | ItemToken : Fin (3 * tp.m) → SegmentType
  | BinBody : Fin tp.m → Fin tp.B → SegmentType
  | Gate : Fin tp.m → Fin (gateSize tp) → SegmentType
```

**Components**:
- Each `|` introduces a constructor
- Constructors can take parameters
- The type name appears after the `:`

**Usage in OCP proof**: Represents the three types of segments in the reduction construction (item tokens, bin body segments, gate segments).

### Pattern Matching on Inductive Types

```lean
match pos with
| ⟨0, _⟩ => triple.1
| ⟨1, _⟩ => triple.2.1
| ⟨2, _⟩ => triple.2.2
| _ => triple.1
```

**Usage in OCP proof**: Extracts the i-th, j-th, or k-th element from a triple based on position.

---

## Functions and Definitions

### Simple Definitions

```lean
def OrderedCover := List Edge
```

**Purpose**: Type synonym for ordered covers (sequences of edges).

### Functions with Parameters

```lean
def residual (π : OrderedCover) (i : ℕ) : Finset Segment :=
  if h : i < π.length then
    let πᵢ := π.get ⟨i, h⟩
    let already_covered := (List.take i π).foldl
      (fun acc e => acc ∪ E.cov e) ∅
    E.cov πᵢ \ already_covered
  else
    ∅
```

**Key features**:
- **Dependent if**: `if h : condition` binds proof `h` that the condition holds
- **Let bindings**: `let x := expr` introduces local definitions
- **Anonymous functions**: `fun acc e => ...` (lambda expressions)
- **Unicode symbols**: `∅` for empty set, `∪` for union, `\` for set difference

**Usage in OCP proof**: Computes the residual (newly covered) segments when adding edge i to the ordered cover.

### Recursive Definitions

```lean
def totalCost (π : OrderedCover) : ℕ :=
  (List.range π.length).foldl (fun acc i => acc + edgeCost S E π i) 0
```

**Usage in OCP proof**: Computes total cost by folding over all edges in the ordered cover.

---

## Propositions and Proofs

In Lean, propositions are types and proofs are terms of those types (Curry-Howard correspondence).

### Predicates as Propositions

```lean
def isFeasible (π : OrderedCover) : Prop :=
  S.segments ⊆ π.foldl (fun acc e => acc ∪ E.cov e) ∅
```

**Key points**:
- Return type is `Prop` (the type of propositions)
- `⊆` is the subset relation
- This is a predicate on ordered covers

### Existential Propositions

```lean
def OCP_DEC.hasValidCover (instance : OCP_DEC) : Prop :=
  ∃ π : OrderedCover,
    isFeasible instance.segments instance.covering π ∧
    totalCost instance.segments instance.covering π ≤ instance.budget
```

**Components**:
- `∃` is existential quantification ("there exists")
- `∧` is conjunction ("and")
- `≤` is less-than-or-equal

### Universal Quantification

```lean
size_bounds : ∀ i, B / 4 < items i ∧ items i < B / 2
```

**Components**:
- `∀` means "for all"
- Expresses that all items satisfy the size constraint

---

## Namespaces

Namespaces organize code and prevent name collisions.

```lean
namespace OCP

variable (S : SegmentUniverse) (E : CoveringFunction)

def residual (π : OrderedCover) (i : ℕ) : Finset Segment := ...

end OCP
```

**Features**:
- `namespace Name` ... `end Name` creates a namespace
- `variable` declares parameters available to all definitions in the namespace
- Definitions can be accessed as `OCP.residual` from outside the namespace

**Usage in OCP proof**: Separates OCP definitions from reduction construction and correctness lemmas.

---

## Dependent Types

Dependent types are types that depend on values.

### Fin Type (Finite Sets)

```lean
Fin n := { i : ℕ // i < n }
```

**Meaning**: Natural numbers less than `n`, with the constraint built into the type.

**Usage examples**:
- `Fin (3 * m)`: Exactly 3m items
- `Fin tp.m`: Exactly m bins
- `Fin 3`: Positions in a triple (0, 1, 2)

### Dependent Functions

```lean
items : Fin (3 * m) → ℕ
```

**Meaning**: A function from finite set of size 3m to natural numbers. The domain size depends on the value `m`.

**Usage in OCP proof**: Represents item sizes where the number of items depends on the number of bins.

---

## Pattern Matching

### Match Expressions

```lean
match pos with
| ⟨0, _⟩ => tp.items triple.1
| ⟨1, _⟩ => tp.items triple.2.1
| ⟨2, _⟩ => tp.items triple.2.2
| _ => 0
```

**Components**:
- `⟨0, _⟩` is anonymous constructor syntax for `Fin` (value, proof)
- `_` ignores the proof component
- `| pattern => expression` for each case

**Usage in OCP proof**: Extracts elements from tuples based on position index.

---

## Mathlib Integration

Mathlib is Lean's mathematics library with extensive formalized mathematics.

### Imported Modules

```lean
import Mathlib.Data.Finset.Basic
import Mathlib.Data.Finset.Card
import Mathlib.Data.Nat.Basic
import Mathlib.Tactic
```

**What they provide**:
- `Finset`: Finite sets with computable operations
- `Card`: Cardinality functions
- `Nat.Basic`: Natural number operations
- `Tactic`: Proof automation tools

### Finset Operations

```lean
Finset.univ          -- Universal set (all elements)
Finset.range n       -- {0, 1, ..., n-1}
Finset.image f s     -- {f(x) | x ∈ s}
s₁ ∪ s₂              -- Union
s₁ \ s₂              -- Set difference
s.card               -- Cardinality
s₁ ⊆ s₂              -- Subset
```

**Usage in OCP proof**: Managing segments, computing residuals, checking coverage.

---

## Proof Tactics

Tactics are commands that construct proofs interactively.

### Sorry Tactic

```lean
theorem reduction_forward (tp : ThreePartition) :
    tp.hasValidPartition →
    (Reduction.constructOCP tp).hasValidCover := by
  intro ⟨partition, h_valid⟩
  sorry
```

**Purpose**:
- `sorry` is a placeholder that accepts any goal as proven
- Used during development before completing the proof
- The proof compiles but is not actually verified

### Common Tactics (for future completion)

```lean
by
  intro x           -- Introduce hypothesis
  exact term        -- Provide exact proof term
  apply theorem     -- Apply a theorem
  simp              -- Simplify using lemmas
  constructor       -- Split conjunction/exists
  cases h           -- Case analysis on h
  induction n       -- Induction on n
```

---

## Lemmas and Theorems

### Lemma Structure

```lean
lemma gate_discipline
    (h_instance : instance = Reduction.constructOCP tp)
    (h_cost : OCP.totalCost instance.segments instance.covering π ≤ instance.budget)
    (h_feasible : OCP.isFeasible instance.segments instance.covering π) :
    ∀ t : Fin tp.m, ∃ i : ℕ, ... := by
  sorry
```

**Components**:
- Hypotheses (above the `:`) are assumptions
- Conclusion (after `:`) is what we prove
- `by` introduces tactic mode

### Theorem with Bidirectional Proof

```lean
theorem ocp_dec_np_complete :
    (∀ tp : ThreePartition,
      tp.hasValidPartition ↔ (Reduction.constructOCP tp).hasValidCover) := by
  intro tp
  constructor
  · exact reduction_forward tp
  · exact reduction_backward tp
```

**Structure**:
- `↔` is logical equivalence (iff)
- `constructor` splits into forward and backward directions
- `·` introduces sub-goals (bullet points)

---

## Key Lean 4 Concepts Summary

| Concept | Purpose | Example in OCP Proof |
|---------|---------|---------------------|
| **Type aliases** | Semantic clarity | `Segment`, `Edge` |
| **Structures** | Record types with constraints | `ThreePartition`, `OCP_DEC` |
| **Inductive types** | Sum types, enums | `SegmentType`, `EdgeType` |
| **Dependent types** | Types depending on values | `Fin n`, `items : Fin (3*m) → ℕ` |
| **Propositions as types** | Curry-Howard | `Prop`, `hasValidCover` |
| **Namespaces** | Code organization | `OCP`, `Reduction`, `Correctness` |
| **Pattern matching** | Destructuring data | `match pos with \| ⟨0,_⟩ => ...` |
| **Tactics** | Interactive proving | `intro`, `constructor`, `sorry` |
| **Mathlib** | Mathematical library | `Finset`, cardinality, set operations |

---

## Next Steps

To complete the formalization:

1. **Replace `sorry`**: Implement actual proof terms using tactics
2. **Verify reduction**: Complete the `reductionCovering` function
3. **Prove lemmas**: Fill in gate discipline, item uniqueness, etc.
4. **Type-check**: Run `lake build` to verify the formalization
5. **Extract certificate**: Use Lean's code extraction to generate verified algorithms

---

## References

- [Lean 4 Manual](https://lean-lang.org/lean4/doc/)
- [Theorem Proving in Lean 4](https://leanprover.github.io/theorem_proving_in_lean4/)
- [Mathematics in Lean](https://leanprover-community.github.io/mathematics_in_lean/)
- [Mathlib Documentation](https://leanprover-community.github.io/mathlib4_docs/)
- [Lean Zulip Chat](https://leanprover.zulipchat.com/)

---

## Glossary

- **Proposition**: A statement that can be true or false (type `Prop`)
- **Proof**: A term that witnesses the truth of a proposition
- **Tactic**: A command that constructs proof terms
- **Dependent type**: A type that depends on a value
- **Inductive type**: A type defined by its constructors
- **Structure**: A record type with named fields
- **Namespace**: A scope for organizing definitions
- **Finset**: A finite set with computable operations
- **Curry-Howard**: The correspondence between propositions and types, proofs and terms
