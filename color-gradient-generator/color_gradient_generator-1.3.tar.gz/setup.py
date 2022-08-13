import setuptools

setuptools.setup(
    name                            = "color_gradient_generator",
    version                         = "1.3",
    author                          = "Mr. PRAINGLE",
    description                     = "This package will generate a color gradient. The colors, the number of colors generated, the color format, the hexadecimal prefix are configurable.",
    packages                        = ["color_gradient_generator"],
    long_description                = """# Color Gradient Generator

This tool will allow you to generate a color gradient from RGB, decimal or hexadecimal. The source code is available on [GitHub](https://www.github.com/MrPRAINGLE/color-gradient).

---

## Table of content

- [Color Gradient Generator](#color-gradient-generator)
  - [Table of content](#table-of-content)
  - [Colors](#colors)
  - [Color formats](#color-formats)
  - [Errors](#errors)
    - [IncorrectProvidedColor](#incorrectprovidedcolor)
  - [Gradient generator](#gradient-generator)

---

## Colors

Every color of the gradient has a value, and that is all you see, but in fact, there is a class named `Color`, which have a "value" argument.

With this class, you can access the color format. The purpose of this class is also to convert its original value to all of the available formats, in case you want your gradient in a specific format.

---

## Color formats

There are 3 color formats, accessible by the `ColorFormat` Enum class:

- DEC for decimal
- HEX for hexadecimal
- RGB for RGB

---

## Errors

A lot of time, while you use this generator, error will raise. A lot of them would just be `TypeError` of `AttributeError`, but custom errors is a thing. At the moment, only one was created.

### IncorrectProvidedColor

This error raises when the color argument of the `Color` class is incorrect.

---

## Gradient generator

The color generation is accessible by the `generate_gradient` function. There are 3 kwargs : the two colors and the amont of variations to add in the gradient. Then there are 2 optionnal args : _format, which is the format in which the gradient will generate, and hex_prefix, useful only if you generate an hexadecimal gradient.

If the amont of variations provided is too high in relation to the difference between the two colors, an error will raise. You can have up to 500 variations.

If you do not provide a "_format" argument, it is necessary that both colors have the same format.

If you do not provide a "hex_prefix" argument, there will simply be no prefix.

---

Well then, that's about it, have fun !""",
    long_description_content_type   = "text/markdown"
)