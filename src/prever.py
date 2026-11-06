"""Inferência local em CSV com as mesmas sete colunas numéricas do treino."""
import argparse
from pathlib import Path
import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path)
    parser.add_argument("--saida", type=Path, default=ROOT / "resultados/previsoes_novas.csv")
    args = parser.parse_args()
    bundle = joblib.load(ROOT / "modelos/seeds_arvore.joblib")
    data = pd.read_csv(args.entrada)
    X = data.loc[:, bundle["features"]].apply(pd.to_numeric, errors="raise")
    if X.empty or not np.isfinite(X.to_numpy()).all() or not X.gt(0).all().all() or not X.compacidade.between(0,1).all():
        raise ValueError("Entrada inválida: medidas numéricas finitas, positivas, compacidade entre 0 e 1.")
    model = bundle["pipeline"]
    output = data.copy()
    output["classe_prevista"] = model.predict(X)
    output["variedade_prevista"] = output.classe_prevista.map(bundle["classes"])
    for k, p in zip(model.classes_, model.predict_proba(X).T):
        output[f"prob_classe_{k}"] = p
    reference = pd.read_csv(ROOT / "modelos/referencia_treino.csv", index_col=0)
    outside = X.lt(reference["min"]) | X.gt(reference["max"])
    output["fora_intervalo_treino"] = outside.any(axis=1)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(args.saida, index=False)
    print(f"{len(output)} previsões em {args.saida}. Fora do intervalo de treino: {int(outside.any(axis=1).sum())}.")


if __name__ == "__main__":
    main()
