from prompt_toolkit import prompt
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.formatted_text import to_formatted_text
from prompt_toolkit.styles import Style


exitLoop = False
kb = KeyBindings()
style = Style([("b", "#abc993 bold")])


def bottom_toolbar():
    return to_formatted_text(
        HTML(
            """<b>Ctrl-c</b>: Cancel
<b>Ctrl-n</b>: Skip to next item, <b>&lt;Enter&gt;</b> Save and next item
<b>Ctrl-s</b>: Sanitize"""
        )
    )

class SkipEvent(Exception):
    pass

@kb.add("c-c")
def _(event):
    global exitLoop
    exitLoop = True
    event.app.exit()


@kb.add("c-n")
def _(event):
    event.app.exit(exception=SkipEvent)


@kb.add("c-s")
def _(event):
    text = event.app.current_buffer.text
    event.app.current_buffer.text = text.replace("-", " ")


def interactive_rename(field: str):
    while not exitLoop:
        try:
            text = prompt(
                f"({field}): ",
                default="Receipt-for-Stuff",
                key_bindings=kb,
                bottom_toolbar=bottom_toolbar,
                style=style,
            )
            if not exitLoop:
                print(f"Setting {field} to {text}")
        except SkipEvent:
            print("skip event")
