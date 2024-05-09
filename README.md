# string-partition-experiments
Experiments for exact solutions of the string partition problem using linear programming

Install dependencies by running `pip install -r requirements`. It is recommended to utilize [Python Virtual Env](https://docs.python.org/3/library/venv.html).

To run a subset of the tests, use the executor script. Inform which which implementation to run ('cb', 'cs', 'cb-mod', 'cs-mod'), the indexes of the first and last test and pass the `-r` flag to allow substring reversal.

## Formulations

### Unbalanced strings

#### Common blocks

Using notation from Blum, 2020:

$$
\begin{align}
    \min \quad & m - \sum_{b_i \in B^{>1}}(x_i - x_i |t_i|) \nonumber \\
    \text{s.t} \quad & \sum_{b_i \in B^{>1} \text{ s.t. } k1_i\leq j < k1_i + |t_i|}x_i \leq 1 & \forall j \in [n_1] \\
    & \sum_{b_i \in B^{>1} \text{ s.t. } k2_i\leq j < k2_i + |t_i|}x_i \leq 1 & \forall j \in [n_2]
\end{align}
$$

where $m$ is the total size of the common substrings, that is:

$$
\begin{equation}
    m = \sum_{c \in \Sigma_{S_1}\cap \Sigma_{S_2}} \min(occ(c, S_1), occ(c, S_2))
\end{equation}
$$

#### Common blocks 2

Let common blocks $b_i$ of strings $s_1$ and $s_2$ be denoted as a triple $(t_i, k1_i, k2_i)$ as in Blum et al, 2015. Let $B = \{ b_1, \ldots, b_m \}$ the ordered set of all possible common blocks of $s_1$ and $s_2$.

An exclusive block is a subsequence of one of the genomes that is disjunct from all common blocks in the partition. Denote an exclusive block of $s_1$ (resp. $s_2$) $e_1$ (resp. $e_1$) by the tuple $(r_i, l1_i)$ (resp. $(r_i, l2_i)$). Let $E1$ and $E2$ denote the ordered set of all excluive blocks of $s_1$ and $s_2$ respectively.

$$
\begin{align}
    \min \quad & \sum_{b_i \in B} x_i + \sum_{e1_{i'} \in E1} y1_{i'} + \sum_{e2_{i''} \in E2} y2_{i''} \nonumber \\
    \text{s.t} \quad & \sum_{b_i \in B \text{ s.t. } k1_i\leq j < k1_i + |t_i|}x_i + \sum_{e1_{i'} \in E1 \text{ s.t. } l1_{i'}\leq j < l1_{i'} + |r_{i'}|} y1_{i'} = 1 & \forall j \in [n_1] \\
    & \sum_{b_i \in B \text{ s.t. } k2_i\leq j < k2_i + |t_i|}x_i + \sum_{e2_{i'} \in E2 \text{ s.t. } l2_{i'}\leq j < l2_{i'} + |r_{i'}|} y2_{i'} = 1 & \forall j \in [n_2]
\end{align}
$$

#### Common blocks 2 modification

The trivial upper bound to the SMCSP problem is the case in which all blocks, exclusive or common, have size 1. Let $m$ be such an upper bound given by:

$$
\begin{equation}
    m = \sum_{c \in \Sigma_{S_1}\cap \Sigma_{S_2}} \max(occ(c, S_1), occ(c, S_2))
\end{equation}
$$

$$
\begin{align}
    \min \quad & m - \sum_{b_i \in B^{>1}} (x_i - x_i|t_i|) + \sum_{e1_{i'} \in E1^{>1}} (y1_{i'} - y1_{i'}|l1_{i'}|) + \sum_{e2_{i''} \in E2^{>1}} (y2_{i''} - y2_{i''}|l2_{i''}|) \nonumber \\
    \text{s.t} \quad & \sum_{b_i \in B^{>1} \text{ s.t. } k1_i\leq j < k1_i + |t_i|}x_i + \sum_{e1_{i'} \in E1^{>1} \text{ s.t. } l1_{i'}\leq j < l1_{i'} + |r_{i'}|} y1_{i'} \leq 1 & \forall j \in [n_1] \\
    & \sum_{b_i \in B^{>1} \text{ s.t. } k2_i\leq j < k2_i + |t_i|}x_i + \sum_{e2_{i'} \in E2^{>1} \text{ s.t. } l2_{i'}\leq j < l2_{i'} + |r_{i'}|} y2_{i'} \leq 1 & \forall j \in [n_2]
\end{align}
$$

#### Common substrings

Let $T$ be the set of all common substrings of $s_1$ and $s_2$. For each $t \in T$, let $Q1_t$ (resp. $Q2_t$) be the set of all position at which $t$ starts in string $s_1$ (resp. $s_2$).

Moreover,  let $E1$ and $E2$ be defined as above.

$$
\begin{align}
    \min \quad & \sum_{t \in T} \sum_{k \in Q1_t} y^1_{t,k} + \sum_{e1_{i} \in E1} x1_{i} + \sum_{e2_{j} \in E2} x2_{j} \nonumber \\
    \text{s.t.} \quad & \sum_{t \in T} \sum_{k \in q1_t \text{s.t. } k \leq j < k + |t|} y^1_{t,k} + \sum_{e1_{i} \in E1 \text{ s.t. } l1_{i}\leq j < l1_{i} + |r_{i}|} x1_{i} = 1 & \forall j \in [n_1] \\
    & \sum_{t \in T} \sum_{k \in q2_t \text{s.t. } k \leq j < k + |t|} y^2_{t,k} + \sum_{e2_{i} \in E2 \text{ s.t. } l2_{i}\leq j < l2_{i} + |r_{i}|} x2_{i} = 1 & \forall j \in [n_2] \\
    & \sum_{k \in Q1_t} y^1_{t,k} = \sum_{k \in Q2_t} y^2_{t,k} & \forall t \in T
\end{align}
$$