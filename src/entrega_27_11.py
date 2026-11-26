"""Refina a regressão logística no treino e depois avalia o teste reservado.

Uso:
    python src/entrega_27_11.py refinar
    python src/entrega_27_11.py avaliar
    python src/entrega_27_11.py verificar
"""

from __future__ import annotations

import argparse
import hashlib
import json

import joblib
import numpy as np
import pandas as pd
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from entrega_20_11 import ATRIBUTOS, BRUTO, RAIZ, SEMENTE, carregar_dados


RESULTADOS = RAIZ / "resultados"
MODELOS = RAIZ / "modelos"
ARQUIVO_MODELO = MODELOS / "modelo_27-11.joblib"
ARQUIVO_TESTE = RESULTADOS / "resumo_teste_27-11.json"
CS = (0.01, 0.1, 1.0, 10.0, 100.0)
CLASSES = (1, 2, 3)
NOMES = {1: "Kama", 2: "Rosa", 3: "Canadian"}


def particoes():
    dados = carregar_dados()
    resumo_anterior = json.loads((RESULTADOS / "treinamento_20-11.json").read_text(encoding="utf-8"))
    hash_atual = hashlib.sha256(BRUTO.read_bytes()).hexdigest()
    if hash_atual != resumo_anterior["sha256_fonte"]:
        raise ValueError("O arquivo bruto mudou desde a entrega de 20/11")

    x = dados[ATRIBUTOS]
    y = dados["classe"].astype(int)
    x_treino, x_teste, y_treino, y_teste = train_test_split(
        x, y, test_size=0.20, random_state=SEMENTE, stratify=y
    )
    particoes_salvas = pd.read_csv(RESULTADOS / "particoes_20-11.csv")
    particoes_atuais = pd.DataFrame(
        {
            "linha_original": np.arange(1, len(dados) + 1),
            "particao": ["treino" if i in x_treino.index else "teste" for i in dados.index],
        }
    )
    pd.testing.assert_frame_equal(particoes_salvas, particoes_atuais)
    if len(x_treino) != 168 or len(x_teste) != 42:
        raise AssertionError("O tamanho das partições mudou")
    return x_treino, x_teste, y_treino, y_teste, hash_atual


def construir_pipeline(c: float) -> Pipeline:
    return Pipeline(
        [
            ("selecao", SelectKBest(score_func=f_classif, k=4)),
            ("padronizacao", StandardScaler()),
            ("classificador", LogisticRegression(C=c, max_iter=2000, random_state=SEMENTE)),
        ]
    )


