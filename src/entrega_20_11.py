"""Reproduz a divisão, escolhe um classificador e treina a entrega de 20/11.

O conjunto de teste é separado, mas nunca é passado a seleção, ajuste ou avaliação.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier


RAIZ = Path(__file__).resolve().parents[1]
BRUTO = RAIZ / "dados" / "dataset-seeds.txt"
ATRIBUTOS = [
    "area",
    "perimetro",
    "compacidade",
    "comprimento_grao",
    "largura_grao",
    "coeficiente_assimetria",
    "comprimento_sulco",
]
COLUNAS = ATRIBUTOS + ["classe"]
SEMENTE = 42


def carregar_dados() -> pd.DataFrame:
    dados = pd.read_csv(BRUTO, sep=r"\s+", header=None, names=COLUNAS)
    if dados.shape != (210, 8):
        raise ValueError(f"Dimensão inesperada: {dados.shape}")
    if dados.isna().any().any() or not np.isfinite(dados.to_numpy()).all():
        raise ValueError("O arquivo bruto contém valor ausente ou não finito")
    if dados.duplicated().any():
        raise ValueError("O arquivo bruto contém linhas duplicadas")
    if dados["classe"].value_counts().sort_index().to_dict() != {1: 70, 2: 70, 3: 70}:
        raise ValueError("Distribuição das classes inesperada")
    return dados


def candidatos() -> dict[str, object]:
    modelos: dict[str, object] = {
        "referencia_classe_mais_frequente": DummyClassifier(strategy="most_frequent"),
    }
    for k in (4, 7):
        modelos[f"regressao_logistica_{k}"] = Pipeline(
            [
                ("selecao", SelectKBest(score_func=f_classif, k=k)),
                ("padronizacao", StandardScaler()),
                ("classificador", LogisticRegression(max_iter=2000, random_state=SEMENTE)),
            ]
        )
        modelos[f"arvore_decisao_{k}"] = Pipeline(
            [
                ("selecao", SelectKBest(score_func=f_classif, k=k)),
                ("classificador", DecisionTreeClassifier(random_state=SEMENTE)),
            ]
        )
    return modelos


def executar() -> None:
    dados = carregar_dados()
    x = dados[ATRIBUTOS]
    y = dados["classe"].astype(int)
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x, y, test_size=0.20, random_state=SEMENTE, stratify=y
    )
    if len(x_treino) != 168 or len(x_teste) != 42:
        raise AssertionError("A divisão 80/20 não foi reproduzida")
    if y_treino.value_counts().sort_index().to_dict() != {1: 56, 2: 56, 3: 56}:
        raise AssertionError("O treino não ficou estratificado")
    if y_teste.value_counts().sort_index().to_dict() != {1: 14, 2: 14, 3: 14}:
        raise AssertionError("O teste não ficou estratificado")
    if not x_treino.index.intersection(x_teste.index).empty:
        raise AssertionError("Há linhas em ambas as partições")

    validacao = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    modelos = candidatos()
    linhas = []
    for nome, modelo in modelos.items():
        notas = cross_validate(
            modelo,
            x_treino,
            y_treino,
            cv=validacao,
            scoring={"f1_macro": "f1_macro", "acuracia": "accuracy"},
            return_train_score=True,
            n_jobs=1,
        )
        linhas.append(
            {
                "modelo": nome,
                "atributos": 7 if nome.endswith("_7") else 4 if nome.endswith("_4") else 0,
                "f1_macro_cv": float(notas["test_f1_macro"].mean()),
                "desvio_f1_cv": float(notas["test_f1_macro"].std(ddof=1)),
                "acuracia_cv": float(notas["test_acuracia"].mean()),
                "acuracia_treino_cv": float(notas["train_acuracia"].mean()),
            }
        )

    comparacao = pd.DataFrame(linhas).sort_values(
        ["f1_macro_cv", "acuracia_cv", "atributos", "modelo"],
        ascending=[False, False, True, True],
    )
    melhor_cv = comparacao.iloc[0]
    limiar_1ep = float(melhor_cv["f1_macro_cv"] - melhor_cv["desvio_f1_cv"] / np.sqrt(5))
    elegiveis = comparacao.loc[comparacao["f1_macro_cv"] >= limiar_1ep]
    vencedor = elegiveis.sort_values(
        ["atributos", "f1_macro_cv", "acuracia_cv", "modelo"],
        ascending=[True, False, False, True],
    ).iloc[0]
    nome_escolhido = str(vencedor["modelo"])
    if nome_escolhido == "referencia_classe_mais_frequente":
        raise RuntimeError("A referência simples venceu; é preciso rever a escolha do modelo")
    modelo_final = modelos[nome_escolhido].fit(x_treino, y_treino)
    mascara = modelo_final.named_steps["selecao"].get_support()
    atributos_finais = x_treino.columns[mascara].tolist()

    pasta_resultados = RAIZ / "resultados"
    pasta_modelos = RAIZ / "modelos"
    pasta_resultados.mkdir(exist_ok=True)
    pasta_modelos.mkdir(exist_ok=True)
    comparacao.to_csv(pasta_resultados / "validacao_20-11.csv", index=False)
    particoes = pd.DataFrame(
        {
            "linha_original": np.arange(1, len(dados) + 1),
            "particao": ["treino" if indice in x_treino.index else "teste" for indice in dados.index],
        }
    )
    particoes.to_csv(pasta_resultados / "particoes_20-11.csv", index=False)
    joblib.dump(modelo_final, pasta_modelos / "modelo_20-11.joblib")
    resumo = {
        "fonte": str(BRUTO.relative_to(RAIZ)).replace("\\", "/"),
        "sha256_fonte": hashlib.sha256(BRUTO.read_bytes()).hexdigest(),
        "semente": SEMENTE,
        "treino": {"total": 168, "por_classe": {"1": 56, "2": 56, "3": 56}},
        "teste_reservado": {"total": 42, "por_classe": {"1": 14, "2": 14, "3": 14}},
        "validacao": "StratifiedKFold: 5 dobras, embaralhamento e semente 42; somente treino",
        "criterio_escolha": "Regra de 1 erro padrão do melhor F1 macro CV; dentre os elegíveis, menos atributos, maior F1, maior acurácia e nome",
        "melhor_f1_macro_cv": float(melhor_cv["f1_macro_cv"]),
        "limiar_1_erro_padrao": limiar_1ep,
        "modelo_escolhido": nome_escolhido,
        "atributos_selecionados_no_treino": atributos_finais,
        "f1_macro_cv": float(vencedor["f1_macro_cv"]),
        "acuracia_cv": float(vencedor["acuracia_cv"]),
        "acuracia_no_treino_ajustado": float(modelo_final.score(x_treino, y_treino)),
        "avaliacao_no_teste_executada": False,
        "versoes": {"pandas": pd.__version__, "scikit_learn": sklearn.__version__},
    }
    (pasta_resultados / "treinamento_20-11.json").write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(comparacao.to_string(index=False, float_format=lambda valor: f"{valor:.4f}"))
    print(f"\nLimiar de 1 erro padrão: {limiar_1ep:.4f}")
    print(f"\nModelo treinado: {nome_escolhido}")
    print(f"Atributos selecionados: {', '.join(atributos_finais)}")
    print("Teste reservado: nenhuma avaliação realizada")


if __name__ == "__main__":
    executar()
