# Guía Básica de Markdown

Markdown es un lenguaje de marcado ligero que permite formatear texto de manera sencilla.

---

## 1. Encabezados (Títulos)

Se usan `#` seguido de un espacio. Más `#` = más pequeño.

```markdown
# Título Principal (H1)
## Subtítulo (H2)
### Sub-subtítulo (H3)
```

**Resultado:**

# Título Principal
## Subtítulo
### Sub-subtítulo

---

## 2. Párrafos y Saltos de Línea

Escribir texto normal crea párrafos. Dejar una línea vacía entre textos crea un nuevo párrafo.

```markdown
Este es el primer párrafo.

Este es el segundo párrafo.
```

---

## 3. Formato de Texto

| Estilo | Sintaxis | Resultado |
|--------|----------|-----------|
| Negrita | `**texto**` | **texto** |
| Cursiva | `*texto*` | *texto* |
| Tachado | `~~texto~~` | ~~texto~~ |
| Código | `` `código` `` | `código` |

```markdown
**Negrita**
*Cursiva*
***Negrita y cursiva***
~~Tachado~~
`código en línea`
```

---

## 4. Listas

### Lista sin orden (viñetas):
```markdown
- Item 1
- Item 2
  - Sub-item (con tab)
- Item 3
```

**Resultado:**
- Item 1
- Item 2
  - Sub-item
- Item 3

### Lista ordenada (numerada):
```markdown
1. Primero
2. Segundo
3. Tercero
```

**Resultado:**
1. Primero
2. Segundo
3. Tercero

---

## 5. Enlaces

```markdown
[Texto del enlace](https://www.ejemplo.com)
```

**Resultado:** [Texto del enlace](https://www.ejemplo.com)

---

## 6. Imágenes

```markdown
![Texto alternativo](ruta/a/la/imagen.jpg)
```

---

## 7. Bloques de Código

Para código de una sola línea: `` `código` ``

Para bloques de código (múltiples líneas), usá tres comillas invertidas:

<pre>
```python
def hola():
    print("Hola mundo")
```
</pre>

**Resultado:**
```python
def hola():
    print("Hola mundo")
```

---

## 8. Citas (Blockquotes)

```markdown
> Esta es una cita.
> Puede ocupar varias líneas.
```

**Resultado:**
> Esta es una cita.
> Puede ocupar varias líneas.

---

## 9. Líneas Horizontales (Separadores)

```markdown
---
```

**Resultado:**

---

## 10. Tablas

```markdown
| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Dato A    | Dato B    | Dato C    |
```

**Resultado:**

| Columna 1 | Columna 2 | Columna 3 |
|-----------|-----------|-----------|
| Dato 1    | Dato 2    | Dato 3    |
| Dato A    | Dato B    | Dato C    |

---

## Resumen Rápido

| Elemento | Sintaxis |
|----------|----------|
| Título H1 | `# Título` |
| Negrita | `**texto**` |
| Cursiva | `*texto*` |
| Lista | `- item` |
| Enlace | `[texto](url)` |
| Imagen | `![alt](url)` |
| Código | `` `código` `` |
| Bloque código | ` ```lenguaje\ncódigo\n``` ` |
| Cita | `> texto` |
| Tabla | `\| col \| col \|` |
