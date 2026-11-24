import streamlit as st
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from modulos.grafico import resolver
from modulos import markov as mk
from modulos.colas import mms, prob_n, prob_espera_mayor_t, tabla_costos

st.set_page_config(page_title="Aplicativo Final - Investigación de Operaciones", layout="wide")
st.title("Aplicativo de Optimización")
st.caption("ITM · Investigación de Operaciones · Método gráfico · Teoría de Colas · Cadenas de Markov")

tab1, tab2, tab3 = st.tabs(["1. Método gráfico (PL)", "2. Teoría de Colas", "3. Cadenas de Markov"])

# ---------------------------------------------------------------- TAB 1
with tab1:
    st.subheader("Programación lineal · Método gráfico (2 variables)")
    st.markdown("Ejemplo precargado: **cafetería universitaria** — cuántos sándwiches (x₁) y wraps (x₂) producir al día para maximizar la utilidad en miles de COP (valores ilustrativos). "
                "Modifique cualquier dato: el resultado se recalcula automáticamente.")

    col_in, col_out = st.columns([1, 1.6])
    with col_in:
        obj = st.radio("Objetivo", ["Maximizar", "Minimizar"], horizontal=True)
        c1c, c2c = st.columns(2)
        c1 = c1c.number_input("c₁: utilidad por unidad de x₁ (miles COP)", value=3.0)
        c2 = c2c.number_input("c₂: utilidad por unidad de x₂ (miles COP)", value=2.0)
        n1 = st.text_input("Nombre x₁", "Sándwich")
        n2 = st.text_input("Nombre x₂", "Wrap")
        st.markdown("**Restricciones**  a₁·x₁ + a₂·x₂ (op) b   (se asume x₁, x₂ ≥ 0). "
                    "Agregue o borre filas con la tabla.")
        base = pd.DataFrame({
            "Nombre": ["Pan/tortillas", "Relleno (porciones)", "Capacidad de plancha"],
            "a1": [2.0, 1.0, 1.0], "a2": [1.0, 1.0, 0.0],
            "op": ["<=", "<=", "<="], "b": [100.0, 80.0, 40.0]})
        df = st.data_editor(
            base, num_rows="dynamic", width="stretch", key="restr",
            column_config={"op": st.column_config.SelectboxColumn("op", options=["<=", ">=", "="], required=True)})

    df = df.dropna(subset=["a1", "a2", "op", "b"])
    restr = [dict(a1=float(r.a1), a2=float(r.a2), op=r.op, b=float(r.b)) for r in df.itertuples()]

    with col_in:
        st.markdown("**Escenario what-if de recursos (opcional)**")
        if restr:
            k_wi = st.selectbox("Restricción a modificar", df["Nombre"].tolist(), key="wi_k")
            d_wi = st.number_input("Cambio Δ en el lado derecho b", value=0.0, step=10.0, key="wi_d")
            st.caption("Δ ≠ 0 compara el óptimo base con el del escenario (b + Δ) y estima el precio sombra ΔZ/Δ.")

    with col_out:
        if not restr:
            st.warning("Ingrese al menos una restricción.")
        else:
            res = resolver(c1, c2, restr, maximizar=(obj == "Maximizar"))
            if res.estado == "infactible":
                st.error("Problema INFACTIBLE: las restricciones no tienen región común.")
            else:
                if res.estado == "no_acotado":
                    st.error("Problema NO ACOTADO: Z mejora indefinidamente dentro de la región factible.")
                # ---- gráfica
                xs = [p[0] for p in res.poligono] or [10]
                ys = [p[1] for p in res.poligono] or [10]
                lim = max(max(xs), max(ys), 1) * 1.15
                if res.estado == "no_acotado":
                    lim = max(max(p[0] for p in res.vertices + [(1, 1, 0)]),
                              max(p[1] for p in res.vertices + [(1, 1, 0)]), 1) * 1.6
                fig, ax = plt.subplots(figsize=(7, 5.5))
                g = np.linspace(0, lim, 400)
                paleta = ["#1f77b4", "#ff7f0e", "#9467bd", "#8c564b", "#17becf", "#e377c2", "#7f7f7f", "#bcbd22"]
                for k, (r, nm) in enumerate(zip(restr, df["Nombre"].tolist())):
                    col = paleta[k % len(paleta)]
                    lab = f'{nm}: {r["a1"]:g}x₁+{r["a2"]:g}x₂ {r["op"]} {r["b"]:g}'
                    if abs(r["a2"]) > 1e-12:
                        ax.plot(g, (r["b"] - r["a1"] * g) / r["a2"], label=lab, color=col, lw=1.8)
                    else:
                        ax.axvline(r["b"] / r["a1"], label=lab, color=col, lw=1.8)
                if res.poligono and len(res.poligono) >= 3:
                    ax.fill([p[0] for p in res.poligono], [p[1] for p in res.poligono],
                            alpha=0.25, color="tab:green", label="Región factible")
                for (x, y, z) in res.vertices:
                    ax.plot(x, y, "ko", ms=5)
                    dx = 8 if x < lim * 0.6 else -62
                    dy = 8 if y < lim * 0.85 else -28
                    ax.annotate(f"({x:g}, {y:g})  Z={z:g}", (x, y), textcoords="offset points",
                                xytext=(dx, dy), fontsize=7.5,
                                bbox=dict(boxstyle="round,pad=0.15", fc="white", ec="none", alpha=0.85))
                if res.optimo:
                    ox, oy, oz = res.optimo
                    ax.plot(ox, oy, "r*", ms=18, label=f"Óptimo ({ox:g}, {oy:g})  Z={oz:g}")
                    # recta de isoutilidad que pasa por el óptimo
                    if abs(c2) > 1e-12:
                        ax.plot(g, (oz - c1 * g) / c2, "r--", lw=1.2, label=f"Z = {oz:g}")
                ax.set_xlim(-lim*0.02, lim); ax.set_ylim(-lim*0.02, lim)
                ax.set_xlabel(f"x₁ = {n1}"); ax.set_ylabel(f"x₂ = {n2}")
                ax.grid(alpha=0.3); ax.legend(fontsize=7, loc="upper right", framealpha=0.95)
                st.pyplot(fig)

                if res.estado == "optimo":
                    ox, oy, oz = res.optimo
                    st.success(f"**Solución óptima:** x₁ = {ox:g} ({n1}), x₂ = {oy:g} ({n2}) → "
                               f"**Z = {oz:g}**")
                    if res.multiples:
                        st.info("Hay **óptimos alternos** (la recta de Z es paralela a una restricción): "
                                + "; ".join(f"({a:g}, {b:g})" for a, b, _ in res.optimos_alternos)
                                + " y todo el segmento entre ellos.")
                    st.caption(f"Verificación independiente (linprog): Z = {res.verificacion_linprog:g}")
                    st.markdown("**Vértices de la región factible**")
                    st.dataframe(pd.DataFrame(res.vertices, columns=["x₁", "x₂", "Z"]),
                                 width="stretch", hide_index=True)
                    st.markdown("**Holgura / uso de recursos en el óptimo**")
                    st.dataframe(pd.DataFrame({
                        "Restricción": df["Nombre"].tolist(),
                        "Holgura": res.holguras,
                        "Estado": ["Activa (agotada)" if h < 1e-6 else "Con holgura" for h in res.holguras]}),
                        width="stretch", hide_index=True)
                    if d_wi != 0:
                        k_idx = df["Nombre"].tolist().index(k_wi)
                        restr2 = [dict(r) for r in restr]
                        restr2[k_idx]["b"] = restr2[k_idx]["b"] + d_wi
                        res2 = resolver(c1, c2, restr2, maximizar=(obj == "Maximizar"))
                        st.markdown(f"**Escenario what-if:** b de «{k_wi}» pasa de {restr[k_idx]['b']:g} a {restr2[k_idx]['b']:g}")
                        if res2.estado != "optimo":
                            st.warning(f"Con este cambio el problema queda: {res2.estado.replace('_', ' ')}.")
                        else:
                            x1b, x2b, zb = res.optimo
                            x1n, x2n, zn = res2.optimo
                            st.dataframe(pd.DataFrame({
                                "Caso": ["Base", "Escenario", "Cambio"],
                                "x₁": [x1b, x1n, x1n - x1b], "x₂": [x2b, x2n, x2n - x2b],
                                "Z": [zb, zn, zn - zb]}), width="stretch", hide_index=True)
                            pre = (zn - zb) / d_wi
                            pre = 0.0 if abs(pre) < 1e-9 else pre
                            st.info(f"ΔZ/Δb = {pre:g} por unidad adicional de «{k_wi}» "
                                    "(precio sombra, válido mientras no cambie el conjunto de restricciones activas).")

