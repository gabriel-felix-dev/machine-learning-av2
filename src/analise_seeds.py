"""AV2 Seeds: auditoria, EDA no treino, seleção em Pipeline e teste final.

Execute: python src/analise_seeds.py
Os caminhos são relativos à raiz do projeto, independentemente do cwd.
"""
from __future__ import annotations

import hashlib
import importlib.metadata
import json
import platform
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, f1_score, roc_auc_score, roc_curve)
from sklearn.model_selection import GridSearchCV, StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["area", "perimetro", "compacidade", "comprimento", "largura", "assimetria", "sulco"]
LABELS = {1: "Kama", 2: "Rosa", 3: "Canadian"}
COLORS = ["#27675e", "#c68b31", "#596d9b"]
RAW_HASH = "1f3f83c0d8485ae9148061389d19628607e3f5660e3d6f40ec9102fb398bb12f"
SEED = 42


def save_json(name, value):
    path = ROOT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def csv(frame, name, index=True):
    frame.to_csv(ROOT / name, index=index, encoding="utf-8", float_format="%.10g")


def figure(name):
    plt.savefig(ROOT / "graficos" / f"{name}.png", dpi=180, bbox_inches="tight", facecolor="white")
    plt.savefig(ROOT / "graficos" / f"{name}.svg", bbox_inches="tight", facecolor="white")
    plt.close()


def load_validate():
    raw = ROOT / "dados/seeds_dataset.txt"
    digest = hashlib.sha256(raw.read_bytes()).hexdigest()
    if digest != RAW_HASH:
        raise ValueError("O bruto difere do SHA-256 registrado. Investigue antes de executar.")
    widths = pd.Series([len(line.split()) for line in raw.read_text().splitlines() if line.strip()])
    if len(widths) != 210 or not widths.eq(8).all():
        raise ValueError("Esperadas 210 linhas com exatamente oito valores.")
    data = pd.read_csv(raw, sep=r"\s+", header=None, names=FEATURES + ["classe"])
    data = data.apply(pd.to_numeric, errors="raise")
    if data.isna().any().any() or not np.isfinite(data.to_numpy()).all():
        raise ValueError("Dados ausentes ou não finitos.")
    if not data.classe.isin(LABELS).all() or not set(data.classe) == set(LABELS):
        raise ValueError("Classes inválidas.")
    if not data[FEATURES].gt(0).all().all() or not data.compacidade.between(0, 1).all():
        raise ValueError("Medidas fora das restrições de consistência.")
    if data.duplicated().any() or data[FEATURES].duplicated().any():
        raise ValueError("Duplicatas detectadas. Rever política de grupos antes da divisão.")
    data[FEATURES] = data[FEATURES].astype(float)
    data["classe"] = data["classe"].astype(int)
    data.index = pd.Index(range(1, len(data) + 1), name="linha_origem")
    quality = {"sha256_antes": digest, "linhas": len(data), "colunas_originais": len(data.columns),
               "ausentes": int(data.isna().sum().sum()), "duplicatas_linhas": int(data.duplicated().sum()),
               "duplicatas_X": int(data[FEATURES].duplicated().sum()),
               "tipos": data.dtypes.astype(str).to_dict(), "classes": data.classe.value_counts().sort_index().to_dict(),
               "medidas_nao_positivas": int((data[FEATURES] <= 0).sum().sum()),
               "compacidade_residuo_maximo": float(abs(data.compacidade - 4 * np.pi * data.area / data.perimetro**2).max()),
               "alteracoes": "Apenas separação dos campos, nomes e tipos. Nenhum valor corrigido ou registro excluído."}
    return data, quality


