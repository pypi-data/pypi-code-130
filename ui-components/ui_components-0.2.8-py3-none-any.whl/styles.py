tag_styles = {
    ":root": {
        "--off-black": "#212121;",
        "--blue": "#0062FF;",
        "--blue-clicked": "#83EEFF",
        "--yellow": "#F2EA02;",
        "--red": "#FF3300;",
        "--green": "#00FF66;",
        "--pink": "#FF0099;",
        "--purple": "#6E0DD0;",
    },
    "body": {
        "background": "var(--off-black);",
        "background-image": "linear-gradient(to right, var(--off-black), charcoal, var(--off-black));",
        "font-family": "'Poppins', sans-serif;",
    },
    "h1, h2, h3, h4, h5, h6": {"color": "var(--blue);"},
    "hr": {
        "border": "0;",
        "clear": "both;",
        "display": "block;",
        "background-color": "var(--blue);",
        "height": "1px;",
    },
    "label": {
        "color": "var(--blue);",
    },
    "select": {
        "background-color": "WhiteSmoke;",
        "color": "var(--off-black);",
        "font-size": "1.125em;",
    },
    "button, input[type=submit], input[type=reset]": {
        "background-color": "var(--blue);",
        "color": "var(--off-black);",
        "border-radius": "5px;",
        "border": "2px solid var(--light-grey);",
        "transition-duration": "0.2s;",
        "cursor": "pointer;",
        "padding": "0.5em 1.33em;",
        "font-weight": "bold;",
    },
    "button:hover": {
        "background-color": "var(--blue);",
    },
    "button.active": {
        "background-color": "var(--blue);",
    },
    "table, th, td": {
        "border-left": "1px solid var(--blue);",
        "border-right": "1px solid var(--blue);",
        "text-align": "center;",
    },
    "table": {
        "display": "table;",
        "border-collapse": "collapse;",
        "width": "80%;",
        "border-bottom": "2px solid var(--blue);",
    },
    "thead": {
        "background": "var(--blue);",
    },
    "tbody tr:nth-child(odd)": {
        "background": "WhiteSmoke;",
    },
    "tbody tr:nth-child(even)": {
        "background": "white;",
    },
}

tab_styles = {
    ".tab": {
        "overflow": "hidden;",
        "border-radius": "0px;",
        "background-color": "Gainsboro;",
    },
    ".tablinks": {
        "border": "1px solid black;",
        "cursor": "pointer;",
        "padding": "0.25em 0.33em;",
        "transition": "0.3s;",
        "font-size": "1em;",
        "border-radius": "0px;",
        "float": "left;",
        "outline": "none;",
        "overflow": "hidden;",
    },
    ".tabcontent": {
        "display": "none;",
        "border": "1px solid var(--blue);",
        "border-radius": "5px;",
        "padding": "1em 5em;",
    },
}

layout_styles = {
    # horizontally center everything in a central vertical column.
    ".y-axis-centered": {
        "display": "flex;",
        "flex-direction": "column;",
        "justify-content": "center;",
        "align-content": "center;",
        "align-items": "center;",
    },
    # evenly horizontally space all 1st children of each 1st child
    ".space-around-rows>*": {
        "display": "flex;",
        "flex-direction": "row;",
        "justify-content": "space-around;",
        "column-gap": "20px;",
    },
    # evenly horizontally space all 1st children of each 1st child and also add a vertical gap between 1st children.
    ".space-around-spaced-rows>*": {
        "display": "flex;",
        "flex-direction": "row;",
        "justify-content": "space-around;",
        "column-gap": "20px;",
        "margin-top": "20px;",
        "margin-bottom": "20px;",
    },
}


iframe_styles = {
    ".iframe-container": {
        "position": "relative;",
        "overflow": "hidden;",
        "width": "100%;",
        "padding-top": "56.25%;",  # 16:9 Aspect Ratio (divide 9 by 16 = 0.5625)
    },
    # Then style the iframe to fit in the container div with full height and width */
    ".responsive-iframe": {
        "position": "absolute;",
        "top": "0;",
        "left": "0;",
        "bottom": "0;",
        "right": "0;",
        "width": "100%;",
        "height": "100%;",
    },
}

