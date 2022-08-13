from color_gradient_generator.typing import Color, ColorFormat

def generate_gradient(_start_color: int | str | tuple[int], _end_color: int | str | tuple[int], variations: int, *, _format: ColorFormat | str = None, hex_prefix: str = None): 
    """
    Generates a gradient of color.

    ## Attributes

    `start_color` : Indicates the color from which the gradient will begin.

    `end_color` : Indicates the color from which the gradient will end.

    `variations` : Indicates how many color shall be added into the gradient (from 1 to 500, start and end color not included).

    `_format` : Indicates the color format in which the gradient will be generated.

    `hex_prefix` : Indicates the hexadecimal prefix (either "0x" or "#"). Useful only if you generate a gradient in hexadecimal.
    """
    start_color = Color(_start_color); end_color = Color(_end_color)
    if abs(start_color.__dec__() - end_color.__dec__()) < variations + 1:
        raise TypeError("Please provide two color arguments not too close one to each other regarding of how many colors you want to generate.")
    if start_color._format != end_color._format and not _format:
        raise TypeError('Please provide either two colors of the same format or a "_format" argument.')
    if not variations:
        raise TypeError('Please provide a value for the "variations" argument.')
    if variations not in range(1, 501):
        raise TypeError('Please provide a "variations" argument within a range of 1 to 100.')
    if _format:
        if f"{_format}" == "<enum 'ColorFormat'>":
            raise AttributeError('Please provide an attribute (DEC, HEX or RGB) for the "_format" argument.')
        try:
            _format = ColorFormat[_format.upper()]
        except:
            if isinstance(_format, str):
                raise TypeError('Inappropriate string provided for argument "_format", please provide a string "DEC", "HEX" or "RGB" or an argument of type ColorFormat.')
            if not isinstance(_format, ColorFormat):
                raise TypeError('Inappropriate value provided for argument "_format", please provide an argument of type ColorFormat or a string "DEC", "HEX" or "RGB".')
    if hex_prefix not in ("#", "0x"):
        raise TypeError('Please provide a "hex_prefix" argument of either "#" or "0x#.')
    __start_color = getattr(start_color, f"__{start_color._format.name.lower() if start_color._format == end_color._format else _format.name.lower()}__")
    __start_color = __start_color() if __start_color.__name__ != "__hex__" else __start_color(hex_prefix)
    end_result = [__start_color]
    if _format == ColorFormat.DEC or start_color._format and end_color._format == ColorFormat.DEC:
        for n in range(variations):
            end_result.append(
                round((end_color.__dec__() - start_color.__dec__()) / (variations + 1) * (n + 1)) + start_color.__dec__()
            )
    elif _format == ColorFormat.HEX or start_color._format and end_color._format == ColorFormat.HEX:
        for i in range(variations):
            end_result.append(
                f"#{round((end_color.__dec__() - start_color.__dec__()) / (variations + 1) * (i + 1)) + start_color.__dec__():0>6x}"
            )
    else:
        _end_result = []
        for n in range(variations):
            for i in range(3):
                _end_result.append(
                    round((end_color.__rgb__()[i] - start_color.__rgb__()[i]) / (variations + 1) * (n + 1)) + start_color.__rgb__()[i]
                )
            end_result.append(tuple(_end_result[len(_end_result) - 3:len(_end_result)]))
        end_result.append()
    __end_color = getattr(end_color, f"__{end_color._format.name.lower() if start_color._format == end_color._format else _format.name.lower()}__")
    __end_color = __end_color() if __end_color.__name__ != "__hex__" else __end_color(hex_prefix)
    end_result.append(__end_color)
    return end_result