def eda(train):
    X = train[FEATURES]
    csv(X.describe().T, "resultados/resumo_treino.csv")
    csv(train.groupby("classe")[FEATURES].agg(["mean", "median", "std", "min", "max"]), "resultados/resumo_por_classe_treino.csv")
    corr = X.corr()
    csv(corr, "resultados/correlacao_treino.csv")
    q1, q3 = X.quantile(.25), X.quantile(.75)
    flags = (X.lt(q1 - 1.5 * (q3 - q1)) | X.gt(q3 + 1.5 * (q3 - q1)))
    csv(flags.astype(int), "resultados/extremos_iqr_treino.csv")
    csv(pd.DataFrame({"q1": q1, "q3": q3, "limite_inferior": q1-1.5*(q3-q1),
                      "limite_superior": q3+1.5*(q3-q1), "sinalizados": flags.sum()}), "resultados/limites_iqr_treino.csv")
    counts = train.classe.value_counts().sort_index()
    plt.figure(figsize=(7, 4))
    plt.bar([LABELS[k] for k in counts.index], counts.values, color=COLORS)
    for i, n in enumerate(counts):
        plt.text(i, n + .5, str(n), ha="center")
    plt.ylim(0, 65); plt.ylabel("Grãos"); plt.title("Classes no conjunto de treino (n = 168)")
    figure("01_classes_treino")
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
    for ax, feature in zip(axes.flat, FEATURES):
        bp = ax.boxplot([train.loc[train.classe.eq(k), feature] for k in LABELS],
                        tick_labels=list(LABELS.values()), patch_artist=True)
        for patch, color in zip(bp["boxes"], COLORS):
            patch.set_facecolor(color); patch.set_alpha(.65)
        ax.set_title(feature); ax.grid(axis="y", alpha=.2)
    axes.flat[-1].set_visible(False)
    fig.suptitle("Distribuição das sete medidas por variedade • apenas treino")
    figure("02_boxplots_treino")
    fig, axes = plt.subplots(2, 4, figsize=(15, 7), constrained_layout=True)
    for ax, feature in zip(axes.flat, FEATURES):
        edges = np.histogram_bin_edges(X[feature], bins=10)
        for (k, label), color in zip(LABELS.items(), COLORS):
            ax.hist(train.loc[train.classe.eq(k), feature], bins=edges, alpha=.45, label=label, color=color)
        ax.set_title(feature); ax.set_ylabel("Grãos")
    axes.flat[-1].set_visible(False); axes.flat[0].legend(fontsize=8)
    fig.suptitle("Histogramas por variedade • apenas treino")
    figure("03_histogramas_treino")
    plt.figure(figsize=(8, 6)); plt.imshow(corr, vmin=-1, vmax=1, cmap="BrBG"); plt.colorbar(label="Correlação de Pearson")
    plt.xticks(range(7), FEATURES, rotation=35, ha="right"); plt.yticks(range(7), FEATURES)
    for i in range(7):
        for j in range(7):
            plt.text(j, i, f"{corr.iloc[i,j]:.2f}", ha="center", va="center", color="white" if abs(corr.iloc[i,j]) > .6 else "black", fontsize=9)
    plt.title("Redundância entre atributos • treino")
    figure("04_correlacoes_treino")
    plt.figure(figsize=(8, 5))
    for (k, label), color in zip(LABELS.items(), COLORS):
        sub = train[train.classe.eq(k)]
        plt.scatter(sub.largura, sub.sulco, label=label, color=color, alpha=.8)
    plt.xlabel("Largura do grão"); plt.ylabel("Comprimento do sulco"); plt.legend(); plt.title("Dispersão das medidas • treino")
    figure("05_dispersao_treino")
    return {"extremos_iqr_por_atributo": flags.sum().to_dict(), "graos_com_extremo_iqr": int(flags.any(axis=1).sum()),
            "correlacao_area_perimetro": float(corr.loc["area", "perimetro"]),
            "medias_por_classe": train.groupby("classe")[FEATURES].mean().to_dict()}


def pipeline(k="all"):
    return Pipeline([("selecao", SelectKBest(f_classif, k=k).set_output(transform="pandas")),
                     ("arvore", DecisionTreeClassifier(random_state=SEED))])


def refit_index(results):
    """Desempate determinístico declarado no protocolo, sem consultar teste."""
    f = results["mean_test_f1_macro"]
    candidates = np.flatnonzero(np.isclose(f, np.max(f), rtol=0, atol=1e-12))
    def key(i):
        p = results["params"][i]
        k = 7 if p["selecao__k"] == "all" else p["selecao__k"]
        depth = p["arvore__max_depth"] or 999
        return (-results["mean_test_accuracy"][i], k, depth,
                -p["arvore__min_samples_leaf"], -p["arvore__ccp_alpha"])
    return int(min(candidates, key=key))


def wilson(correct, n):
    z = 1.959963984540054; p = correct / n
    den = 1 + z*z/n
    center = (p + z*z/(2*n))/den
    half = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/den
    return [float(center-half), float(center+half)]


