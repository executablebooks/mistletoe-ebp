---
front: matter
---
# Markdown Cheatsheet

    Markup :  # Heading 1

    -OR-

    Markup :  ============= (below H1 text)

    Markup :  ## Heading 2

    -OR-

    Markup: --------------- (below H2 text)

## Heading 2

    Markup :  ### Heading 3

### Heading 3

    Markup :  #### Heading 4

#### Heading 4

    Markup :  Common text

Common text

    Markup :  _Emphasized text_ or *Emphasized text*

_Emphasized text_

    Markup :  ~~Strikethrough text~~

~~Strikethrough text~~

    Markup :  __Strong text__ or **Strong text**

__Strong text__

    Markup :  ___Strong emphasized text___ or ***Strong emphasized text***

___Strong emphasized text___ or ***Strong emphasized text***

    Horizontal line

    Markup :  - - - -

- - - -

    Markup :  inline `code()`

inline `code()`

    Fenced code block:

    Markup : ```python
             fenced = "code block"
             ```

```python
fenced = "code block"
```

~~~
 Markup : * Bullet list
              * Nested bullet
                  * Sub-nested bullet etc
          * Bullet list item 2

-OR-

 Markup : - Bullet list
              - Nested bullet
                  - Sub-nested bullet etc
          - Bullet list item 2
~~~

* Bullet list
    * Nested bullet
        * Sub-nested bullet etc
* Bullet list item 2

~~~
 Markup : 1. A numbered list
              1. A nested numbered list
              2. Which is numbered
          1. Which is numbered
~~~

1. A numbered list
    1. A nested numbered list
    2. Which is numbered
2. Which is numbered

    Markup :  > Blockquote
              >> Nested Blockquote

> Blockquote
>> Nested blockquote

    Markup :  [Named Link](http://www.google.fr/ "Named link title") or <http://example.com/>

[Named Link](http://www.google.fr/ "Named link title")
or <http://example.com/>

    Markup: [heading-1](#heading-1 "Goto heading-1")

[heading-1](#heading-1 "Goto heading-1")

    Image with alt:

    Markup : ![picture alt](http://via.placeholder.com/200x150 "Title is optional")

![picture alt](http://via.placeholder.com/200x150 "Title is optional")

    definition list:

    Markup: [text with *__nested__* syntax][link]

    [link]: https://google.com

[text with *__nested__* syntax][link]

[link]: https://google.com

HTML Block:

    Markup : <details>
               <summary>Title 1</summary>
               <p>Content 1 Content 1 Content 1 Content 1 Content 1</p>
             </details>

<details>
  <summary>Title 1</summary>
  <p>Content 1 Content 1 Content 1 Content 1 Content 1</p>
</details>
<details>
  <summary>Title 2</summary>
  <p>Content 2 Content 2 Content 2 Content 2 Content 2</p>
</details>

## Extensions

Table, like this one :

First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell

```
First Header  | Second Header
------------- | -------------
Content Cell  | Content Cell
Content Cell  | Content Cell
```

    Footnote:

    Markup: [^1]

    [^1]: this is a footnote

[^1]

[^1]: this is a footnote

```
Markup : - [ ] An uncompleted task
        - [x] A completed task
```

- [ ] An uncompleted task
- [x] A completed task

```
Markup : - [ ] An uncompleted task
            - [ ] A subtask
```

- [ ] An uncompleted task
    - [ ] A subtask

```
Emoji:

Markup : Code appears between colons :EMOJICODE:
```

:exclamation: Use emoji icons to enhance text. :+1:  Look up emoji codes at [emoji-cheat-sheet.com](http://emoji-cheat-sheet.com/)
