"""Benchmark metrics for evidence-synthesis tasks (QAS-033). Pure Python, no dependencies.
Conventions: a ranking is a list of 0/1 labels ordered best-first (1 = relevant/included)."""
import math
from typing import Iterable, Sequence, Set, Tuple

def _check(labels: Sequence[int]):
    if not labels: raise ValueError("empty ranking")
    if sum(labels) == 0: raise ValueError("no relevant records")

def screened_for_recall(labels: Sequence[int], recall: float) -> int:
    """Smallest number of records screened (from the top) that reaches the target recall."""
    _check(labels)
    need = math.ceil(recall * sum(labels) - 1e-12); found = 0
    for i, l in enumerate(labels, 1):
        found += l
        if found >= need: return i
    return len(labels)

def wss(labels: Sequence[int], recall: float = 0.95) -> float:
    """Work Saved over Sampling at a target recall: (N - n) / N - (1 - recall)."""
    n = screened_for_recall(labels, recall); N = len(labels)
    return (N - n) / N - (1 - recall)

def recall_at(labels: Sequence[int], fraction: float) -> float:
    """Recall after screening the top `fraction` of records."""
    _check(labels); k = math.ceil(fraction * len(labels) - 1e-12)
    return sum(labels[:k]) / sum(labels)

def atd(labels: Sequence[int]) -> float:
    """Average time to discovery: mean position of relevant records as a fraction of N."""
    _check(labels); N = len(labels)
    pos = [i for i, l in enumerate(labels, 1) if l]
    return sum(pos) / len(pos) / N

def pair_prf(predicted: Iterable[Tuple[str, str]], truth: Iterable[Tuple[str, str]]) -> Tuple[float, float, float]:
    """Precision, recall, F1 for duplicate pairs (order-insensitive)."""
    norm = lambda s: {tuple(sorted(p)) for p in s}
    P, T = norm(predicted), norm(truth); tp = len(P & T)
    p = tp / len(P) if P else 0.0; r = tp / len(T) if T else 0.0
    return p, r, (2 * p * r / (p + r) if p + r else 0.0)

def cohens_kappa(a: Sequence[int], b: Sequence[int]):
    """Cohen's kappa for two raters; None when undefined (expected agreement is 1)."""
    n = len(a)
    if n == 0 or n != len(b): raise ValueError("raters must have equal, non-zero length")
    po = sum(x == y for x, y in zip(a, b)) / n
    cats: Set = set(a) | set(b)
    pe = sum((a.count(c) / n) * (b.count(c) / n) for c in cats)
    return None if pe >= 1 else (po - pe) / (1 - pe)

def prisma_reconciles(identified: int, duplicates: int, screened: int, excluded_ta: int,
                      assessed: int, excluded_ft: int, included: int) -> list:
    """Return a list of discrepancies in PRISMA 2020 flow counts (empty list = reconciles)."""
    issues = []
    if identified - duplicates != screened: issues.append("identified - duplicates != screened")
    if screened - excluded_ta != assessed: issues.append("screened - excluded(TA) != assessed")
    if assessed - excluded_ft != included: issues.append("assessed - excluded(FT) != included")
    return issues
