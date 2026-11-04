# Informe técnico: Proyecto Red

## 1. Formalización

En una ronda hay `N` nodos candidatos y se pueden seleccionar `k < N`.
Cada subconjunto `S` tiene utilidad `f(S)`. Para cobertura máxima, cada nodo
`i` representa un subconjunto `C_i` del universo `U` y
`f(S) = |∪_{i∈S} C_i|`. Esta función es monótona y submodular: la utilidad
marginal de `i` solo puede disminuir cuando crece el conjunto ya seleccionado.

En el reparto, `B` es el presupuesto entero y `u_i(x)` es creciente y cóncava.
Se representa mediante sus marginales discretos
`Δ_i(j) = u_i(j) - u_i(j-1)`, con `Δ_i(j+1) <= Δ_i(j)`.

## 2. Algoritmos

### 2.1 Reparto exacto

Se mantiene el siguiente marginal disponible de cada nodo en un max-heap.
Cada extracción elige el mayor marginal y después inserta el siguiente
marginal de ese nodo. La implementación está en
[`red_project/allocation.py`](red_project/allocation.py).

La inicialización cuesta `O(N)`. Se hacen como máximo `B` extracciones y cada
extracción/inserción cuesta `O(log N)`, por lo que:

`T(N,B) = O(N + B log N) = O(B log N)` cuando `B >= N`.

**Intercambio:** si una asignación contiene una unidad con marginal `a`
menor que otra unidad disponible con marginal `b >= a`, intercambiar ambas no
disminuye la utilidad. Repetir el intercambio produce exactamente las `B`
mayores marginales factibles. La concavidad garantiza que si una unidad está
disponible, todas sus predecesoras ya fueron elegidas; por eso el heap siempre
ofrece una elección factible y el algoritmo es óptimo.

### 2.2 Selección exacta y aproximada

La referencia exacta enumera `C(N,k)` subconjuntos:
`T_exact(N,k) = O(C(N,k) * k)` incluyendo la evaluación de la unión.

Greedy inicia con `S = ∅` y agrega el nodo de mayor ganancia marginal en cada
paso. Evalúa a lo sumo `N` candidatos en cada uno de `k` pasos:
`T_greedy(N,k) = O(Nk)` evaluaciones de `f` (más el costo de cada evaluación).

Para una función monótona submodular no negativa con restricción de cardinalidad,
el teorema de Nemhauser, Wolsey y Fisher (1978) demuestra:

`f(S_greedy) >= (1 - 1/e) f(S*) ≈ 0.632 f(S*)`.

El experimento compara el resultado greedy con el óptimo exacto y registra la
razón observada. No debe confundirse la cota con una igualdad: los datos
pueden superar el 63.2%.

## 3. NP-dureza

La instancia de Maximum Coverage es `(U, C_1,...,C_N,k)`. Se transforma en
una instancia de selección usando un nodo por cada conjunto `C_i` y la
utilidad `f(S)=|∪_{i∈S} C_i|`. La transformación es polinomial, conserva `k`,
y cualquier solución seleccionada cubre exactamente la misma cantidad de
elementos. Por tanto, resolver óptimamente selección submodular resolvería
Maximum Coverage. Como Maximum Coverage es NP-difícil, la selección general
también lo es.

## 4. Variantes

- **Costos:** `greedy_budgeted_select` usa ganancia marginal por costo y compara
  además el mejor nodo individual factible. La garantía de `1-1/e` debe
  citarse para la variante de *budgeted maximum coverage*; no se debe afirmar
  automáticamente la cota de cardinalidad sin esta adaptación.
- **Fallos:** `select_over_rounds` reconstruye el conjunto activo después de
  cada ronda y usa una semilla para reproducir los fallos.
- **Vecindarios:** `neighborhood_utility` agrega el efecto de los vecinos. Si
  el modelo de influencia no mantiene submodularidad, solo debe presentarse
  como heurística y medirse, no como una aplicación automática del teorema.

## 5. Validación experimental

Ejecutar:

```powershell
python -m red_project.cli experiment --output results
```

Se usan cinco tamaños crecientes y semilla fija. `times.csv` contiene tiempos,
utilidades y razón greedy/óptimo; `times.png` contrasta las curvas. Para el
informe final se deben repetir varias veces cada tamaño, reportar promedio y
desviación, y explicar que la fuerza bruta solo puede crecer hasta tamaños que
permitan terminar en el equipo disponible.

## 6. Referencia

G. L. Nemhauser, L. A. Wolsey y M. L. Fisher, “An analysis of approximations
for maximizing submodular set functions—I”, *Mathematical Programming*,
14, 1978, 265–294.
