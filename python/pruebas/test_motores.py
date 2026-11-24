"""Pruebas automáticas de los motores de cálculo.  Uso:  python pruebas/test_motores.py"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np
from modulos.grafico import resolver
from modulos.colas import mms, tabla_costos, prob_n
from modulos import markov as mk

def R(b1=100, b2=80, b3=40):
    return [dict(a1=2, a2=1, op="<=", b=b1), dict(a1=1, a2=1, op="<=", b=b2), dict(a1=1, a2=0, op="<=", b=b3)]

def aprox(a, b, tol=1e-6): assert abs(a - b) < tol, (a, b)

def test_grafico():
    r = resolver(3, 2, R()); assert r.estado == "optimo"
    assert r.optimo == (20.0, 60.0, 180.0) and len(r.vertices) == 5
    aprox(r.verificacion_linprog, 180)
    assert r.holguras == [0.0, 0.0, 20.0]
    assert resolver(3, 5, R()).optimo[:2] == (0.0, 80.0)            # c2 = 5
    assert resolver(3, 1, R()).optimo[:2] == (40.0, 20.0)           # c2 = 1
    assert resolver(3, 3, R()).multiples                            # óptimos alternos (frontera)
    assert resolver(3, 2, R(b1=120)).optimo == (40.0, 40.0, 200.0)  # precio sombra 1
    assert resolver(3, 2, R(b3=30)).optimo[2] == 180.0              # restricción inactiva
    assert resolver(1, 1, R() + [dict(a1=1, a2=1, op=">=", b=200)]).estado == "infactible"
    assert resolver(1, 1, [dict(a1=1, a2=-1, op="<=", b=5)]).estado == "no_acotado"
    m = resolver(2, 3, [dict(a1=1, a2=1, op=">=", b=10), dict(a1=1, a2=0, op=">=", b=2)], maximizar=False)
    assert m.optimo == (10.0, 0.0, 20.0)

def test_colas():
    m = mms(2, 3, 1)                                                 # M/M/1 con solución cerrada
    aprox(m.L, 2); aprox(m.Lq, 4 / 3); aprox(m.W, 1); aprox(m.Wq, 2 / 3)
    m = mms(40, 25, 2); aprox(m.P0, 1 / 9); aprox(m.Lq, 2.844444, 1e-5); aprox(m.L, 4.444444, 1e-5)
    assert not mms(40, 25, 1).estable
    aprox(sum(prob_n(mms(40, 25, 3), n) for n in range(600)), 1, 1e-9)
    for lam, s_esp in [(20, 2), (40, 3), (60, 4)]:
        t = [f for f in tabla_costos(lam, 25, 1, 9, 8, 12) if f["estable"]]
        assert min(t, key=lambda f: f["costo_total"])["s"] == s_esp

def test_markov():
    P = np.array([[.7, .2, .1], [.25, .6, .15], [.3, .2, .5]])
    assert mk.validar(P) == [] and mk.validar([[.5, .4], [.3, .7]]) != []
    pi = mk.estado_estable(P); assert np.allclose(pi, [17 / 36, 1 / 3, 7 / 36])
    assert np.allclose(mk.proyectar([.5, .3, .2], P, 1)[1], [.485, .32, .195])
    assert mk.clasificar(P).ergodica
    M = mk.tiempos_primera_pasada(P); assert np.allclose(np.diag(M), 1 / pi)
    assert mk.estado_estable([[1, 0], [.5, .5]]) is None            # absorbente: sin π único
    assert not mk.clasificar([[0, 1], [1, 0]]).ergodica             # periódica

if __name__ == "__main__":
    for f in (test_grafico, test_colas, test_markov):
        f(); print("OK ", f.__name__)
    print("Todas las pruebas pasaron.")
