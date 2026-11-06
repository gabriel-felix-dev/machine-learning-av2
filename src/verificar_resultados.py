"""Verifica integridade dos dados e coerência dos artefatos executados."""
import hashlib
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix

ROOT = Path(__file__).resolve().parents[1]


def main():
    summary = json.loads((ROOT / "resultados/resumo_execucao.json").read_text(encoding="utf-8"))
    digest = hashlib.sha256((ROOT / "dados/seeds_dataset.txt").read_bytes()).hexdigest()
    assert digest == summary["auditoria"]["sha256_antes"] == summary["auditoria"]["sha256_depois"]
    train = pd.read_csv(ROOT / "dados/X_treino.csv", index_col=0)
    test = pd.read_csv(ROOT / "dados/X_teste.csv", index_col=0)
    assert len(train) == 168 and len(test) == 42
    assert set(train.index).isdisjoint(test.index)
    assert set(train.index) | set(test.index) == set(range(1, 211))
    folds = pd.read_csv(ROOT / "resultados/folds_validacao.csv")
    assert set(folds.linha_origem) == set(train.index)
    assert folds.linha_origem.value_counts().eq(1).all()
    assert set(folds.fold) == set(range(1, 6))
    assert len(pd.read_csv(ROOT / "resultados/busca_hiperparametros.csv")) == 240
    predictions = pd.read_csv(ROOT / "resultados/previsoes_teste.csv", index_col=0)
    model = joblib.load(ROOT / "modelos/seeds_arvore.joblib")
    pred = model["pipeline"].predict(test)
    assert np.array_equal(pred, predictions.prev_arvore_refinada.to_numpy())
    for row in summary["teste"]:
        name = row["modelo"]
        values = predictions[f"prev_{name}"]
        cm = confusion_matrix(predictions.classe, values, labels=[1, 2, 3])
        assert np.array_equal(cm, summary["matrizes_confusao"][name])
        assert int(np.trace(cm)) == row["acertos"]
        assert row["acertos"] + row["erros"] == 42
        assert np.isclose(np.trace(cm)/42, row["acuracia_teste"])
    error_ids = {item["linha_origem"] for item in summary["erros_finais"]}
    assert error_ids == set(predictions.index[predictions.classe.ne(predictions.prev_arvore_refinada)])
    demo = ROOT / "resultados/previsoes_exemplo.csv"
    if demo.exists():
        demo_data = pd.read_csv(demo)
        assert np.array_equal(demo_data.classe_prevista, model["pipeline"].predict(demo_data[model["features"]]))
    print("OK: bruto, partições, folds, grade, modelo salvo, previsões, métricas, matrizes e erros coerentes.")


if __name__ == "__main__":
    main()
