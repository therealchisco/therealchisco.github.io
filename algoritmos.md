# I Parte - Optimización de Algoritmos

## Medidas de Eficiencia

### Objetivo:

* Describir de manera exacta pero simplificada el desempeño de un Algoritmo.
La especificación exacta del tiempo de ejecución de un algoritmo esta defininda por una operación de
estructuras discretas
* Conjunto I de las Instancias
* Tiempo de Ejecución del Algoritmo:  <img src="https://latex.codecogs.com/gif.latex?T:&space;I&space;\to&space;\mathbb{N}" title="T: I \to \mathbb{N}" />

### Problema:
<img src="https://latex.codecogs.com/gif.latex?T" title="T" /> es muy difícil de determinar y describir

### Solución:
**Agrupación de las instancias (por tamaño)**
Dado el conjunto de Instancias <img src="https://latex.codecogs.com/gif.latex?I_{n}" title="I_{n}" /> de tamaño **n** de un problema, podemos medir la eficiencia y determinar:

### Worst case:
Nos garantiza la eficiencia del algoritmo, pero posiblemente con una aproximación demasiado pesimista

<img src="https://latex.codecogs.com/gif.latex?t(n)&space;=\max\left&space;\{{T(i):i\in&space;I_{n}}&space;\right&space;\}" title="t(n) =\max\left \{{T(i):i\in I_{n}} \right \}" />

### Average case:

Nos da el tiempo de ejecución promedio, pero este no corresponde necesariamente al tiempo real en la práctica

<img src="https://latex.codecogs.com/gif.latex?t(n)&space;=&space;{1&space;\over&space;\left|&space;I_{n}\right&space;|}\sum_{i\in&space;I_{n}}T\left(i&space;\right&space;)" title="t(n) = {1 \over \left| I_{n}\right |}\sum_{i\in I_{n}}T\left(i \right )" />

### Best case:

Comparable al worst case, nos da una aproximación posiblemente demasiado optimista

<img src="https://latex.codecogs.com/gif.latex?t(n)&space;=\min\left&space;\{{T(i):i\in&space;I_{n}}&space;\right&space;\}" title="t(n) =\min\left \{{T(i):i\in I_{n}} \right \}" />

*Nos aseguramos que I sea finito y que el minimo y máximo elemento existan*

### Las ecuaciones exactas para t(n) son demasiado complejas sino imposibles para esto utilizamos:

## Crecimiento asintótico

f(n) y g(n) tienen el mismo índice de crecimiento, si la proporción esta delimitada por constantes c y d

<img src="https://latex.codecogs.com/gif.latex?\exists&space;c,d&space;\in&space;\mathbb{R_{&plus;}}&space;\&space;\&space;\exists&space;n_{0}&space;\in&space;\mathbb{N}\&space;\&space;\forall&space;n&space;\geq&space;n_{0}:&space;c&space;\leq&space;{f(n)&space;\over&space;g(n)}&space;\leq&space;d" title="\exists c,d \in \mathbb{R_{+}} \ \ \exists n_{0} \in \mathbb{N}\ \ \forall n \geq n_{0}: c \leq {f(n) \over g(n)} \leq d" />

f(n) **crece más rápido** que g(n) cuando:

<img src="https://latex.codecogs.com/gif.latex?\forall&space;c&space;\in&space;\mathbb{N_{&plus;}}&space;\&space;\&space;\exists&space;n_{0}&space;\in&space;\mathbb{N}&space;\&space;\&space;\forall&space;n&space;\geq&space;n_{0}:&space;f(n)&space;\geq&space;c&space;\cdot&space;g(n)" title="\forall c \in \mathbb{N_{+}} \ \ \exists n_{0} \in \mathbb{N} \ \ \forall n \geq n_{0}: f(n) \geq c \cdot g(n)" />

**O en otras palabras**
<img src="https://latex.codecogs.com/gif.latex?\lim_{x\to\infty}&space;{g(n)&space;\over&space;f(n)}&space;=&space;0" title="\lim_{x\to\infty} {g(n) \over f(n)} = 0" />

Para más información por favor ver el articulo completo en pdf
## [Descargar PDF](articulo.pdf)