def main():
    for folder in ["resultados", "graficos", "modelos"]:
        (ROOT / folder).mkdir(exist_ok=True)
    plt.rcParams.update({"font.family": "DejaVu Sans", "axes.spines.top": False, "axes.spines.right": False})
    data, quality = load_validate()
    X, y = data[FEATURES], data["classe"]
    # Primeiro a divisão. Nunca ajustar seletores em X completo.
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, stratify=y, random_state=SEED)
    assert set(X_train.index).isdisjoint(X_test.index)
    assert len(X_train) + len(X_test) == len(data)
    train = data.loc[X_train.index]
    part = pd.Series("treino", index=data.index, name="particao")
    part.loc[X_test.index] = "teste"
    derived = data.assign(variedade=data.classe.map(LABELS), particao=part)
    csv(derived, "dados/seeds_tratado.csv")
    csv(part.to_frame(), "resultados/particoes.csv")
    for name, frame in [("X_treino", X_train), ("X_teste", X_test), ("y_treino", y_train.to_frame()), ("y_teste", y_test.to_frame())]:
        csv(frame, f"dados/{name}.csv")
    distribution = pd.crosstab(part, data.classe).rename(columns=LABELS)
    csv(distribution, "resultados/distribuicao_particoes.csv")
    eda_summary = eda(train)
    # Ranking descritivo no treino. Pipelines abaixo reaprendem ranking em cada fold.
    ranking_selector = SelectKBest(f_classif, k=3).fit(X_train, y_train)
    ranking = pd.DataFrame({"atributo": FEATURES, "F_ANOVA": ranking_selector.scores_,
                            "p_valor_exploratorio": ranking_selector.pvalues_, "candidato_k3": ranking_selector.get_support()})
    ranking = ranking.sort_values("F_ANOVA", ascending=False)
    csv(ranking, "resultados/ranking_atributos_treino.csv", index=False)
    plt.figure(figsize=(9, 4)); plt.barh(ranking.atributo[::-1], ranking.F_ANOVA[::-1], color="#27675e")
    plt.xlabel("Estatística F (ANOVA univariada)"); plt.title("Ranking supervisionado ajustado somente no treino")
    figure("06_selecao_atributos")
    cv = list(StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED).split(X_train, y_train))
    folds = []
    for fold, (fit_ids, val_ids) in enumerate(cv, 1):
        assert set(fit_ids).isdisjoint(val_ids)
        folds.extend({"fold": fold, "linha_origem": int(X_train.index[i]), "papel": "validacao"} for i in val_ids)
    csv(pd.DataFrame(folds), "resultados/folds_validacao.csv", index=False)
    initial = {"referencia": DummyClassifier(strategy="most_frequent"), "arvore_7": pipeline(), "arvore_k3": pipeline(3)}
    cv_rows = []; cv_folds = []
    for name, model in initial.items():
        scores = cross_validate(model, X_train, y_train, cv=cv, scoring={"accuracy": "accuracy", "f1_macro": "f1_macro"}, return_train_score=True)
        cv_rows.append({"modelo": name, "acuracia_cv_media": float(scores["test_accuracy"].mean()),
                        "acuracia_cv_dp": float(scores["test_accuracy"].std()), "f1_macro_cv_media": float(scores["test_f1_macro"].mean()),
                        "f1_macro_cv_dp": float(scores["test_f1_macro"].std()), "acuracia_treino_cv": float(scores["train_accuracy"].mean())})
        cv_folds.extend({"modelo": name, "fold": i+1, "acuracia": float(a), "f1_macro": float(f)}
                        for i, (a, f) in enumerate(zip(scores["test_accuracy"], scores["test_f1_macro"])))
        model.fit(X_train, y_train)
    csv(pd.DataFrame(cv_folds), "resultados/comparacao_folds.csv", index=False)
    grid = {"selecao__k": [2, 3, 4, 5, 6, "all"], "arvore__max_depth": [2, 3, 4, 5, None],
            "arvore__min_samples_leaf": [1, 2, 4, 6], "arvore__ccp_alpha": [0.0, 0.01]}
    search = GridSearchCV(pipeline(), grid, scoring={"accuracy": "accuracy", "f1_macro": "f1_macro"},
                          refit=refit_index, cv=cv, n_jobs=1, return_train_score=True, error_score="raise")
    search.fit(X_train, y_train)
    results = pd.DataFrame(search.cv_results_)
    csv(results, "resultados/busca_hiperparametros.csv", index=False)
    best = search.best_estimator_
    idx = search.best_index_
    cv_rows.append({"modelo": "arvore_refinada", "acuracia_cv_media": float(results.loc[idx, "mean_test_accuracy"]),
                    "acuracia_cv_dp": float(results.loc[idx, "std_test_accuracy"]),
                    "f1_macro_cv_media": float(results.loc[idx, "mean_test_f1_macro"]),
                    "f1_macro_cv_dp": float(results.loc[idx, "std_test_f1_macro"]),
                    "acuracia_treino_cv": float(results.loc[idx, "mean_train_accuracy"])})
    cv_summary = pd.DataFrame(cv_rows)
    csv(cv_summary, "resultados/comparacao_validacao.csv", index=False)
    selection = best.named_steps["selecao"]
    selected = list(np.array(FEATURES)[selection.get_support()])
    tree = best.named_steps["arvore"]
    csv(pd.DataFrame({"atributo": selected, "importancia_gini": tree.feature_importances_}), "resultados/importancias_arvore_final.csv", index=False)
    # Congelamento acontece ANTES de qualquer predict no teste.
    frozen = {"metrica_escolha": "F1 macro médio em CV no treino", "parametros": search.best_params_,
              "atributos": selected, "profundidade_observada": int(tree.get_depth()), "folhas": int(tree.get_n_leaves()),
              "configuracoes": len(results), "random_state": SEED, "teste_usado_para_escolher": False}
    save_json("resultados/modelo_congelado.json", frozen)
    joblib.dump({"pipeline": best, "features": FEATURES, "classes": LABELS, "sha256_bruto": RAW_HASH}, ROOT / "modelos/seeds_arvore.joblib")
    csv(X_train.agg(["min", "max", "mean", "std"]).T, "modelos/referencia_treino.csv")
    initial["arvore_refinada"] = best
    test_rows = []; reports = {}; matrices = {}
    predictions = data.loc[X_test.index].copy()
    for name, model in initial.items():
        pred = model.predict(X_test)
        rep = classification_report(y_test, pred, labels=list(LABELS), target_names=list(LABELS.values()), output_dict=True, zero_division=0)
        cm = confusion_matrix(y_test, pred, labels=list(LABELS))
        reports[name] = rep; matrices[name] = cm.tolist()
        test_rows.append({"modelo": name, "acuracia_treino": float(model.score(X_train, y_train)),
                          "acuracia_teste": float(accuracy_score(y_test, pred)), "f1_macro_teste": float(f1_score(y_test, pred, average="macro")),
                          "acertos": int((pred == y_test).sum()), "erros": int((pred != y_test).sum())})
        predictions[f"prev_{name}"] = pred
        csv(pd.DataFrame({key: value for key, value in rep.items() if isinstance(value, dict)}).T,
            f"resultados/metricas_por_classe_{name}.csv")
        csv(pd.DataFrame(cm, index=list(LABELS.values()), columns=list(LABELS.values())).rename_axis("real"), f"resultados/matriz_confusao_{name}.csv")
    test_summary = pd.DataFrame(test_rows)
    csv(test_summary, "resultados/comparacao_teste.csv", index=False)
    csv(predictions, "resultados/previsoes_teste.csv")
    probabilities = best.predict_proba(X_test)
    error_data = predictions[predictions.classe.ne(predictions.prev_arvore_refinada)].copy()
    path = best.decision_path(X_test) if hasattr(best, "decision_path") else tree.decision_path(selection.transform(X_test))
    leaves = tree.apply(selection.transform(X_test))
    scaler = StandardScaler().fit(X_train)  # Exclusivo ao diagnóstico de vizinhos, não ao modelo.
    tr_scaled, te_scaled = scaler.transform(X_train), scaler.transform(X_test)
    errors_detail = []
    for row_id in error_data.index:
        pos = X_test.index.get_loc(row_id)
        leaf = int(leaves[pos]); rules = []
        for node in path.indices[path.indptr[pos]:path.indptr[pos+1]]:
            feature_index = tree.tree_.feature[node]
            if feature_index >= 0:
                feature = selected[feature_index]; threshold = float(tree.tree_.threshold[node]); value = float(X_test.loc[row_id, feature])
                rules.append(f"{feature}={value:.5g} {'<=' if value <= threshold else '>'} {threshold:.5g}")
        distances = np.linalg.norm(tr_scaled - te_scaled[pos], axis=1)
        nearest = np.argsort(distances)[:3]
        detail = {"linha_origem": int(row_id), "classe_real": int(y_test.loc[row_id]),
                  "variedade_real": LABELS[int(y_test.loc[row_id])], "classe_prevista": int(predictions.loc[row_id, "prev_arvore_refinada"]),
                  "variedade_prevista": LABELS[int(predictions.loc[row_id, "prev_arvore_refinada"])],
                  "folha": leaf, "amostras_treino_folha": int(tree.tree_.n_node_samples[leaf]),
                  "proporcoes_classes_folha": tree.tree_.value[leaf][0].tolist(),
                  "caminho": rules, "vizinhos_treino": [{"linha": int(X_train.index[j]), "classe": int(y_train.iloc[j]), "distancia_padronizada_7_atributos": float(distances[j])} for j in nearest]}
        errors_detail.append(detail)
    save_json("resultados/erros_detalhados.json", errors_detail)
    for k in LABELS:
        error_data[f"prob_classe_{k}"] = pd.Series(probabilities[:, list(tree.classes_).index(k)], index=X_test.index).loc[error_data.index]
    csv(error_data, "resultados/erros_teste.csv")
    cm = np.array(matrices["arvore_refinada"])
    fig, ax = plt.subplots(figsize=(6.5, 5)); im = ax.imshow(cm, cmap="Greens", vmin=0, vmax=14)
    ax.set_xticks(range(3), LABELS.values()); ax.set_yticks(range(3), LABELS.values())
    ax.set_xlabel("Classe prevista"); ax.set_ylabel("Classe real"); ax.set_title("Matriz de confusão final • teste reservado (n = 42)")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i,j], ha="center", va="center", color="white" if cm[i,j] >= 8 else "black", fontsize=18)
    figure("07_matriz_confusao_final")
    fig, ax = plt.subplots(figsize=(9, 4.8)); x = np.arange(4)
    ax.bar(x-.2, cv_summary.acuracia_cv_media, width=.4, color="#596d9b", label="Validação cruzada (treino)")
    ax.bar(x+.2, test_summary.acuracia_teste, width=.4, color="#27675e", label="Teste final")
    ax.set_xticks(x, ["Referência", "Árvore 7", "Árvore k=3", "Refinada"]); ax.set_ylim(0, 1.12); ax.set_ylabel("Acurácia"); ax.legend(loc="lower right")
    ax.set_title("Comparação predefinida • escolha somente pela validação")
    for i, value in enumerate(test_summary.acuracia_teste):
        ax.text(i+.2, value+.02, f"{value:.1%}", ha="center", fontsize=10)
    figure("08_comparacao_modelos")
    plt.figure(figsize=(17, max(7, tree.get_depth()*1.7)))
    plot_tree(tree, feature_names=selected, class_names=list(LABELS.values()), filled=True, rounded=True, fontsize=9, precision=3)
    plt.title("Árvore final • ajustada somente nos 168 registros de treino")
    figure("09_arvore_final")
    (ROOT / "modelos/regras_arvore.txt").write_text(export_text(tree, feature_names=selected), encoding="utf-8")
    # ROC OvR complementa as métricas de classificação listadas no slide, sem orientar tuning.
    auc = roc_auc_score(y_test, probabilities, labels=list(LABELS), multi_class="ovr", average="macro")
    plt.figure(figsize=(7, 5))
    for i, ((k, label), color) in enumerate(zip(LABELS.items(), COLORS)):
        fpr, tpr, _ = roc_curve(y_test.eq(k), probabilities[:, i])
        plt.plot(fpr, tpr, label=label, color=color)
    plt.plot([0,1], [0,1], "--", color="grey"); plt.xlabel("Taxa de falsos positivos"); plt.ylabel("Taxa de verdadeiros positivos")
    plt.legend(); plt.title(f"ROC um-contra-resto • AUC macro = {auc:.3f}")
    figure("10_roc_final")
    quality["sha256_depois"] = hashlib.sha256((ROOT / "dados/seeds_dataset.txt").read_bytes()).hexdigest()
    assert quality["sha256_depois"] == quality["sha256_antes"]
    save_json("resultados/validacao_dados.json", quality)
    final_result = test_rows[-1]
    summary = {"data_execucao": datetime.now(ZoneInfo("America/Sao_Paulo")).isoformat(), "data_academica_referencia": "2026-11-06",
               "python": platform.python_version(), "versoes": {p: importlib.metadata.version(p) for p in ["pandas", "numpy", "scipy", "scikit-learn", "matplotlib", "joblib"]},
               "auditoria": quality, "eda_treino": eda_summary, "divisao": {"treino": len(X_train), "teste": len(X_test), "semente": SEED, "por_classe_treino": y_train.value_counts().sort_index().to_dict(), "por_classe_teste": y_test.value_counts().sort_index().to_dict()},
               "candidatos_k3": ranking.loc[ranking.candidato_k3, "atributo"].tolist(), "modelo_final": frozen,
               "validacao": cv_rows, "teste": test_rows, "metricas_por_classe": reports,
               "matrizes_confusao": matrices, "erros_finais": errors_detail,
               "ic95_wilson_acuracia": wilson(final_result["acertos"], len(y_test)), "auc_macro_ovr": float(auc),
               "ganho_acuracia_pontos_percentuais": 100 * (final_result["acuracia_teste"] - test_rows[0]["acuracia_teste"])}
    save_json("resultados/resumo_execucao.json", summary)
    print(json.dumps({"final": final_result, "parametros": frozen, "ic95": summary["ic95_wilson_acuracia"], "bruto_preservado": True}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
