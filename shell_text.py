def get_shelltext(text: str, color: str = "default", style: str = "default") -> str:
    """Create colorful custom shell texts. """

    shell_styles = {"default": 0, "bold": 1, "faded": 2,
                        "italic": 3, "uline": 4, "blink": 5, "bg": 7}

    shell_colors = {"default": 0, "blue": 30, "red": 31, "green": 32,
                    "yellow": 33, "salmon": 34, "purple": 35, "cyan": 36,  "grey": 37}

    return f'\033[{shell_styles[style]};{shell_colors[color]}m{text}\033[0m'
