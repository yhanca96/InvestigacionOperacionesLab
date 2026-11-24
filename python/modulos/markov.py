"""Cadenas de Markov de tiempo discreto y espacio de estados finito."""
from dataclasses import dataclass
from math import gcd
import numpy as np

TOL = 1e-8


def validar(P, tol=1e-6):
    """Devuelve lista de errores (vacía si P es una matriz estocástica válida)."""
    P = np.asarray(P, dtype=float)
    errs = []
    if P.ndim != 2 or P.shape[0] != P.shape[1]:
        return ["La matriz debe ser cuadrada."]
    if (P < -tol).any():
        errs.append("Hay probabilidades negativas.")
    if (P > 1 + tol).any():
        errs.append("Hay probabilidades mayores que 1.")
    for i, s in enumerate(P.sum(axis=1)):
        if abs(s - 1) > tol:
            errs.append(f"La fila {i + 1} suma {s:.4f} (debe sumar 1).")
    return errs


def proyectar(pi0, P, n):
    """Lista [π(0), π(1), ..., π(n)] con π(k+1) = π(k)·P."""
    pi = np.asarray(pi0, dtype=float)
    P = np.asarray(P, dtype=float)
    out = [pi.copy()]
    for _ in range(n):
        pi = pi @ P
        out.append(pi.copy())
    return np.array(out)


def potencia(P, n):
    return np.linalg.matrix_power(np.asarray(P, dtype=float), n)


def accesibilidad(P, tol=TOL):
    """R[i,j] = True si j es alcanzable desde i en ≥ 0 pasos."""
    n = len(P)
    A = (np.asarray(P) > tol)
    R = A | np.eye(n, dtype=bool)
    for _ in range(n):                       # cierre transitivo
        R = R | (R.astype(int) @ R.astype(int) > 0)
    return R


def periodo_estado(P, i, tol=TOL):
    """Período del estado i: mcd de los n con (Pⁿ)_ii > 0 (se revisan n ≤ 2·N²)."""
    P = np.asarray(P, dtype=float)
    N = len(P)
    g, M = 0, np.eye(N)
    for n in range(1, 2 * N * N + 1):
        M = M @ P
        if M[i, i] > tol:
            g = gcd(g, n)
            if g == 1:
                return 1
    return g


@dataclass
class Clasificacion:
    irreducible: bool
    aperiodica: bool
    ergodica: bool
    absorbentes: list
    periodos: list
    clases: list


def clasificar(P):
    P = np.asarray(P, dtype=float)
    N = len(P)
    R = accesibilidad(P)
    comunican = R & R.T
    clases, vistos = [], set()
    for i in range(N):
        if i in vistos:
            continue
        c = [j for j in range(N) if comunican[i, j]]
        vistos.update(c)
        clases.append(c)
    irred = len(clases) == 1
    per = [periodo_estado(P, i) for i in range(N)]
    aper = all(p == 1 for p in per) if irred else False
    absorb = [i for i in range(N) if abs(P[i, i] - 1) < TOL]
    return Clasificacion(irred, aper, irred and aper, absorb, per, clases)


def estado_estable(P):
    """π tal que πP = π, Σπ = 1.  Devuelve None si no es único (cadena no irreducible)."""
    P = np.asarray(P, dtype=float)
    N = len(P)
    if not clasificar(P).irreducible:
        return None
    A = np.vstack([(P.T - np.eye(N))[:-1], np.ones(N)])
    b = np.zeros(N); b[-1] = 1
    pi = np.linalg.solve(A, b)
    return pi


def tiempos_primera_pasada(P):
    """M[i,j] = E[pasos para llegar a j por primera vez partiendo de i] (M[i,i] = tiempo de retorno)."""
    P = np.asarray(P, dtype=float)
    N = len(P)
    M = np.zeros((N, N))
    for j in range(N):
        idx = [i for i in range(N) if i != j]
        Q = P[np.ix_(idx, idx)]
        m = np.linalg.solve(np.eye(N - 1) - Q, np.ones(N - 1))
        for k, i in enumerate(idx):
            M[i, j] = m[k]
        M[j, j] = 1 + P[j, idx] @ m
    return M


def pasos_hasta_convergencia(pi0, P, eps=1e-3, max_n=500):
    """Primer n con max|π(n) − π| < eps."""
    pi_est = estado_estable(P)
    if pi_est is None:
        return None
    pi = np.asarray(pi0, dtype=float)
    P = np.asarray(P, dtype=float)
    for n in range(max_n + 1):
        if np.max(np.abs(pi - pi_est)) < eps:
            return n
        pi = pi @ P
    return None
