# -*- coding: utf-8 -*-
"""Gera os SVGs desta aula a partir dos DADOS REAIS (nada é ilustrativo à toa).

    uv run python disciplinas/ai-business-society/aulas/machine-learning/assets/gerar.py

Os SVGs usam variáveis CSS do tema (--ink, --accent, ...) em vez de cores fixas.
Por isso o layout `diagrama` embute o arquivo INLINE: assim o desenho acompanha
o modo claro/escuro do deck e sai vetorial (nítido) no PDF.
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier

AQUI = Path(__file__).resolve().parent
CSV = AQUI.parent / "notas" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"   # fora de assets/: não é publicado
SEED = 42

INK, ACC, ACC2, MUT, RULE = (
    "var(--ink)", "var(--accent)", "var(--accent-2)", "var(--muted)", "var(--rule)")
FONTE = "ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, sans-serif"


def svg(w, h, corpo):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" '
            f'font-family="{FONTE}" role="img">{corpo}</svg>')


# O SVG entra no slide com viewBox de 1180 unidades ocupando ~149cqh de largura,
# então 1 unidade ≈ 0,126cqh. O tema usa 2,5cqh para legenda e 3,6cqh para corpo
# — ou seja, NADA abaixo de ~20 unidades é legível projetado. PISO é esse mínimo.
PISO = 20


def texto(x, y, s, tam=PISO, cor=INK, peso="400", anc="middle"):
    tam = max(tam, PISO)
    return (f'<text x="{x}" y="{y}" font-size="{tam}" fill="{cor}" font-weight="{peso}" '
            f'text-anchor="{anc}" dominant-baseline="middle">{s}</text>')


def caixa(x, y, w, h, cor=RULE, preench="none", raio=8, larg=1.5):
    return (f'<rect x="{x - w/2:.1f}" y="{y - h/2:.1f}" width="{w}" height="{h}" rx="{raio}" '
            f'fill="{preench}" stroke="{cor}" stroke-width="{larg}"/>')


def linha(x1, y1, x2, y2, cor=RULE, larg=1.5):
    return f'<path d="M{x1:.1f},{y1:.1f} L{x2:.1f},{y2:.1f}" stroke="{cor}" stroke-width="{larg}" fill="none"/>'


# --------------------------------------------------------------------------- #
def treinar():
    df = pd.read_csv(CSV)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce").fillna(0)
    V = ["tenure", "MonthlyCharges", "TotalCharges", "Contract", "InternetService",
         "TechSupport", "OnlineSecurity", "PaymentMethod", "PaperlessBilling",
         "SeniorCitizen", "Partner", "Dependents", "gender"]
    X = pd.get_dummies(df[V], drop_first=True)
    y = (df["Churn"] == "Yes").astype(int)
    return train_test_split(X, y, test_size=0.25, stratify=y, random_state=SEED)


# --------------------------------------------------------------------------- #
def arvore_profundidade_2(Xtr, ytr):
    """A árvore de profundidade 2 de verdade — cortes e percentuais do modelo."""
    m = DecisionTreeClassifier(max_depth=2, random_state=SEED).fit(Xtr, ytr)
    t = m.tree_
    n = [int(v) for v in t.weighted_n_node_samples]
    pc = [t.value[i][0][1] for i in range(t.node_count)]   # fração que cancelou

    p = []
    W, H = 1180, 470
    yr, yi, yf = 54, 200, 348          # raiz · nós internos · folhas
    xr, xL, xR = 590, 300, 880
    xs = [120, 480, 700, 1060]

    # arestas
    for (x1, y1, x2, y2, rot, dx) in [
        (xr, yr + 37, xL, yi - 37, "yes", -46), (xr, yr + 37, xR, yi - 37, "no", 46),
        (xL, yi + 37, xs[0], yf - 43, "no", -34), (xL, yi + 37, xs[1], yf - 43, "yes", 34),
        (xR, yi + 37, xs[2], yf - 43, "no", -34), (xR, yi + 37, xs[3], yf - 43, "yes", 34),
    ]:
        p.append(linha(x1, y1, x2, y2))
        p.append(texto((x1 + x2) / 2 + dx, (y1 + y2) / 2, rot, 20, MUT, "600"))

    # raiz e nós internos
    for (x, yy, rot, idx, w) in [(xr, yr, "tenure ≤ 10.5 months?", 0, 330),
                                 (xL, yi, "Fiber optic?", 1, 230),
                                 (xR, yi, "Fiber optic?", 4, 230)]:
        p.append(caixa(x, yy, w, 74, ACC, "none", 8, 2))
        p.append(texto(x, yy - 15, rot, 23, INK, "600"))
        p.append(texto(x, yy + 16, f"{n[idx]:,} · {pc[idx]:.1%} cancelled", 20, MUT))

    # folhas
    rotulos = ["no fiber", "fiber", "no fiber", "fiber"]
    for x, idx, rot in zip(xs, [2, 3, 5, 6], rotulos):
        cancela = pc[idx] >= 0.50
        cor = ACC2 if cancela else RULE
        p.append(caixa(x, yf, 224, 86, cor, "none", 8, 2.5 if cancela else 1.5))
        p.append(texto(x, yf - 26, rot, 20, MUT, "600"))
        p.append(texto(x, yf + 4, f"{pc[idx]:.1%} cancelled", 25, ACC2 if cancela else INK, "700"))
        p.append(texto(x, yf + 34, f"of {n[idx]:,}", 20, MUT))
        p.append(texto(x, yf + 70, "→ CANCELS" if cancela else "→ stays", 21,
                       ACC2 if cancela else MUT, "700"))
    p.append(texto(W / 2, H - 14,
                   "Two questions. That is the whole model.", 24, INK, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def crescimento(Xtr, ytr):
    """Quantas folhas cada profundidade cria — e quantas guardam 1 só cliente."""
    info = []
    for d in (2, 5, 30):
        m = DecisionTreeClassifier(max_depth=d, random_state=SEED).fit(Xtr, ytr)
        folhas = m.tree_.children_left == -1
        tam = m.tree_.weighted_n_node_samples[folhas]
        info.append((d, int(folhas.sum()), int((tam == 1).sum()), m.get_depth()))

    p, W, H = [], 1180, 470
    for k, (d, nf, um, real) in enumerate(info):
        cx = 200 + k * 390
        p.append(texto(cx, 30, f"Depth {d}", 21, INK, "700"))
        # silhueta: um nível de pontos por profundidade (saturando na largura)
        niveis = min(real, 7)
        for lv in range(niveis + 1):
            qtd = min(2 ** lv, 34)
            meia = 30 + lv * (145 - 30) / max(niveis, 1)   # meia-largura do nível
            yy = 74 + lv * 34
            for j in range(qtd):
                x = cx + meia * 2 * (j - (qtd - 1) / 2) / max(qtd - 1, 1)
                ultimo = lv == niveis
                p.append(f'<circle cx="{x:.1f}" cy="{yy}" r="{3.4 if ultimo else 2.6}" '
                         f'fill="{ACC2 if (ultimo and d == 30) else ACC}" '
                         f'opacity="{0.95 if ultimo else 0.45}"/>')
        if real > niveis:
            p.append(texto(cx, 74 + (niveis + 1) * 34, "⋮", 22, ACC, "700"))
        p.append(texto(cx, 372, f"{nf:,} leaves", 20, ACC2 if d == 30 else INK, "700"))
        p.append(texto(cx, 398, f"{len(Xtr) / nf:.0f} customers per leaf", 13, MUT))
        if um:
            p.append(texto(cx, 424, f"{um} leaves hold ONE customer", 13, ACC2, "700"))
    p.append(texto(W / 2, H - 14,
                   "A leaf with one customer has not learned a pattern. It has stored a person.",
                   14, MUT, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def ajuste():
    """Os MESMOS pontos, três modelos: subajuste · equilíbrio · sobreajuste."""
    rng = np.random.default_rng(7)
    xd = np.linspace(0.06, 0.94, 16)
    verdade = lambda x: 0.55 + 0.42 * np.sin(2 * np.pi * x - 0.6)
    yd = verdade(xd) + rng.normal(0, 0.075, xd.size)

    # legendas em duas linhas: em 20u uma linha só invade o painel vizinho
    paineis = [("Underfitting", 1, "too simple —|misses the pattern", "bad", "bad"),
               ("Balance", 4, "caught the pattern,|ignored the noise", "good", "good"),
               ("Overfitting", 13, "chases every point,|noise included", "great", "bad")]

    p, W, H = [], 1180, 470
    PW, PH, y0 = 330, 168, 58
    for k, (nome, grau, legenda, tr, te) in enumerate(paineis):
        x0 = 40 + k * 385
        mx = lambda v: x0 + v * PW
        my = lambda v: y0 + (1 - v) * PH
        p.append(texto(x0 + PW / 2, 30, nome, 26, ACC2 if te == "bad" else ACC, "700"))
        p.append(f'<clipPath id="painel{k}"><rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" rx="6"/></clipPath>')
        p.append(f'<rect x="{x0}" y="{y0}" width="{PW}" height="{PH}" fill="none" '
                 f'stroke="{RULE}" stroke-width="1.5" rx="6"/>')
        # curva ajustada (mesmos pontos nos três painéis)
        c = np.polyfit(xd, yd, grau)
        xx = np.linspace(0.02, 0.98, 260)
        yy = np.clip(np.polyval(c, xx), -0.25, 1.25)
        d = " ".join(f"{'M' if i == 0 else 'L'}{mx(a):.1f},{my(b):.1f}" for i, (a, b) in enumerate(zip(xx, yy)))
        p.append(f'<path d="{d}" stroke="{ACC2 if te == "bad" else ACC}" stroke-width="3" fill="none" '
                 f'stroke-linejoin="round" clip-path="url(#painel{k})"/>')
        # os mesmos 16 pontos, sempre
        for a, b in zip(xd, yd):
            p.append(f'<circle cx="{mx(a):.1f}" cy="{my(b):.1f}" r="4.6" fill="{INK}" opacity="0.72"/>')
        for li, lg in enumerate(legenda.split("|")):
            p.append(texto(x0 + PW / 2, y0 + PH + 32 + li * 26, lg, 20, MUT))
        p.append(texto(x0 + PW / 2, y0 + PH + 96, f"training {tr}", 21, MUT, "600"))
        p.append(texto(x0 + PW / 2, y0 + PH + 124, f"new customers {te}", 23,
                       ACC2 if te == "bad" else ACC, "700"))
    p.append(texto(W / 2, H - 12, "Same 16 customers in all three panels. Only the model changed.", 22, INK, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def matriz_confusao(Xtr, ytr, Xte, yte):
    """O quadro clássico de 4 casas — nome técnico + o que significa + o preço."""
    from sklearn.metrics import confusion_matrix
    m = DecisionTreeClassifier(max_depth=5, random_state=SEED).fit(Xtr, ytr)
    pred = (m.predict_proba(Xte)[:, 1] >= 0.50).astype(int)
    tn, fp, fn, tp = confusion_matrix(yte, pred, labels=[0, 1]).ravel()

    p, W, H = [], 1180, 470
    CW, CH = 384, 156                     # célula
    gx, gy = 300, 96                     # canto superior esquerdo da grade

    # cabeçalhos das colunas (o que o MODELO disse)
    p.append(texto(gx + CW, 26, "THE MODEL SAYS", 20, MUT, "700"))
    p.append(texto(gx + CW / 2, 62, "stays", 24, INK, "700"))
    p.append(texto(gx + CW * 1.5, 62, "cancels", 24, INK, "700"))
    # cabeçalhos das linhas (a REALIDADE)
    p.append(f'<text x="112" y="{gy + CH}" font-size="{PISO}" fill="{MUT}" font-weight="700" '
             f'text-anchor="middle" transform="rotate(-90 112 {gy + CH})">WHAT ACTUALLY HAPPENED</text>')
    p.append(texto(232, gy + CH / 2, "stayed", 24, INK, "700", "end"))
    p.append(texto(232, gy + CH * 1.5, "cancelled", 24, INK, "700", "end"))

    casas = [
        (0, 0, "TRUE NEGATIVE", "Said stay — they stayed", "Nothing to do. Correct.", tn, False),
        (1, 0, "FALSE POSITIVE", "Said cancel — they stayed", "FALSE ALARM · you paid the offer for nothing", fp, True),
        (0, 1, "FALSE NEGATIVE", "Said stay — they left", "MISSED · the customer walked out", fn, True),
        (1, 1, "TRUE POSITIVE", "Said cancel — they cancelled", "Caught it. The offer gets a chance.", tp, False),
    ]
    for col, lin, nome, oque, preco, valor, erro in casas:
        cx, cy = gx + col * CW + CW / 2, gy + lin * CH + CH / 2
        cor = ACC2 if erro else ACC
        p.append(f'<rect x="{cx - CW/2 + 5:.0f}" y="{cy - CH/2 + 5:.0f}" width="{CW - 10}" height="{CH - 10}" '
                 f'rx="10" fill="{cor}" fill-opacity="{0.13 if erro else 0.07}" '
                 f'stroke="{cor}" stroke-width="{2.5 if erro else 1.5}"/>')
        p.append(texto(cx, cy - 56, nome, 20, cor, "700"))
        p.append(texto(cx, cy - 22, f"{valor:,}", 34, INK, "700"))
        p.append(texto(cx, cy + 12, oque, 20, INK))
        p.append(texto(cx, cy + 44, preco, 20, cor if erro else MUT, "600" if erro else "400"))

    p.append(texto(W / 2, H - 16, "The two orange squares are the two ways to be wrong — and they do NOT cost the same.",
                   25, INK, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def metricas(Xtr, ytr, Xte, yte):
    """Acurácia · precisão · recall: qual pedaço da matriz cada uma olha."""
    from sklearn.metrics import confusion_matrix
    m = DecisionTreeClassifier(max_depth=5, random_state=SEED).fit(Xtr, ytr)
    pred = (m.predict_proba(Xte)[:, 1] >= 0.50).astype(int)
    tn, fp, fn, tp = confusion_matrix(yte, pred, labels=[0, 1]).ravel()
    n = len(yte)

    paineis = [
        ("ACCURACY", "of EVERYONE|how often was I right?",
         [(0, 0), (1, 1)], [(0, 0), (0, 1), (1, 0), (1, 1)],
         "TP + TN", "TP + TN + FP + FN",
         f"{tp + tn:,}", f"{n:,}", (tn + tp) / n),
        ("PRECISION", "when I said CANCEL|was I right?",
         [(1, 1)], [(1, 0), (1, 1)],
         "TP", "TP + FP",
         f"{tp}", f"{tp + fp}", tp / (tp + fp)),
        ("RECALL", "of those who CANCELLED|how many did I catch?",
         [(1, 1)], [(0, 1), (1, 1)],
         "TP", "TP + FN",
         f"{tp}", f"{tp + fn}", tp / (tp + fn)),
    ]
    rotulos = {(0, 0): "TN", (1, 0): "FP", (0, 1): "FN", (1, 1): "TP"}

    p, W, H = [], 1180, 470
    CW, CH = 82, 60
    for k, (nome, pergunta, num, den, f_num, f_den, v_num, v_den, valor) in enumerate(paineis):
        x0 = 40 + k * 385
        cx0 = x0 + 330 / 2 - CW                      # grade centrada no painel
        p.append(texto(x0 + 165, 30, nome, 26, ACC, "700"))
        for li, linha_ in enumerate(pergunta.split("|")):
            p.append(texto(x0 + 165, 62 + li * 26, linha_, 20, MUT))
        for col in (0, 1):
            for lin in (0, 1):
                x, y = cx0 + col * CW, 124 + lin * CH
                no_num, no_den = (col, lin) in num, (col, lin) in den
                p.append(f'<rect x="{x}" y="{y}" width="{CW}" height="{CH}" '
                         f'fill="{ACC if no_num else "none"}" fill-opacity="{0.30 if no_num else 0}" '
                         f'stroke="{ACC if no_den else RULE}" stroke-width="{2.5 if no_den else 1}"/>')
                p.append(texto(x + CW / 2, y + CH / 2, rotulos[(col, lin)], 15,
                               ACC if no_den else MUT, "700" if no_den else "400"))
        cx = x0 + 165
        # fórmula em símbolos (fração de verdade: traço horizontal)
        p.append(texto(cx, 272, f_num, 21, ACC, "700"))
        p.append(f'<path d="M{cx - 104},288 L{cx + 104},288" stroke="{ACC}" stroke-width="1.8"/>')
        p.append(texto(cx, 304, f_den, 21, ACC, "700"))
        # a mesma fração com os números desta aula
        p.append(texto(cx, 344, f"{v_num} ÷ {v_den}", 20, MUT, "600"))
        p.append(texto(cx, 390, f"{valor:.1%}", 40, ACC, "700"))
    p.append(texto(W / 2, 450, "Same model, same customers, same matrix — three very different numbers.",
                   24, INK, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def familias(X, y):
    """Seis famílias no MESMO problema, medidas 20 vezes cada.

    O desenho é um dot plot com amplitude: o ponto é a média, a barra é o
    intervalo entre a pior e a melhor partição. O que ensina é a SOBREPOSIÇÃO.
    """
    import warnings
    warnings.filterwarnings("ignore")
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier, HistGradientBoostingClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score
    from sklearn.neighbors import KNeighborsClassifier
    from sklearn.neural_network import MLPClassifier
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler

    esc = lambda m: make_pipeline(StandardScaler(), m)
    fam = {
        "Logistic regression": esc(LogisticRegression(max_iter=2000, random_state=SEED)),
        "Gradient boosting":   HistGradientBoostingClassifier(random_state=SEED),
        "Decision tree":       DecisionTreeClassifier(max_depth=5, random_state=SEED),
        "Random forest":       RandomForestClassifier(n_estimators=300, random_state=SEED, n_jobs=-1),
        "Nearest neighbours":  esc(KNeighborsClassifier(n_neighbors=25)),
        "Neural network":      esc(MLPClassifier(hidden_layer_sizes=(64, 32), max_iter=400, random_state=SEED)),
        "“Nobody cancels”":    DummyClassifier(strategy="most_frequent"),
    }
    # 140 treinos: fica em cache para ajuste de layout não custar minutos.
    # Apague o .json (ou rode com --recalcular) se o dado ou os modelos mudarem.
    cache = AQUI / ".familias-cv.json"
    if cache.exists() and "--recalcular" not in sys.argv:
        dados = [tuple(d) for d in json.loads(cache.read_text())]
    else:
        cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=4, random_state=SEED)
        dados = []
        for nome, m in fam.items():
            sc = cross_val_score(m, X, y, cv=cv, scoring="accuracy", n_jobs=-1)
            dados.append((nome, float(sc.mean()), float(sc.min()), float(sc.max())))
        cache.write_text(json.dumps(dados, ensure_ascii=False))

    p, W, H = [], 1180, 470
    x0, x1 = 300, 1080
    lo, hi = 0.72, 0.83
    mx = lambda v: x0 + (v - lo) / (hi - lo) * (x1 - x0)

    # eixo
    for t in np.arange(0.72, 0.831, 0.02):
        p.append(f'<path d="M{mx(t):.1f},64 L{mx(t):.1f},372" stroke="{RULE}" stroke-width="1"/>')
        p.append(texto(mx(t), 392, f"{t:.0%}", 12, MUT))
    p.append(texto((x0 + x1) / 2, 30, "Accuracy — mean of 20 measurements, with the full range", 14, MUT, "600"))

    for k, (nome, med, mn, mx_) in enumerate(dados):
        yy = 84 + k * 42
        base = nome.startswith("“Nobody")
        cor = MUT if base else (ACC2 if nome == "Neural network" else ACC)
        p.append(texto(x0 - 18, yy, nome, 15, INK if not base else MUT,
                       "700" if k == 0 else "400", "end"))
        p.append(f'<path d="M{mx(mn):.1f},{yy} L{mx(mx_):.1f},{yy}" stroke="{cor}" '
                 f'stroke-width="7" stroke-linecap="round" opacity="0.28"/>')
        p.append(f'<circle cx="{mx(med):.1f}" cy="{yy}" r="7" fill="{cor}"/>')
        p.append(texto(x1 + 58, yy, f"{med:.1%}", 15, cor, "700"))

    p.append(texto(W / 2, 442,
                   "The bars overlap — one model swings 3.3 points across partitions.",
                   26, INK, "600"))
    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
def limiar(Xtr, ytr, Xte, yte):
    """O limiar como uma LINHA sobre a distribuição de probabilidades.

    Histograma espelhado: quem cancelou para cima, quem ficou para baixo, cada
    grupo em % DELE MESMO (senão o desbalanceamento de 26,5% achata o laranja).
    A linha vertical é a decisão — e as quatro regiões são as quatro casas da
    matriz de confusão, agora vistas de outro ângulo.
    """
    m = DecisionTreeClassifier(max_depth=5, random_state=SEED).fit(Xtr, ytr)
    pr = m.predict_proba(Xte)[:, 1]
    yv = np.asarray(yte)

    passo = 0.05
    bins = np.arange(0, 0.95, passo)
    canc = np.array([((pr >= b) & (pr < b + passo) & (yv == 1)).sum() for b in bins])
    fica = np.array([((pr >= b) & (pr < b + passo) & (yv == 0)).sum() for b in bins])
    pc, pf = canc / canc.sum(), fica / fica.sum()

    p, W, H = [], 1180, 470
    x0, x1 = 268, 1132          # margem esquerda larga: os rótulos de grupo moram lá
    meio, alt = 250, 116
    mx = lambda v: x0 + v / 0.95 * (x1 - x0)
    esc = max(pc.max(), pf.max())

    T = 0.50
    p.append(f'<rect x="{mx(T):.1f}" y="{meio - alt - 40}" width="{x1 - mx(T):.1f}" '
             f'height="{2 * alt + 80}" fill="{ACC2}" fill-opacity="0.06"/>')

    for b, vc, vf in zip(bins, pc, pf):
        xa, larg = mx(b) + 1.5, (x1 - x0) * passo / 0.95 - 3
        if vc: p.append(f'<rect x="{xa:.1f}" y="{meio - 26 - vc/esc*alt:.1f}" width="{larg:.1f}" '
                        f'height="{vc/esc*alt:.1f}" fill="{ACC2}" rx="2"/>')
        if vf: p.append(f'<rect x="{xa:.1f}" y="{meio + 26:.1f}" width="{larg:.1f}" '
                        f'height="{vf/esc*alt:.1f}" fill="{ACC}" rx="2"/>')

    # eixo, entre as duas metades
    for t in np.arange(0, 0.91, 0.1):
        p.append(texto(mx(t), meio, f"{t:.1f}", 20, MUT))
    p.append(texto((x0 + x1) / 2, H - 16, "probability the model gives each customer  →", 21, MUT))

    # rótulos dos grupos: fora do gráfico, à esquerda, sem disputar espaço com nada
    p.append(texto(x0 - 24, meio - 74, "actually", 21, ACC2, "400", "end"))
    p.append(texto(x0 - 24, meio - 46, "CANCELLED", 23, ACC2, "700", "end"))
    p.append(texto(x0 - 24, meio + 46, "actually", 21, ACC, "400", "end"))
    p.append(texto(x0 - 24, meio + 74, "STAYED", 23, ACC, "700", "end"))

    # a linha da decisão
    for val, dash, rot, cor in [(0.20, "7,6", "0.20", MUT), (T, "", "0.50", INK)]:
        p.append(f'<path d="M{mx(val):.1f},{meio - alt - 46} L{mx(val):.1f},{meio + alt + 50}" '
                 f'stroke="{cor}" stroke-width="{3 if not dash else 2}" '
                 f'{f'stroke-dasharray="{dash}"' if dash else ""}/>')
        p.append(texto(mx(val), meio - alt - 66, rot, 22, cor, "700"))
    p.append(f'<path d="M{mx(0.47):.1f},{meio + alt + 68} L{mx(0.23):.1f},{meio + alt + 68}" '
             f'stroke="{MUT}" stroke-width="2" marker-end="url(#pta)"/>')
    p.append('<defs><marker id="pta" markerWidth="9" markerHeight="9" refX="7" refY="4.5" '
             f'orient="auto"><path d="M0,0 L9,4.5 L0,9 z" fill="{MUT}"/></marker></defs>')

    # regiões: acima do topo do laranja e abaixo do fundo do azul
    for xx, yy, rot, cor in [
        (mx(0.28), meio - alt - 20, "missed (FN)", ACC2),
        (mx(0.74), meio - alt - 20, "caught (TP)", ACC2),
        (mx(0.28), meio + alt + 24, "left alone (TN)", ACC),
        (mx(0.74), meio + alt + 24, "false alarm (FP)", ACC),
    ]:
        p.append(texto(xx, yy, rot, 21, cor, "700"))

    return svg(W, H, "".join(p))


# --------------------------------------------------------------------------- #
if __name__ == "__main__":
    Xtr, Xte, ytr, yte = treinar()
    for nome, conteudo in [("arvore-profundidade-2.svg", arvore_profundidade_2(Xtr, ytr)),
                           ("arvore-crescimento.svg", crescimento(Xtr, ytr)),
                           ("ajuste.svg", ajuste()),
                           ("matriz-confusao.svg", matriz_confusao(Xtr, ytr, Xte, yte)),
                           ("metricas.svg", metricas(Xtr, ytr, Xte, yte)),
                           ("limiar.svg", limiar(Xtr, ytr, Xte, yte)),
                           ("familias.svg", familias(pd.concat([Xtr, Xte]), pd.concat([ytr, yte])))]:
        (AQUI / nome).write_text(conteudo, encoding="utf-8")
        print(f"  ✓ {nome}  ({len(conteudo):,} bytes)")