def refinar() -> None:
    if ARQUIVO_TESTE.exists():
        raise RuntimeError("O teste já foi avaliado; não refinar novamente após consultar seus resultados")
    x_treino, _, y_treino, _, hash_atual = particoes()
    validacao = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEMENTE)
    linhas = []
    for c in CS:
        notas = cross_validate(
            construir_pipeline(c),
            x_treino,
            y_treino,
            cv=validacao,
            scoring={"f1_macro": "f1_macro", "acuracia": "accuracy"},
            return_train_score=True,
            n_jobs=1,
        )
        linhas.append(
            {
                "C": c,
                "f1_macro_cv": float(notas["test_f1_macro"].mean()),
                "desvio_f1_cv": float(notas["test_f1_macro"].std(ddof=1)),
                "acuracia_cv": float(notas["test_acuracia"].mean()),
                "acuracia_treino_cv": float(notas["train_acuracia"].mean()),
            }
        )

    comparacao = pd.DataFrame(linhas).sort_values(
        ["f1_macro_cv", "acuracia_cv", "C"], ascending=[False, False, True]
    )
    melhor = comparacao.iloc[0]
    limiar = float(melhor["f1_macro_cv"] - melhor["desvio_f1_cv"] / np.sqrt(5))
    # Menor C = regularização mais forte; a regra favorece o modelo mais simples.
    escolhido = comparacao.loc[comparacao["f1_macro_cv"] >= limiar].sort_values("C").iloc[0]
    c_final = float(escolhido["C"])
    modelo = construir_pipeline(c_final).fit(x_treino, y_treino)
    atributos_finais = x_treino.columns[modelo.named_steps["selecao"].get_support()].tolist()

    RESULTADOS.mkdir(exist_ok=True)
    MODELOS.mkdir(exist_ok=True)
    comparacao.to_csv(RESULTADOS / "refino_27-11.csv", index=False)
    joblib.dump(modelo, ARQUIVO_MODELO)
    configuracao = {
        "origem": "entrega de 20/11: regressão logística com 4 atributos",
        "sha256_fonte": hash_atual,
        "sha256_modelo": hashlib.sha256(ARQUIVO_MODELO.read_bytes()).hexdigest(),
        "particoes": "resultados/particoes_20-11.csv",
        "validacao": "5 dobras estratificadas, shuffle=True, random_state=42, apenas treino",
        "valores_C_testados": list(CS),
        "criterio": "maior F1 macro médio; regra de 1 erro padrão; dentre elegíveis, menor C",
        "melhor_f1_macro_cv": float(melhor["f1_macro_cv"]),
        "limiar_1_erro_padrao": limiar,
        "C_escolhido": c_final,
        "f1_macro_cv_escolhido": float(escolhido["f1_macro_cv"]),
        "acuracia_cv_escolhida": float(escolhido["acuracia_cv"]),
        "atributos_finais": atributos_finais,
        "acuracia_treino_ajustado": float(modelo.score(x_treino, y_treino)),
        "avaliacao_teste_executada_nesta_etapa": False,
    }
    (RESULTADOS / "configuracao_27-11.json").write_text(
        json.dumps(configuracao, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(comparacao.to_string(index=False, float_format=lambda n: f"{n:.4f}"))
    print(f"\nLimiar de 1 erro padrão: {limiar:.4f}")
    print(f"C fixado antes do teste: {c_final:g}")
    print(f"Atributos: {', '.join(atributos_finais)}")


def avaliar() -> None:
    if ARQUIVO_TESTE.exists():
        raise RuntimeError("O teste já foi avaliado; consulte os resultados salvos")
    x_treino, x_teste, _, y_teste, hash_atual = particoes()
    configuracao = json.loads((RESULTADOS / "configuracao_27-11.json").read_text(encoding="utf-8"))
    if hash_atual != configuracao["sha256_fonte"]:
        raise ValueError("O arquivo bruto mudou depois de fixar o modelo")
    if hashlib.sha256(ARQUIVO_MODELO.read_bytes()).hexdigest() != configuracao["sha256_modelo"]:
        raise ValueError("O modelo mudou depois de ser fixado")
    modelo = joblib.load(ARQUIVO_MODELO)
    if float(modelo.named_steps["classificador"].C) != configuracao["C_escolhido"]:
        raise ValueError("O modelo salvo não corresponde à configuração fixada")
    atributos = x_treino.columns[modelo.named_steps["selecao"].get_support()].tolist()
    if atributos != configuracao["atributos_finais"]:
        raise ValueError("Os atributos salvos não correspondem à configuração fixada")

    previsoes = modelo.predict(x_teste)
    probabilidades = modelo.predict_proba(x_teste)
    if tuple(modelo.classes_) != CLASSES:
        raise ValueError("A ordem das classes do modelo mudou")
    matriz = confusion_matrix(y_teste, previsoes, labels=CLASSES)
    relatorio = classification_report(
        y_teste, previsoes, labels=CLASSES, output_dict=True, zero_division=0
    )
    acuracia = float(accuracy_score(y_teste, previsoes))
    f1_macro = float(f1_score(y_teste, previsoes, average="macro"))

    linhas_teste = pd.DataFrame(
        {
            "linha_original": x_teste.index.to_numpy() + 1,
            "classe_real": y_teste.to_numpy(),
            "classe_prevista": previsoes,
            "acertou": (y_teste.to_numpy() == previsoes),
            "prob_kama": probabilidades[:, 0],
            "prob_rosa": probabilidades[:, 1],
            "prob_canadian": probabilidades[:, 2],
        },
        index=x_teste.index,
    )
    linhas_teste = pd.concat([linhas_teste, x_teste], axis=1).sort_values("linha_original")
    linhas_teste.to_csv(RESULTADOS / "previsoes_teste_27-11.csv", index=False)
    erros = linhas_teste.loc[~linhas_teste["acertou"]].copy()
    erros.to_csv(RESULTADOS / "erros_27-11.csv", index=False)
    pd.DataFrame(
        matriz,
        index=[f"real_{NOMES[c]}" for c in CLASSES],
        columns=[f"previsto_{NOMES[c]}" for c in CLASSES],
    ).to_csv(RESULTADOS / "matriz_confusao_27-11.csv", index_label="classe_real")
    pd.DataFrame(
        [
            {"classe": NOMES[c], **relatorio[str(c)]}
            for c in CLASSES
        ]
    ).to_csv(RESULTADOS / "metricas_por_classe_27-11.csv", index=False)
    resumo = {
        "C_fixado_antes_do_teste": configuracao["C_escolhido"],
        "atributos": atributos,
        "total_teste": len(x_teste),
        "acertos": int((linhas_teste["acertou"]).sum()),
        "erros": len(erros),
        "acuracia_teste": acuracia,
        "f1_macro_teste": f1_macro,
        "matriz_confusao_linhas_reais_colunas_previstas": matriz.tolist(),
        "linhas_originais_com_erro": erros["linha_original"].tolist(),
        "nenhum_ajuste_apos_abrir_teste": True,
    }
    ARQUIVO_TESTE.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Acurácia no teste: {acuracia:.4f} ({resumo['acertos']}/{len(x_teste)})")
    print(f"F1 macro no teste: {f1_macro:.4f}")
    print("Matriz de confusão (linhas reais, colunas previstas):")
    print(matriz)
    print("Erros (linhas originais):", resumo["linhas_originais_com_erro"])


def verificar() -> None:
    """Confere os artefatos salvos sem alterar o modelo nem os resultados."""
    x_treino, x_teste, _, y_teste, hash_atual = particoes()
    configuracao = json.loads((RESULTADOS / "configuracao_27-11.json").read_text(encoding="utf-8"))
    resumo = json.loads(ARQUIVO_TESTE.read_text(encoding="utf-8"))
    if hash_atual != configuracao["sha256_fonte"]:
        raise AssertionError("Fonte diferente da usada no refino")
    if hashlib.sha256(ARQUIVO_MODELO.read_bytes()).hexdigest() != configuracao["sha256_modelo"]:
        raise AssertionError("Modelo diferente do que foi fixado")
    modelo = joblib.load(ARQUIVO_MODELO)
    atributos = x_treino.columns[modelo.named_steps["selecao"].get_support()].tolist()
    if atributos != configuracao["atributos_finais"]:
        raise AssertionError("Atributos diferentes da configuração fixada")
    previsoes = modelo.predict(x_teste)
    salvas = pd.read_csv(RESULTADOS / "previsoes_teste_27-11.csv").sort_values("linha_original")
    ordem = np.argsort(x_teste.index.to_numpy())
    np.testing.assert_array_equal(salvas["linha_original"].to_numpy(), x_teste.index.to_numpy()[ordem] + 1)
    np.testing.assert_array_equal(salvas["classe_real"].to_numpy(), y_teste.to_numpy()[ordem])
    np.testing.assert_array_equal(salvas["classe_prevista"].to_numpy(), previsoes[ordem])
    if not np.isclose(accuracy_score(y_teste, previsoes), resumo["acuracia_teste"]):
        raise AssertionError("Acurácia salva diferente da reproduzida")
    if not np.isclose(f1_score(y_teste, previsoes, average="macro"), resumo["f1_macro_teste"]):
        raise AssertionError("F1 salvo diferente do reproduzido")
    if confusion_matrix(y_teste, previsoes, labels=CLASSES).tolist() != resumo[
        "matriz_confusao_linhas_reais_colunas_previstas"
    ]:
        raise AssertionError("Matriz salva diferente da reproduzida")
    print("Artefatos de 27/11 conferidos: fonte, modelo, previsões e métricas coincidem")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("fase", choices=("refinar", "avaliar", "verificar"))
    args = parser.parse_args()
    if args.fase == "refinar":
        refinar()
    elif args.fase == "avaliar":
        avaliar()
    else:
        verificar()
