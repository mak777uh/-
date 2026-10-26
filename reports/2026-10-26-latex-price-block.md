# LaTeX-блок для `main.tex` §«Condition two: the price of a trait» (v1.1)

*Файл-заготовка: три замены в `_hourly/grants/arxiv-tex/main.tex`. Причина — `main.tex` отстал от
`paper.md`: в нём строка таблицы говорит «threshold −0.3 met», а вердикт ужесточён до «sign firm,
magnitude not determined», и нет абзаца про ограничение конструкции (§10bd).*

## Замена 1 — строка таблицы (one-bud)

**Было:**

```latex
one bud per lineage, seeds 101–110 & \textbf{7.5} & \textbf{8/10} & \textbf{−0.478}, threshold −0.3 met \\
```

**Стало:**

```latex
one bud per lineage, seeds 101–110 & \textbf{7.5} & \textbf{8/10} & \textbf{−0.478}; sign firm, magnitude not determined \\
```

## Замена 2 — абзац «The magnitude is unstable…»

**Было:**

```latex
The magnitude is unstable: in 3 of 8 runs the threshold is not reached, with
quartiles −0.785 … −0.203. The sign is negative even in the control where there
are only 2.5 lineages, so the sign alone does not establish the mechanism. What
distinguishes the constructions is the number of lineages (2.5 → 4.0 → 7.5) and
the fraction of usable runs (1/10 → 4/10 → 8/10).
```

**Стало:**

```latex
Sign and magnitude behave differently, and we separate them. The sign is firm:
the partial correlation is negative in \textbf{all 8} usable runs (one-sided sign
test, $p = 0.0039$). The magnitude is not: median −0.478 with a 95\,\% bootstrap
interval $[-0.797,\,-0.177]$, and the pre-registered threshold $-0.3$ lies
\emph{inside} that interval, so no quantitative verdict is issued (quartiles
$-0.785$ … $-0.203$; in 3 of 8 runs the threshold is not reached). Adding seeds
does not help: at 30 seeds the upper bound is still $-0.281$. What distinguishes
the constructions is the number of lineages (2.5 → 4.0 → 7.5) and the fraction of
usable runs (1/10 → 4/10 → 8/10).
```

## Замена 3 — новый абзац после «Boundary» (перед следующей подсекцией)

```latex
\textbf{Why the magnitude is not determined: a limit of the construction, not of
sampling.} The width of the interval of the median scales as $1/\sqrt{n_{\text{lines}}}$,
and the threshold $-0.3$ leaves the interval only at \textbf{12 or more lineages
per run}: 7.5 lineages give $[-0.689,\,-0.267]$, 9 give $[-0.670,\,-0.286]$, 12
give $[-0.645,\,-0.311]$. We therefore varied the construction rather than the
number of seeds: fourteen single-seed pilots, each changing one parameter. The
best result is \textbf{9 lineages} (\texttt{--steps 250}, top-1 share 0.507);
longer runs are worse because the dominant lineage takes the world (top-1 share
0.507 → 0.685 → 0.9 as the run grows), more mutation produces many labels and
few usable lineages (97–103 labels, 3 lineages), and more starting cells produce
exactly \textbf{one} lineage (top-1 share 0.88). The series was not run: $df \ge 9$
is unreachable in this world. A verdict would require a different mechanism that
limits the share of the world held by one lineage (type quotas or frequency
dependence), because such a change alters the mechanism of displacement itself.
```

## Проверки после вставки

1. `$` сбалансированы: в блоке 12 пар, ни одного «голого» процента (`\%`).
2. Тире и минус: в формулах `$[-0.797,\,-0.177]$` — дефис-минус, как в остальном файле.
3. Числа совпадают с агрегатами: 7.5 / 8/10 / −0.478 / 0.0039 / [−0.797, −0.177] / 0.281 / 9 / 0.507 /
   0.685 / 0.9 / 0.88 / 97–103 / 3 — все из §10ax и §10bd.
4. После вставки пересобрать `arxiv-tex.zip` (6 файлов) и прогнать `check_draft_numbers.py` на
   `paper.md` — он не смотрит `.tex`, но сверка чисел делается по нему.
