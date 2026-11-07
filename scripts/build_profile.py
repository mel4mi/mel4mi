import argparse
import copy
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path


SVG_NS = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG_NS)


def svg_tag(name):
    return f"{{{SVG_NS}}}{name}"


def add_text(parent, x, y, value, size=14, color="#c9d1d9", weight="400"):
    node = ET.SubElement(parent, svg_tag("text"), {
        "x": str(x),
        "y": str(y),
        "fill": color,
        "font-family": "Consolas, 'Courier New', monospace",
        "font-size": str(size),
        "font-weight": weight,
    })
    node.text = value
    return node


def add_line(parent, x1, y1, x2, y2, color="#26313d", width=1):
    ET.SubElement(parent, svg_tag("path"), {
        "d": f"M{x1} {y1}H{x2}" if y1 == y2 else f"M{x1} {y1}L{x2} {y2}",
        "fill": "none",
        "stroke": color,
        "stroke-width": str(width),
    })


def add_section(parent, number, title, y):
    add_text(parent, 54, y, number, 13, "#00e5a0", "700")
    add_text(parent, 91, y, title.upper(), 13, "#f0f6fc", "700")
    add_line(parent, 54, y + 15, 946, y + 15)


def add_chip(parent, x, y, label):
    width = max(64, 22 + len(label) * 9)
    ET.SubElement(parent, svg_tag("rect"), {
        "x": str(x),
        "y": str(y - 20),
        "width": str(width),
        "height": "30",
        "rx": "4",
        "fill": "#111923",
        "stroke": "#26313d",
    })
    add_text(parent, x + 11, y, label, 13, "#c9d1d9")
    return width


def add_project(parent, x, title, description, url):
    node = ET.SubElement(parent, svg_tag("a"), {"href": url})
    add_text(node, x, 440, title, 15, "#58a6ff", "700")
    add_text(node, x, 466, description, 11, "#9daab8")


def add_embedded_svg(parent, path, x, y, width, height, fallback_title, fallback_status):
    if path and Path(path).is_file():
        source = ET.parse(path).getroot()
        view_box = source.get("viewBox")
        if not view_box:
            source_width = source.get("width", "495").replace("px", "")
            source_height = source.get("height", "180").replace("px", "")
            view_box = f"0 0 {source_width} {source_height}"
        embedded = ET.SubElement(parent, svg_tag("svg"), {
            "x": str(x),
            "y": str(y),
            "width": str(width),
            "height": str(height),
            "viewBox": view_box,
            "preserveAspectRatio": "xMidYMid meet",
        })
        for child in source:
            embedded.append(copy.deepcopy(child))
        return

    add_text(parent, x + 12, y + 42, fallback_title, 15, "#f0f6fc", "700")
    add_text(parent, x + 12, y + 70, fallback_status, 11, "#9daab8")
    add_text(parent, x + 12, y + 94, "Replaced with live data by GitHub Actions.", 11, "#9daab8")


