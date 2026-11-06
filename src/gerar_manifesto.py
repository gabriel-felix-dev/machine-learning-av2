"""Lista arquivos finais, estado em relação ao início e SHA-256; exclui temporários."""
import csv
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREEXISTING = {"AGENTS.md", "README", "projeto_av2_seeds.md", "entrega_06-11_seeds.md",
               "prompt_agente_ia.md", "slide-machine-learning.pdf", "dados/seeds_dataset.txt"}
OUTPUT = "resultados/manifesto_arquivos.csv"


def main():
    rows=[]
    for file in sorted(ROOT.rglob("*")):
        if not file.is_file():
            continue
        relative=file.relative_to(ROOT)
        if any(p in {".git", ".venv", ".build", "__pycache__", "node_modules"} or p.startswith(".chart-data-") for p in relative.parts):
            continue
        name=relative.as_posix()
        if name == OUTPUT:
            continue  # Evita auto-hash recursivo.
        status="atualizado" if name == "projeto_av2_seeds.md" else "preexistente_preservado" if name in PREEXISTING else "criado"
        rows.append({"arquivo":name,"estado":status,"bytes":file.stat().st_size,
                     "sha256":hashlib.sha256(file.read_bytes()).hexdigest()})
    with (ROOT / OUTPUT).open("w", encoding="utf-8", newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=["arquivo","estado","bytes","sha256"])
        writer.writeheader(); writer.writerows(rows)
    print(f"Manifesto: {len(rows)} arquivos (o próprio manifesto fica fora de sua lista).")


if __name__ == "__main__":
    main()