ioinfobox_styles = {
    ".ioinfobox_container": {"border": "1px solid;"},
    ".ioinfobox_input": {
        "background-color": "#b9c2a8",
    },
    ".ioinfobox_meta": {"background-color": "#a4c567"},
    ".ioinfobox_output": {"background-color": "#99ca3c"},
}


# TODO change colors.
multiselect_styles = {
    ".ms-container": {
        "border": "1px solid var(--purple);",
        # "padding": "0.125em;",
        # "max-width": "17%;",
        # "resize": "both;",
        # "overflow": "auto;",
    },
    ".ms-selections": {
        "display": "flex;",
        "flex-flow": "row wrap;",
    },
    ".ms-option": {
        "border-style": "dashed;",
        "border-width": "1px;",
        "border-color": "var(--purple);",
        "background-color": "var(--blue);",
        "color": "var(--off-black);",
        "padding": "0.2em;",
        "cursor": "pointer;",
    },
}

pagaination_styles = {
    ".pagination": {
        "display": "inline-block;",
    },
    ".pagination a": {
        "color": "var(--blue);",
        "float": "left;",
        "padding": "8px 16px;",
        "text-decoration": "none;",
        "transition": "background-color .2s;",
    },
    ".pagination a.active": {
        "background-color": "var(--blue);",
        "color": "white;",
        "border-radius": "2px;",
    },
    ".pagination a:hover:not(.active)": {
        "background-color": "var(--blue);",
        "border-radius": "2px;",
    },
}

tooltip_styles = {
    ".tooltip": {
        "position": "relative;",
        "display": "inline-block;",
        "border-bottom": "1px dotted var(--purple);",
    },
    ".tooltip .tooltiptext": {
        "visibility": "hidden;",
        "width": "120px;",
        "background-color": "var(--green);",
        "color": "black;",
        "text-align": "center;",
        "border-radius": "6px;",
        "padding": "5px 0;",
        # Position the tooltip
        "position": "absolute;",
        "z-index": "1;",
        "bottom": "150%;",
        "left": "50%;",
        "margin-left": "-60px;",
    },
    ".tooltip .tooltiptext::after": {
        "content": '"";',
        "position": "absolute;",
        "top": "100%;",
        "left": "50%;",
        "margin-left": "-5px;",
        "border-width": "5px;",
        "border-style": "solid;",
        "border-color": "pink transparent transparent transparent;",
    },
    ".tooltip:hover .tooltiptext": {
        "visibility": "visible;",
    },
}

top_label_style = {
    ".top-label": {
        "display": "inline-block;",
        "margin": "0 auto;",
        "padding": "0px;",
        # "background-color": "#8ebf42;",
        # "text-align": "center;",
    }
}

centered_top_label_style = {
    ".centered-top-label": {**top_label_style[".top-label"], "text-align": "center;"}
}

buttons_style = {
    ".close-btn": {
        "width": "1%;",
        "height": "1%;",
        "position": "absolute;",
        "right": "-1px;",
        "z-index": "1000;",
        "float": "right;",
        "top": "1px;",
    }
}


all_styles = {
    **tag_styles,
    **tab_styles,
    **layout_styles,
    **iframe_styles,
    **ioinfobox_styles,
    **multiselect_styles,
    **pagaination_styles,
    **tooltip_styles,
    **top_label_style,
    **centered_top_label_style,
}


def flexbox_class(**kwargs):
    properties = {
        "display": "flex",
        "flex-flow": "column wrap",
        "justify-content": "center",
        "align-items": "center",
        "align-content": "center",
        "background-color": "#1ae8bf",
    }
    properties.update(kwargs)


def vega_chat_grid(n_cols: int):
    css = {
        f".vega-grid-{n_cols}": {
            "display": "grid",
            "grid-gap": "1px;",
            "place-items": "center",
            "grid-template-columns": f"repeat({n_cols}, 1fr);",
        },
    }
    all_styles.update(css)
