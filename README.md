# Proyecto Red: reparto de presupuesto y selección de participantes

Implementación reproducible del proyecto de Análisis y Diseño de Algoritmos.
El código usa la biblioteca estándar de Python para los algoritmos; `matplotlib`
es opcional y solo se necesita para generar las gráficas.

## Requisitos

- Python 3.10 o superior.
- Opcional: `pip install matplotlib`.

## Ejecución

Desde esta carpeta:

```powershell
python -m red_project.cli demo
python -m red_project.cli experiment --output results --repetitions 20
python -m unittest discover -s tests -v
```

El experimento genera:

- `results/times.csv`: una fila por repetición, con la semilla usada.
- `results/summary.csv`: promedio y desviación estándar por tamaño.
- `results/times.png`: comparación de tiempos de Greedy y exacto.
- `results/approximation.png`: calidad de Greedy respecto al óptimo.

Las instancias se generan con semillas deterministas para que los resultados
sean reproducibles.

## Organización

- [`red_project/allocation.py`](red_project/allocation.py): reparto cóncavo
  óptimo mediante cola de prioridad.
- [`red_project/selection.py`](red_project/selection.py): fuerza bruta,
  Greedy submodular y Greedy con presupuesto.
- [`red_project/variants.py`](red_project/variants.py): fallos por rondas y
  externalidades sobre vecinos.
- [`red_project/experiments.py`](red_project/experiments.py): generación,
  medición repetida, estadística y comparación experimental.
- [`report.md`](report.md): formalización, pruebas, complejidad y garantías.

La fuerza bruta se reserva para tamaños pequeños, porque su complejidad es
`O(C(N,k) * k)` y sirve como referencia óptima para medir la aproximación.

La garantía `1 - 1/e` se afirma únicamente para selección submodular monótona
con restricción de cardinalidad. La variante con costos usa densidad marginal
y mejor elemento individual como heurística para cobertura con presupuesto;
sus garantías son distintas. La variante de vecindarios se reporta por
separado y no recibe automáticamente la cota submodular.
