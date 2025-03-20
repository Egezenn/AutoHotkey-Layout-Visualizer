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

try:
    with open(f"layouts/{layout}.json", "r", encoding="utf-8") as file:
        layout_data = json.load(file)
except FileNotFoundError:
    print("Layout is not found!\nYou don't have to specify the directory.")
    exit()

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
                match.upper()
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
    # if they're indented it probably means they're context sensitive
except FileNotFoundError:
    print("Script file not found!")
    exit()


def svg_element_constructor(
    text,
    text_list,
    current_width,
    current_height,
    key_dimension,
    modified_height,
    modified_width,
    preset=1,
    bg_fill="white",
    font_size=14,
):
    # TODO replace the text to something beatiful with a dict
    if preset == 1:
        if len(text_list) > 1:
            return [
                svg.Rect(
                    x=current_width,
                    y=current_height,
                    width=key_dimension,
                    height=key_dimension,
                    stroke="black",
                    fill=bg_fill,
                    stroke_width=2,
                ),
                svg.Text(
                    x=current_width + key_dimension / 2,
                    y=current_height + key_dimension / 2 - font_size // 2,
                    text=html.escape(text_list[0]).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
                svg.Text(
                    x=current_width + key_dimension / 2,
                    y=current_height + key_dimension / 2 + font_size // 2,
                    text=html.escape(text_list[1]).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
            ]
        else:
            return [
                svg.Rect(
                    x=current_width,
                    y=current_height,
                    width=key_dimension,
                    height=key_dimension,
                    stroke="black",
                    fill=bg_fill,
                    stroke_width=2,
                ),
                svg.Text(
                    x=current_width + key_dimension / 2,
                    y=current_height + key_dimension / 2,
                    text=html.escape(text).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
            ]
    elif preset == 2:
        if len(text_list) > 1:
            return [
                svg.Rect(
                    x=current_width,
                    y=current_height,
                    width=key_dimension * modified_width,
                    height=key_dimension * modified_height,
                    stroke="black",
                    fill=bg_fill,
                    stroke_width=2,
                ),
                svg.Text(
                    x=current_width + (key_dimension / 2) * modified_width,
                    y=current_height + key_dimension / 2 - font_size // 2,
                    text=html.escape(text_list[0]).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
                svg.Text(
                    x=current_width + (key_dimension / 2) * modified_width,
                    y=current_height + key_dimension / 2 + font_size // 2,
                    text=html.escape(text_list[1]).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
            ]
        else:
            return [
                svg.Rect(
                    x=current_width,
                    y=current_height,
                    width=key_dimension * modified_width,
                    height=key_dimension * modified_height,
                    stroke="black",
                    fill=bg_fill,
                    stroke_width=2,
                ),
                svg.Text(
                    x=current_width + (key_dimension / 2) * modified_width,
                    y=current_height + key_dimension / 2,
                    text=html.escape(text).replace("&lt;br&gt;", ""),
                    fill="black",
                    font_size=font_size,
                    font_weight="bold",
                    font_family="Calibri",
                    text_anchor="middle",
                ),
            ]


row_width_list = []
modified_width = 1
modified_height = 1
current_height = 0
current_width = 0
for rows in layout_data:
    if current_width != 0:
        row_width_list.append(current_width)
    current_width = 0
    for column in rows:
        # each key is iterated, modifiers (width, height modifications skips to the next iteration)
        if type(column) == dict:
            if "x" in column:  # spacing
                current_width += key_dimension * float(column["x"])
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
            text = column.upper()
            text_list = text.split(" && ")
            if text in sanitized_matches or any(
                e in text_list for e in sanitized_matches
            ):
                try:
                    redness = 255 - (
                        (
                            sanitized_matches.count(text_list[1])
                            + sanitized_matches.count(text_list[2])
                        )
                        * 32
                    )
                except IndexError:
                    redness = 255 - (sanitized_matches.count(text) * 32)

                redness = hex(64) if redness <= 63 else hex(redness)
                if modified_width != 1 or modified_height != 1:
                    elements.append(
                        svg_element_constructor(
                            text,
                            text_list,
                            current_width,
                            current_height,
                            key_dimension,
                            modified_height,
                            modified_width,
                            preset=2,
                            bg_fill=f"#{redness.replace("0x", "")}0000",
                        )
                    )
                    current_width += key_dimension * modified_width
                    modified_width = 1
                    modified_height = 1
                else:
                    elements.append(
                        svg_element_constructor(
                            text,
                            text_list,
                            current_width,
                            current_height,
                            key_dimension,
                            modified_height,
                            modified_width,
                            bg_fill=f"#{redness.replace("0x", "")}0000",
                        )
                    )
                    current_width += key_dimension
            else:
                if modified_width != 1 or modified_height != 1:
                    elements.append(
                        svg_element_constructor(
                            text,
                            text_list,
                            current_width,
                            current_height,
                            key_dimension,
                            modified_height,
                            modified_width,
                            preset=2,
                        )
                    )
                    current_width += key_dimension * modified_width
                    modified_width = 1
                    modified_height = 1
                else:
                    elements.append(
                        svg_element_constructor(
                            text,
                            text_list,
                            current_width,
                            current_height,
                            key_dimension,
                            modified_height,
                            modified_width,
                        )
                    )
                    current_width += key_dimension
    current_height += key_dimension
row_width_list.append(current_width)

canvas = svg.SVG(
    width=max(row_width_list),
    height=current_height,
    elements=[
        svg.Rect(
            width=max(row_width_list),
            height=current_height,
            stroke="lightgray",
            fill="lightgray",
        ),
        *elements,
    ],
)


with open(output, "w", encoding="utf-8") as file:
    file.write(str(canvas))
