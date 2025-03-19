import html
import json
import re
import sys

import svg

elements = []
key_dimension = 100

if len(sys.argv) > 2:
    layout = sys.argv[-3]
    script = sys.argv[-2]
    output = sys.argv[-1]
else:
    print("No arguments given, provide layout, script and output name.")
    exit()

with open(f"layouts/{layout}.json", "r", encoding="utf-8") as file:
    layout_data = json.load(file)

    try:
        with open(script, "r", encoding="utf-8") as script:
            data = script.readlines()
            matches = []
            for line in data:
                search = re.search(r"^\s*?[^\s*?;](.*?)::", line, re.DOTALL)
                if search is not None:
                    matches.append(search.group())
            sanitized_matches = []
            for match in matches:
                sanitized_matches.append(
                    match.lower()
                    .strip()
                    .replace("\t", "")
                    .replace("~", "")
                    .replace("$", "")
                    .replace("<", "")
                    .replace(">", "")
                    .replace("#", "")
                    .replace("^", "")
                    .replace("!", "")
                    .replace("+", "")
                    .replace("::", "")
                )
        # make subset layouts keys with modifiers
    except FileNotFoundError:
        print("Script file not found!")


def return_with_modifiers_preset(bg_fill="white"):
    global x_0, y_0, column, key_dimension, modified_height, modified_width
    return [
        svg.Rect(
            x=x_0,
            y=y_0,
            width=key_dimension * modified_width,
            height=key_dimension * modified_height,
            stroke="black",
            fill=bg_fill,
            stroke_width=2,
        ),
        svg.Text(
            x=x_0 + (key_dimension / 2) * modified_width,
            y=y_0 + key_dimension / 2,
            text=html.escape(column).replace("&lt;br&gt;", ""),
            fill="black",
            font_size=16,
            font_weight="bold",
            font_family="Calibri",
            text_anchor="middle",
        ),
    ]


def return_normal_preset(bg_fill="white"):
    global x_0, y_0, column, key_dimension, modified_height, modified_width
    return [
        svg.Rect(
            x=x_0,
            y=y_0,
            width=key_dimension,
            height=key_dimension,
            stroke="black",
            fill=bg_fill,
            stroke_width=2,
        ),
        svg.Text(
            x=x_0 + key_dimension / 2,
            y=y_0 + key_dimension / 2,
            text=html.escape(column).replace("&lt;br&gt;", ""),
            fill="black",
            font_size=16,
            font_weight="bold",
            font_family="Calibri",
            text_anchor="middle",
        ),
    ]


modified_width = 1
modified_height = 1
y_0 = 0
for rows in layout_data:
    x_0 = 0
    for column in rows:
        # each key is iterated, modifiers (width, height modifications skips to the next iteration)
        if type(column) == dict:
            if "x" in column:  # spacing
                x_0 += key_dimension * float(column["x"])
            # "big ass enter", without the width modification (for now)
            if "h" and "h2" in column:
                modified_height = float(column["h"]) + float(column["h2"])
            if "w" in column:  # width
                modified_width = float(column["w"])
                continue
            if "h" in column:  # height
                modified_height = float(column["h"])
                continue

        else:
            if column.lower() in sanitized_matches:
                redness = 255 - (sanitized_matches.count(column.lower()) - 1) * 32
                redness = hex(64) if redness <= 63 else hex(redness)
                if modified_width != 1 or modified_height != 1:
                    elements.append(
                        return_with_modifiers_preset(
                            bg_fill=f"#{redness.replace("0x", "")}0000"
                        )
                    )
                    x_0 += key_dimension * modified_width
                    modified_width = 1
                    modified_height = 1
                else:
                    elements.append(
                        return_normal_preset(
                            bg_fill=f"#{redness.replace("0x", "")}0000"
                        )
                    )
                    x_0 += key_dimension
            else:
                if modified_width != 1 or modified_height != 1:
                    elements.append(return_with_modifiers_preset())
                    x_0 += key_dimension * modified_width
                    modified_width = 1
                    modified_height = 1
                else:
                    elements.append(return_normal_preset())
                    x_0 += key_dimension
    y_0 += key_dimension

# x_0 += key_dimension  # because last column isn't a starting point

canvas = svg.SVG(
    width=x_0,
    height=y_0,
    elements=[
        svg.Rect(width=x_0, height=y_0, stroke="lightgray", fill="lightgray"),
        *elements,
    ],
)


with open(output, "w", encoding="utf-8") as svg:
    svg.write(str(canvas))