with tab2:
    st.subheader("Teoría de Colas · M/M/s (M/M/1 si s = 1)")
    st.markdown("Ejemplo precargado: **caja de la cafetería en hora pico** (valores ilustrativos). "
                "Todas las tasas deben estar en la misma unidad de tiempo (aquí: hora).")
    ci, co = st.columns([1, 1.8])
    with ci:
        lam = st.number_input("λ: llegadas por hora", min_value=0.01, value=40.0)
        mu = st.number_input("μ: atenciones por hora de UN cajero", min_value=0.01, value=25.0)
        st.markdown("**Costos (miles COP por hora)**")
        cs = st.number_input("Costo por cajero activo", min_value=0.0, value=8.0)
        cw = st.number_input("Costo de espera por cliente", min_value=0.0, value=12.0)
        base_esp = st.radio("El costo de espera se aplica a", ["Clientes en el sistema (L)", "Clientes en cola (Lq)"])
        smin, smax = st.slider("Rango de cajeros a evaluar", 1, 12, (1, 5))
        s_sel = st.number_input("Cajeros s para el detalle", min_value=1, max_value=20, value=3, step=1)
        t_min = st.number_input("t: minutos para P(espera > t)", min_value=0.0, value=5.0)
    with co:
        m = mms(lam, mu, int(s_sel))
        if not m.estable:
            st.error(f"Sistema INESTABLE con s = {int(s_sel)}: ρ = λ/(sμ) = {m.rho:.3f} ≥ 1. "
                     "La cola crece sin límite; se necesitan más servidores.")
        else:
            st.markdown(f"**Indicadores con s = {int(s_sel)}**")
            c = st.columns(4)
            c[0].metric("ρ (utilización)", f"{m.rho:.3f}")
            c[1].metric("P₀ (sistema vacío)", f"{m.P0:.4f}")
            c[2].metric("P(debe esperar)", f"{m.Pespera:.3f}")
            c[3].metric("P(Wq > t)", f"{prob_espera_mayor_t(m, t_min / 60):.3f}")
            c = st.columns(4)
            c[0].metric("L (en sistema)", f"{m.L:.3f}")
            c[1].metric("Lq (en cola)", f"{m.Lq:.3f}")
            c[2].metric("W (min en sistema)", f"{m.W * 60:.2f}")
            c[3].metric("Wq (min en cola)", f"{m.Wq * 60:.2f}")

        filas = tabla_costos(lam, mu, smin, smax, cs, cw,
                             "sistema" if base_esp.startswith("Clientes en el sistema") else "cola")
        dft = pd.DataFrame(filas)
        ok = dft[dft["estable"]] if "estable" in dft else dft
        st.markdown("**Costo total vs. número de cajeros**")
        if ok.empty:
            st.warning("Ningún s del rango es estable; aumente el rango de cajeros.")
        else:
            best = ok.loc[ok["costo_total"].idxmin()]
            st.success(f"**s óptimo = {int(best['s'])} cajeros** → costo total = "
                       f"{best['costo_total']:.2f} miles COP/hora (servicio {best['costo_servicio']:.2f} + espera {best['costo_espera']:.2f})")
            fig2, ax2 = plt.subplots(figsize=(6.5, 3.6))
            ax2.plot(ok["s"], ok["costo_servicio"], "o-", label="Costo de servicio")
            ax2.plot(ok["s"], ok["costo_espera"], "s-", label="Costo de espera")
            ax2.plot(ok["s"], ok["costo_total"], "k^-", lw=2, label="Costo total")
            ax2.axvline(best["s"], color="r", ls="--", alpha=.5)
            ax2.set_xlabel("Número de cajeros s"); ax2.set_ylabel("Miles COP / hora")
            ax2.set_xticks(list(ok["s"])); ax2.grid(alpha=.3); ax2.legend(fontsize=8)
            st.pyplot(fig2)
        mostrar = dft.copy()
        mostrar["estable"] = mostrar["estable"].map({True: "Sí", False: "NO (ρ ≥ 1)"})
        mostrar = mostrar.rename(columns={
            "s": "Cajeros s", "rho": "ρ", "estable": "¿Estable?", "L": "L", "Lq": "Lq",
            "W": "W (h)", "Wq": "Wq (h)", "costo_servicio": "Costo servicio",
            "costo_espera": "Costo espera", "costo_total": "Costo total"})
        fmt = {c: "{:.4f}" for c in ["ρ", "L", "Lq", "W (h)", "Wq (h)"]}
        fmt.update({c: "{:.2f}" for c in ["Costo servicio", "Costo espera", "Costo total"]})
        st.dataframe(mostrar.style.format(fmt, na_rep="—"), width="stretch", hide_index=True)

        if m.estable:
            N = 15
            fig3, ax3 = plt.subplots(figsize=(6.5, 2.8))
            ax3.bar(range(N + 1), [prob_n(m, n) for n in range(N + 1)])
            ax3.set_xlabel("n clientes en el sistema"); ax3.set_ylabel("Pₙ"); ax3.grid(alpha=.3)
            st.pyplot(fig3)
