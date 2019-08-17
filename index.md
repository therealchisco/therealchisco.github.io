
<iframe src="https://drive.google.com/file/d/1GFIEJ3l44nP9QJTn2KG4RopPS7YmAA0f/preview" width="640" height="480"></iframe>


# Aplicaciones del Cálculo en la Ingenieria de Software: Optimización de Algoritmos y Métodos Criptográficos


### Tabla de Contenido
1. [Abstracción](#abs)
2. [Introduccion](#intro)
3. [Justificación del Tema](#just)
4. [**Parte I**:Optimización de Algoritmos](algos.md)
  * [Video: Algoritmos](https://drive.google.com/file/d/1aKWFb39mYadUy1dHeEDyjhmmtiCBrhZ-/view?usp=sharing)
5. [**Parte II**:Optimización de Algoritmos](cripto.md)
  * [Video: Criptografia RSA](https://drive.google.com/file/d/1aKWFb39mYadUy1dHeEDyjhmmtiCBrhZ-/view?usp=sharing)
6. [Descarga Archivo PDF](trabajo.pdf)

### Miembros de Equipo
1. [Francisco J. Diaz](github.com/therealchisco)
2. [Introduccion](#intro)
3. [Justificación del Tema](#just)
4. [**Parte I**:Optimización de Algoritmos](algos.md)
  * [Video: Algoritmos](https://drive.google.com/file/d/1aKWFb39mYadUy1dHeEDyjhmmtiCBrhZ-/view?usp=sharing)
5. [**Parte II**:Optimización de Algoritmos](cripto.md)
  * [Video: Criptografia RSA](https://drive.google.com/file/d/1aKWFb39mYadUy1dHeEDyjhmmtiCBrhZ-/view?usp=sharing)
6. [Descarga Archivo PDF](trabajo.pdf)




## Abstracción <a name="abs"></a>

Aqui encontrará una explicación de la importancia que los conocimientos matemáticos juegan en la ingeniería de so-
ware. Utilizamos ejemplos simplificados para hacer los conceptos accesibles a gente no familiarizada
con el campo.

## Introducción <a name="intro"></a>

El poder de los computadores ha crecido de forma exponencial en las ultimas décadas, (un celular
de hoy, es significativamente más avanzado que el ordenador a bordo del Apollo 11) sin embargo no
siempre se explota su máximo potencial.

Una de las características más fundamentales de las computadoras es que estas solo pueden ser tan
eficientes como el software que corren, por ende el software ineficiente, será ineficiente sin importar
que tan sofisticado o moderno sea el Hardware donde corre.


Como ingenieros es aquí donde los conocimientos adquiridos en el curso de “Cálculo I” (BMAT-01)
resultan altamente útiles para poder por ejemplo:

* Analizar los limites de dos piezas de software para determinar cual será más rápido

* Utilizar derivación para poder saber cual será el tiempo de ejecución de un algoritmo en el peor y mejor de los casos.

Además hay procesos informáticos de los cuales dependemos diariamente y (damos por sentado)
como la “encripción RSA” que mantiene nuestros datos personales, y contraseñas protegidas y en
secreto. Este proceso no sería posible de implementar de no tener un fundamento fuerte matemático
por ejemplo:

* La definición del teorema de números primos se puede probar buscando un limite
* Para probar la seguridad de este algoritmo es necesario solucionar varias integrales

## Justificación del Tema <a name="just"></a>

Existe mucha gente incluso dentro de las otras áreas de ingeniera que no esta familiarizada con lo que
hacen los ingenieros de software, por eso la misión de este trabajo es:

>Poder explicar brevemente y poner en contexto a estos grupos explicando
>* Que significa programar
>* Que es un algoritmo
>* Cuales son los retos a la hora de escribir buen algoritmo?

Existen también ingenieros de software que no tienen muy clara la conexión que existe entre su carrera y
la matemática analítica, por eso además nuestro proyecto pretende

>Poder mostrarle a los ingenieros familiarizados con el software:
> * Como pueden empezar a usar el cálculo para mejorar el soware que escriben
> * Motivar a los estudiantes a considerar utilizar un enfoque matemático a la hora de investigar temas de software y no únicamente la parte más técnica de lenguajes de programación


# I Parte - Optimización de Algoritmos

A continuación encontrara un video con información sobre el tema, tambien podra encontrar toda la infromación en forma de texto

## Video 

## Medidas de Eficiencia

### Objetivo:
* Describir de manera exacta pero simplificada el desempeño de un Algoritmo.
La especificación exacta del tiempo de ejecución de un algoritmo esta defininda por una operación de
estructuras discretas
* Conjunto I de las Instancias
* Tiempo de Ejecución del Algoritmo: T : I ! N
Problema:

T es muy difícil de determinar y describir

### Solución

Agrupación de las instancias (por tamaño)
Dado el conjunto de Instancias In de tamaño n de un problema, podemos medir la eficiencia y determinar:

### Worst case:
* Nos garantiza la eficiencia del algoritmo, pero posiblemente con una aproximación demasiado pesimista
t(n) = max {T(i) : i 2 In}

### Average case:
* Nos da el tiempo de ejecución promedio, pero este no corresponde necesariamente al tiempo real en
la práctica

### Best case:
* Comparable al worst case, nos da una aproximación posiblemente demasiado optimista
t(n) = min {T(i) : i 2 In}
* Nos aseguramos que I sea finito y que el minimo y máximo elemento existan

**Las ecuaciones exactas para t(n) son demasiado complejas sino imposibles para esto
utilizamos:**

## Crecimiento asintótico
f(n) y g(n) tienen el mismo índice de crecimiento, si la proporción esta delimitada por constantes c
y d
9c, d 2 R+ 9n0 2 N 8n  n0 : c 
f(n)
g(n)  d
f(n) crece más rápido que g(n) cuando exista un n0 para todos las constantes positivas c , a partir de
f(n)  c · g(n) para n  n0
8c 2 R+ 9n0 2 N 8n  n0 : f(n)  c · g(n)


O en otras palabras
lim
x!1
g(n)
f(n) = 0
Conjuntos para la formalización de la notación asintótico
O(f(n)) : {g(n) : 9c > 0 : 9n0 > 0 : 8n  n0 : g(n)  c · f(n))}

(f(n)) : {g(n) : 9c > 0 : 9n0 > 0 : 8n  n0 : g(n)  c · f(n))}
(f(n)) = O(f(n)) \ 
(f(n))
o(f(n)) : {g(n) : 8c > 0 : 9n0 > 0 : 8n  n0 : g(n)  c · f(n))}
!(f(n)) : {g(n) : 8c > 0 : 9n0 > 0 : 8n  n0 : g(n)  c · f(n))}


### Markdown

Markdown is a lightweight and easy-to-use syntax for styling your writing. It includes conventions for

```markdown
Syntax highlighted code block

# Header 1
## Header 2
### Header 3

- Bulleted
- List

1. Numbered
2. List

**Bold** and _Italic_ and `Code` text

[Link](url) and ![Image](src)
```

For more details see [GitHub Flavored Markdown](https://guides.github.com/features/mastering-markdown/).

### Jekyll Themes

Your Pages site will use the layout and styles from the Jekyll theme you have selected in your [repository settings](https://github.com/therealchisco/therealchisco.github.io/settings). The name of this theme is saved in the Jekyll `_config.yml` configuration file.

### Support or Contact

Having trouble with Pages? Check out our [documentation](https://help.github.com/categories/github-pages-basics/) or [contact support](https://github.com/contact) and we’ll help you sort it out.
