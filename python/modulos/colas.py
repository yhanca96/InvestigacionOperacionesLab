"""Teoría de colas M/M/s (incluye M/M/1 con s=1).

λ = tasa de llegadas, μ = tasa de servicio POR servidor (mismas unidades de tiempo).
a = λ/μ ; ρ = λ/(sμ) < 1 para estabilidad.
"""
from dataclasses import dataclass
from math import factorial, exp


@dataclass
class MMs:
    s: int
    lam: float
    mu: float
    estable: bool
    rho: float
    P0: float = float("nan")
    Pespera: float = float("nan")   # prob. de que un cliente deba esperar (Erlang C)
    Lq: float = float("inf")
    L: float = float("inf")
    Wq: float = float("inf")
    W: float = float("inf")


def mms(lam, mu, s):
    rho = lam / (s * mu)
    if rho >= 1:
        return MMs(s, lam, mu, False, rho)
    a = lam / mu
    suma = sum(a ** n / factorial(n) for n in range(s))
    ultimo = a ** s / (factorial(s) * (1 - rho))
    P0 = 1.0 / (suma + ultimo)
    C = ultimo * P0
    Lq = P0 * a ** s * rho / (factorial(s) * (1 - rho) ** 2)
    Wq = Lq / lam
    W = Wq + 1 / mu
    return MMs(s, lam, mu, True, rho, P0, C, Lq, lam * W, Wq, W)


def prob_n(m: MMs, n):
    """P(n clientes en el sistema)."""
    a = m.lam / m.mu
    if n < m.s:
        return m.P0 * a ** n / factorial(n)
    return m.P0 * a ** n / (factorial(m.s) * m.s ** (n - m.s))


def prob_espera_mayor_t(m: MMs, t):
    """P(Wq > t) en las mismas unidades de tiempo que λ y μ."""
    return m.Pespera * exp(-(m.s * m.mu - m.lam) * t)


def tabla_costos(lam, mu, s_min, s_max, c_servidor, c_espera, espera_en="sistema"):
    """Costo total esperado por unidad de tiempo para s = s_min..s_max.

    CT = c_servidor*s + c_espera*(L | Lq)   (c_espera = costo por cliente por unidad de tiempo).
    """
    filas = []
    for s in range(s_min, s_max + 1):
        m = mms(lam, mu, s)
        if not m.estable:
            filas.append(dict(s=s, rho=m.rho, estable=False))
            continue
        n_esp = m.L if espera_en == "sistema" else m.Lq
        cs, ce = c_servidor * s, c_espera * n_esp
        filas.append(dict(s=s, rho=m.rho, estable=True, L=m.L, Lq=m.Lq, W=m.W, Wq=m.Wq,
                          costo_servicio=cs, costo_espera=ce, costo_total=cs + ce))
    return filas
