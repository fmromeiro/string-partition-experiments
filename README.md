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