"""Motor del método gráfico (programación lineal, 2 variables).

Modelo:  opt Z = c1*x1 + c2*x2   s.t.  a1*x1 + a2*x2 (<=,>=,=) b,  x1,x2 >= 0
Método: se intersectan todas las rectas por pares, se conservan los puntos
factibles (vértices) y se evalúa Z en cada uno. scipy.linprog se usa solo
para clasificar el caso (infactible / no acotado) y como verificación.
"""
from dataclasses import dataclass, field
from itertools import combinations
import numpy as np
from scipy.optimize import linprog

TOL = 1e-7


@dataclass
class Resultado:
    estado: str                      # 'optimo' | 'infactible' | 'no_acotado'
    vertices: list = field(default_factory=list)   # [(x1, x2, Z)]
    optimo: tuple | None = None      # (x1, x2, Z)
    multiples: bool = False          # óptimos alternos
    optimos_alternos: list = field(default_factory=list)
    holguras: list = field(default_factory=list)   # por restricción en el óptimo
    verificacion_linprog: float | None = None
    poligono: list = field(default_factory=list)   # para graficar (con caja)


def _lineas(restricciones):
    """Todas las rectas (a1,a2,b): restricciones del usuario + ejes."""
    L = [(r["a1"], r["a2"], r["b"]) for r in restricciones]
    L += [(1.0, 0.0, 0.0), (0.0, 1.0, 0.0)]      # x1=0, x2=0
    return L


def es_factible(p, restricciones, tol=TOL):
    x1, x2 = p
    if x1 < -tol or x2 < -tol:
        return False
    for r in restricciones:
        v = r["a1"] * x1 + r["a2"] * x2
        if r["op"] == "<=" and v > r["b"] + tol:
            return False
        if r["op"] == ">=" and v < r["b"] - tol:
            return False
        if r["op"] == "=" and abs(v - r["b"]) > tol:
            return False
    return True


def _vertices(restricciones, extra=()):
    L = _lineas(restricciones) + list(extra)
    pts = []
    for (a1, a2, b), (c1, c2, d) in combinations(L, 2):
        det = a1 * c2 - a2 * c1
        if abs(det) < 1e-12:
            continue                                # paralelas
        x1 = (b * c2 - a2 * d) / det
        x2 = (a1 * d - b * c1) / det
        p = (round(x1, 9) + 0.0, round(x2, 9) + 0.0)
        if es_factible(p, restricciones) and all(
                abs(p[0] - q[0]) > 1e-6 or abs(p[1] - q[1]) > 1e-6 for q in pts):
            pts.append(p)
    return pts


def _orden_poligono(pts):
    if len(pts) < 3:
        return pts
    cx = sum(p[0] for p in pts) / len(pts)
    cy = sum(p[1] for p in pts) / len(pts)
    return sorted(pts, key=lambda p: np.arctan2(p[1] - cy, p[0] - cx))


def _linprog(c, restricciones, maximizar):
    cc = -np.array(c) if maximizar else np.array(c)
    Aub, bub, Aeq, beq = [], [], [], []
    for r in restricciones:
        fila = [r["a1"], r["a2"]]
        if r["op"] == "<=":
            Aub.append(fila); bub.append(r["b"])
        elif r["op"] == ">=":
            Aub.append([-fila[0], -fila[1]]); bub.append(-r["b"])
        else:
            Aeq.append(fila); beq.append(r["b"])
    return linprog(cc, A_ub=Aub or None, b_ub=bub or None,
                   A_eq=Aeq or None, b_eq=beq or None,
                   bounds=[(0, None), (0, None)], method="highs")


def resolver(c1, c2, restricciones, maximizar=True, caja=None):
    """Resuelve el PL. `caja` = límite para dibujar regiones no acotadas."""
    ref = _linprog((c1, c2), restricciones, maximizar)
    # status: 0 ok, 2 infactible, 3 no acotado
    if ref.status == 2:
        return Resultado(estado="infactible")

    V = _vertices(restricciones)
    if ref.status == 3:
        res = Resultado(estado="no_acotado")
        res.vertices = [(x, y, c1 * x + c2 * y) for x, y in V]
        res.poligono = _poligono_caja(restricciones, caja)
        return res

    Z = [(x, y, c1 * x + c2 * y) for x, y in V]
    if not Z:  # no debería ocurrir si linprog dice óptimo
        return Resultado(estado="infactible")
    key = max if maximizar else min
    zopt = key(z[2] for z in Z)
    opts = [z for z in Z if abs(z[2] - zopt) < 1e-6]
    best = opts[0]
    hol = []
    for r in restricciones:
        v = r["a1"] * best[0] + r["a2"] * best[1]
        hol.append(round(abs(r["b"] - v), 9) if r["op"] != "=" else 0.0)
    res = Resultado(
        estado="optimo", vertices=sorted(Z), optimo=best,
        multiples=len(opts) > 1, optimos_alternos=opts, holguras=hol,
        verificacion_linprog=(-ref.fun if maximizar else ref.fun),
    )
    res.poligono = _poligono_caja(restricciones, caja)
    return res


def _poligono_caja(restricciones, caja=None):
    """Polígono de la región (recortada por una caja) solo para dibujar."""
    V = _vertices(restricciones)
    if caja is None:
        m = max([abs(c) for p in V for c in p] + [1.0])
        caja = m * 2 + 10
    extra = [(1.0, 0.0, caja), (0.0, 1.0, caja)]
    rcaja = restricciones + [
        {"a1": 1.0, "a2": 0.0, "op": "<=", "b": caja},
        {"a1": 0.0, "a2": 1.0, "op": "<=", "b": caja}]
    P = _vertices(rcaja)
    return _orden_poligono(P)