with tab3:
    st.subheader("Cadenas de Markov · proyección y estado estable")
    st.markdown("Ejemplo precargado: **¿a qué sitio almuerzan los estudiantes cada semana?** "
                "Estados: Cafetería Central, Cafetería del Bloque y Comida externa (valores ilustrativos). "
                "P[i][j] = probabilidad de pasar del estado i (esta semana) al j (la siguiente).")
    nombres_base = ["Central", "Bloque", "Externa", "Estado 4", "Estado 5", "Estado 6"]
    P_base = [[0.70, 0.20, 0.10], [0.25, 0.60, 0.15], [0.30, 0.20, 0.50]]
    mi, mo = st.columns([1, 1.8])
    with mi:
        N = st.number_input("Número de estados", min_value=2, max_value=6, value=3, step=1)
        N = int(N)
        nombres = [st.text_input(f"Nombre estado {i + 1}", nombres_base[i], key=f"nm{i}") for i in range(N)]
        if N == 3:
            P0 = pd.DataFrame(P_base, index=nombres, columns=nombres)
        else:
            P0 = pd.DataFrame(np.full((N, N), 1.0 / N), index=nombres, columns=nombres)
        st.markdown("**Matriz de transición P** (cada fila debe sumar 1)")
        Pdf = st.data_editor(P0, key=f"P_{N}", width="stretch")
        st.markdown("**Distribución inicial π(0)** (debe sumar 1)")
        ini0 = pd.DataFrame([[0.5, 0.3, 0.2] if N == 3 else [1.0 / N] * N], columns=nombres)
        inic = st.data_editor(ini0, key=f"pi0_{N}", hide_index=True, width="stretch")
        pasos = st.slider("Número de pasos n (semanas)", 1, 40, 4)
        poblacion = st.number_input("Población total (para convertir a personas)", min_value=1, value=1000, step=100)
        st.markdown("**Escenario what-if (opcional)**")
        P_base = Pdf.to_numpy(dtype=float)
        usar_wi = st.checkbox("Cambiar la probabilidad de permanecer en un estado")
        if usar_wi:
            sel_wi = st.selectbox("Estado cuya retención cambia", nombres)
            i_wi = nombres.index(sel_wi)
            r_wi = st.slider("Nueva probabilidad de permanecer (P[i][i])", 0.0, 1.0,
                             float(np.clip(P_base[i_wi, i_wi], 0, 1)), 0.01)
            st.caption("El resto de la fila se reparte en proporción a sus valores originales.")

    P = P_base.copy()
    P_original = P_base.copy()
    wi_activo = False
    if usar_wi and abs(P[i_wi].sum() - 1) < 1e-6 and P[i_wi, i_wi] < 1 - 1e-9:
        resto_old = 1 - P[i_wi, i_wi]
        fila = P[i_wi] * ((1 - r_wi) / resto_old)
        fila[i_wi] = r_wi
        P[i_wi] = fila
        wi_activo = True
    pi0 = inic.to_numpy(dtype=float)[0]
    with mo:
        errs = mk.validar(P)
        if abs(pi0.sum() - 1) > 1e-6 or (pi0 < 0).any():
            errs.append(f"π(0) debe ser no negativo y sumar 1 (suma actual: {pi0.sum():.4f}).")
        if errs:
            for e in errs:
                st.error(e)
        else:
            cl = mk.clasificar(P)
            tray = mk.proyectar(pi0, P, pasos)
            st.markdown("**Matriz de transición (mapa de calor)**")
            fig4, ax4 = plt.subplots(figsize=(4.6, 3.4))
            im = ax4.imshow(P, vmin=0, vmax=1, cmap="Blues")
            ax4.set_xticks(range(N)); ax4.set_xticklabels(nombres, fontsize=8)
            ax4.set_yticks(range(N)); ax4.set_yticklabels(nombres, fontsize=8)
            for i in range(N):
                for j in range(N):
                    ax4.text(j, i, f"{P[i, j]:.2f}", ha="center", va="center",
                             color="white" if P[i, j] > .55 else "black", fontsize=9)
            ax4.set_xlabel("Estado siguiente"); ax4.set_ylabel("Estado actual")
            st.pyplot(fig4)

            st.markdown(f"**Proyección a n = {pasos} pasos:** π(n) = π(0)·Pⁿ")
            tabla = pd.DataFrame(tray, columns=nombres)
            tabla.index.name = "n"
            st.dataframe(tabla.style.format("{:.4f}"), width="stretch")
            st.success("**π(" + str(pasos) + ") = (" + ", ".join(f"{v:.4f}" for v in tray[-1]) + ")**  →  "
                       + ", ".join(f"{nm}: {v * poblacion:.0f} personas" for nm, v in zip(nombres, tray[-1])))

            fig5, ax5 = plt.subplots(figsize=(6.5, 3.4))
            for k, nm in enumerate(nombres):
                ax5.plot(range(pasos + 1), tray[:, k], "o-", ms=3, label=nm)
            pie = mk.estado_estable(P)
            if pie is not None:
                for k in range(N):
                    ax5.axhline(pie[k], color=f"C{k}", ls=":", alpha=.6)
            ax5.set_xlabel("n (semanas)"); ax5.set_ylabel("Probabilidad"); ax5.grid(alpha=.3); ax5.legend(fontsize=8)
            st.pyplot(fig5)

            if wi_activo:
                st.info(f"Escenario what-if activo: P[{sel_wi}][{sel_wi}] = {r_wi:.2f}. "
                        "Fila modificada: " + ", ".join(f"{nombres[j]} = {P[i_wi, j]:.4f}" for j in range(N)))
            st.markdown("**Largo plazo (estado estable):** se resuelve πP = π con Σπᵢ = 1")
            st.write(f"Irreducible: **{'sí' if cl.irreducible else 'no'}** · "
                     f"Aperiódica: **{'sí' if cl.aperiodica else 'no'}** · "
                     f"Ergódica: **{'sí' if cl.ergodica else 'no'}** · "
                     f"Estados absorbentes: **{', '.join(nombres[i] for i in cl.absorbentes) or 'ninguno'}**")
            if pie is None:
                st.warning("La cadena NO es irreducible: no existe una distribución estable única que no dependa "
                           "del estado inicial (hay estados absorbentes o clases separadas). "
                           "Se muestra solo la proyección a n pasos.")
            else:
                if not cl.ergodica:
                    st.warning("La cadena es irreducible pero PERIÓDICA: π existe y es única, pero π(n) "
                               "no converge a π (oscila).")
                else:
                    st.success("La cadena es ergódica: π(n) converge a π sin importar el estado inicial.")
                M = mk.tiempos_primera_pasada(P)
                est = pd.DataFrame({"Estado": nombres, "π (largo plazo)": pie,
                                    "Personas": pie * poblacion,
                                    "Tiempo medio de retorno 1/π (pasos)": 1 / pie})
                st.dataframe(est.style.format({"π (largo plazo)": "{:.4f}", "Personas": "{:.0f}",
                                               "Tiempo medio de retorno 1/π (pasos)": "{:.3f}"}),
                             width="stretch", hide_index=True)
                if wi_activo:
                    pib = mk.estado_estable(P_original)
                    if pib is not None:
                        comp = pd.DataFrame({"Estado": nombres, "π base": pib, "π escenario": pie,
                                             "Cambio (pp)": (pie - pib) * 100,
                                             "Personas base": pib * poblacion,
                                             "Personas escenario": pie * poblacion})
                        st.markdown("**Comparación: base vs. escenario**")
                        st.dataframe(comp.style.format({"π base": "{:.4f}", "π escenario": "{:.4f}",
                                                        "Cambio (pp)": "{:+.2f}", "Personas base": "{:.0f}",
                                                        "Personas escenario": "{:.0f}"}),
                                     width="stretch", hide_index=True)
                if cl.ergodica:
                    n_conv = mk.pasos_hasta_convergencia(pi0, P, 1e-3)
                    st.caption(f"Con tolerancia 0.001, π(n) alcanza a π en n = {n_conv} pasos.")
                st.markdown("**Tiempo medio de primera pasada** (fila → columna, en pasos)")
                st.dataframe(pd.DataFrame(M, index=nombres, columns=nombres).style.format("{:.3f}"),
                             width="stretch")
                st.markdown("**Verificación:** ‖πP − π‖∞ = " + f"{np.max(np.abs(pie @ P - pie)):.2e}")
