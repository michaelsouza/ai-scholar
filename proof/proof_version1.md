# Teorema (NP-Completude do OCP-DEC)

**Enunciado.** O problema decisório OCP-DEC — dado um hipergrafo (H=(E_p,S)) (no formato do OCP) e um orçamento (B), decidir se existe uma ordenação (\pi) que cobre (S) com (F(\pi)\le B) — é NP-completo.

**Prova.**
(1) ( \mathbf{OCP\text{-}DEC\in NP}): dado (\pi), computa-se incrementalmente (\Gamma(\pi_i)) com bitsets sobre (S) e (F(\pi)); verifica-se cobertura. Tempo polinomial.

(2) ( \mathbf{NP})-dureza por redução de **Set Cover**. Dada ((U,\mathcal C,k)), constrói-se uma instância OCP:

* Fixe (R) tal que (2^R>\alpha n) (p.ex., (R=\lceil \log_2(2n)\rceil+1), (\alpha=2)).
* Para cada (u\in U), crie um segmento (t(u)).
* Para cada (C_j\in\mathcal C), crie um bloco (G_j) com (R) segmentos (disjuntos entre si e de todos (t(\cdot))).
* Arestas:

  * (A_j): (\llbracket A_j\rrbracket=G_j) (seletor do conjunto (j)).
  * (Z_{j,u}) (para todo (u\in C_j)): (\llbracket Z_{j,u}\rrbracket=G_j\cup{t(u)}).
  * (Opcional) (F_u): (\llbracket F_u\rrbracket={t(u)}) — não é necessária para a correção, apenas ajuda a clarear que há sempre caminho barato para (t(u)).

Defina (E_p) como o conjunto das arestas acima e **(S)** como a partição **induzida por** (\bigcup_{e\in E_p}\llbracket e\rrbracket) (logo, somente os (G_j) efetivamente presentes nas incidências das arestas e os (t(u)) aparecem em (S)).
Orçamento: (B=k\cdot 2^R+\alpha n).

* (⇒) Se existe (\mathcal C'\subseteq\mathcal C), (|\mathcal C'|\le k), que cobre (U), tome (\pi) que:

  1. seleciona (A_j) para cada (j\in\mathcal C') (custo (k\cdot 2^R));
  2. para cada (u), escolhe algum (j\in\mathcal C') com (u\in C_j) e seleciona (Z_{j,u}) **depois** de (A_j) (cada um custa (\le 2)).
     Total (F(\pi)\le k\cdot 2^R+\alpha n=B). Cobertura: todos os (G_j) com (j\in\mathcal C') e todos os (t(u)) ficam cobertos.

* (⇐) Se existe (\pi) com (F(\pi)\le B):
  Cada vez que (\pi) cobre algum (G_j) pela primeira vez, o incremento é (\ge 2^R); seja (S^+(\pi)) o conjunto desses (j). Então (|S^+(\pi)|\le k) (pois (F(\pi)\le B)).
  Para cobrir todo (t(u)), é necessário que (\pi) contenha algum (Z_{j,u}) **após** (A_j) (ou custo (\ge 2^R) adicional, o que violaria (B) por escolha de (R)). Logo, ({C_j:, j\in S^+(\pi)}) **cobre (U)** e (|S^+(\pi)|\le k). Conclui-se uma solução de Set Cover com (\le k) conjuntos.

Como a redução é polinomial e (1) vale, OCP-DEC é NP-completo. (\square)

---

## Notas finais (sobre a engenharia do (S))

* A definição de (S) **segue exatamente** a do seu OCP: é a partição dos índices induzida por (\llbracket E_p\rrbracket). Não “criamos” portas de conjuntos não usados fora de (\llbracket E_p\rrbracket); portanto, não há a obrigação espúria de cobri-las.
* O truque técnico é **não proliferar** múltiplas portas (G_{j,\ell}); usamos **um único** (G_j) por conjunto e forçamos que **apenas** (A_j) (ou o primeiro (Z_{j,u})) pague o custo (2^R). Em seguida, os (t(u)) são cobertos a custo (\le\alpha) por elemento.

