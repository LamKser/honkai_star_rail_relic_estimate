from yattag import indent

from src.utils.convert import convert_extract_info_2_html


def save_extract_info_2_html(html_content: str, save: str):
    result = indent(
        html_content,
        indentation = '\t',
        newline = '\n',
        indent_text = True
    )

    # Save the HTML content to a file
    with open(save, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"HTML content saved to {save}")