def read_posts(feed_url, limit):
    request = urllib.request.Request(feed_url, headers={"User-Agent": "mel4mi-profile-readme"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            feed = ET.fromstring(response.read())
    except (ET.ParseError, urllib.error.URLError, TimeoutError):
        return []

    posts = []
    for item in feed.findall("./channel/item")[:limit]:
        title = item.findtext("title", default="").strip()
        url = item.findtext("link", default="").strip()
        if title and url:
            posts.append((title, url))
    return posts


def add_posts(parent, posts):
    if not posts:
        add_text(parent, 64, 823, "Medium feed is temporarily unavailable.", 12, "#9daab8")
        return

    for index, (title, url) in enumerate(posts):
        y = 822 + index * 34
        link = ET.SubElement(parent, svg_tag("a"), {"href": url})
        add_text(link, 64, y, f"0{index + 1}  /", 12, "#00e5a0", "700")
        add_text(link, 112, y, title[:88], 12, "#c9d1d9")


def compose(args):
    root = ET.Element(svg_tag("svg"), {
        "width": "1000",
        "height": "1180",
        "viewBox": "0 0 1000 1180",
        "role": "img",
        "aria-labelledby": "title description",
    })
    ET.SubElement(root, svg_tag("title"), {"id": "title"}).text = "mel4mi GitHub profile"
    ET.SubElement(root, svg_tag("desc"), {"id": "description"}).text = (
        "A unified terminal-inspired profile with skills, projects, live GitHub statistics, "
        "recent Medium posts, and contribution animation."
    )

    defs = ET.SubElement(root, svg_tag("defs"))
    pattern = ET.SubElement(defs, svg_tag("pattern"), {
        "id": "grid",
        "width": "28",
        "height": "28",
        "patternUnits": "userSpaceOnUse",
    })
    ET.SubElement(pattern, svg_tag("path"), {
        "d": "M28 0H0V28",
        "fill": "none",
        "stroke": "#131b24",
        "stroke-width": "1",
    })

    ET.SubElement(root, svg_tag("rect"), {"width": "1000", "height": "1180", "fill": "#0d1117"})
    ET.SubElement(root, svg_tag("rect"), {"width": "1000", "height": "1180", "fill": "url(#grid)"})
    ET.SubElement(root, svg_tag("rect"), {
        "x": "1",
        "y": "1",
        "width": "998",
        "height": "1178",
        "rx": "8",
        "fill": "none",
        "stroke": "#26313d",
        "stroke-width": "2",
    })

    ET.SubElement(root, svg_tag("circle"), {"cx": "25", "cy": "24", "r": "5", "fill": "#ff5f56"})
    ET.SubElement(root, svg_tag("circle"), {"cx": "45", "cy": "24", "r": "5", "fill": "#ffbd2e"})
    ET.SubElement(root, svg_tag("circle"), {"cx": "65", "cy": "24", "r": "5", "fill": "#27c93f"})
    add_text(root, 88, 29, "mel4mi@valhalla: ~", 13, "#738091")
    add_line(root, 1, 48, 999, 48)

    add_text(root, 58, 95, "$ whoami", 15, "#00e5a0", "700")
    add_text(root, 54, 158, "MEL4MI", 52, "#f0f6fc", "700")
    add_text(root, 58, 190, "HACKER FROM VALHALLA  /  JUNIOR PENETRATION TESTER", 14, "#9daab8")
    add_text(root, 58, 220, "Curious about systems, security, and the code that connects them.", 13, "#c9d1d9")
    add_text(root, 850, 203, "[ ONLINE ]", 12, "#00e5a0", "700")
    add_line(root, 58, 239, 942, 239, "#00e5a0", 2)

    add_section(root, "01", "Toolkit", 276)
    chip_x = 58
    for label in ("C", "Python", "HTML", "CSS", "Bootstrap", "Django", "Flask", "MySQL", "Linux"):
        chip_x += add_chip(root, chip_x, 318, label) + 10

    add_section(root, "02", "Selected work", 378)
    add_project(root, 60, "HackGurat", "Cybersecurity learning resources", "https://github.com/mel4mi/HackGurat")
    add_project(root, 370, "Huntress CTF", "2025 competition writeups", "https://github.com/mel4mi/2025HuntressCTF_Writeups")
    add_project(root, 680, "ascii-trailer", "ASCII art for the terminal", "https://github.com/mel4mi/ascii-trailer")
    add_line(root, 350, 421, 350, 478)
    add_line(root, 660, 421, 660, 478)

    add_section(root, "03", "GitHub activity", 522)
    add_embedded_svg(root, args.stats, 54, 545, 432, 150, "PROFILE STATS", "PREVIEW / WAITING FOR FIRST ACTION RUN")
    add_embedded_svg(root, args.languages, 514, 545, 432, 150, "TOP LANGUAGES", "PREVIEW / WAITING FOR FIRST ACTION RUN")

    add_section(root, "04", "Recent writing", 741)
    add_posts(root, read_posts(args.feed, 3))

    add_section(root, "05", "Contribution trail", 930)
    add_embedded_svg(root, args.snake, 58, 960, 884, 170, "CONTRIBUTION ANIMATION", "Generated by GitHub Actions")
    add_text(root, 58, 1155, "$ echo 'keep building'", 12, "#00e5a0")

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    ET.indent(root, space="  ")
    output.write_bytes(ET.tostring(root, encoding="utf-8", xml_declaration=True))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stats")
    parser.add_argument("--languages")
    parser.add_argument("--snake")
    parser.add_argument("--feed", default="https://medium.com/feed/@mel4mi")
    parser.add_argument("--output", default="profile/profile.svg")
    compose(parser.parse_args())


if __name__ == "__main__":
    main()