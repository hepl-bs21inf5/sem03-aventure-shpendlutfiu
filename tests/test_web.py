from glob import glob
from html.parser import HTMLParser
from os import path
from subprocess import check_output


def test_index():
    assert path.isfile("index.html"), "Il faut le fichier 'index.html'."


def test_html():
    for file in glob("**/*.html", recursive=True):
        output = check_output(
            [
                "curl",
                "-s",
                "-H",
                "Content-Type: text/html",
                "--data-binary",
                f"@{file}",
                "https://validator.w3.org/nu/?out=gnu&level=error",
            ],
        ).decode()
        assert "" == output, f"{file} {output}"


def test_css():
    count: int = 0
    for file in glob("**/*.css", recursive=True):
        count += 1
        output = check_output(
            [
                "curl",
                "-s",
                "-H",
                "Content-Type: text/css",
                "--data-binary",
                f"@{file}",
                "https://validator.w3.org/nu/?out=gnu",
            ],
        ).decode()
        assert "" == output, f"{file} {output}"
    assert count > 0, "Il faut au moins un fichier CSS."


def test_tags():
    any_tags: set[str] = set()
    all_tags: set[str] = set()

    class MyHTMLParser(HTMLParser):
        inner_tags: set[str] = set()

        def handle_starttag(self, tag, _):
            any_tags.add(tag)
            self.inner_tags.add(tag)

    parser = MyHTMLParser()
    for file in glob("**/*.html", recursive=True):
        parser.inner_tags.clear()
        parser.feed(open(file).read())
        if all_tags:
            all_tags &= parser.inner_tags
        else:
            all_tags = parser.inner_tags.copy()

    assert "title" in all_tags, "Il faut un titre (onglet) dans chaque fichier."
    assert "h1" in all_tags, "Il faut un titre de niveau 1 dans chaque fichier."
    assert "p" in all_tags, "Il faut au moins un paragraphe dans chaque fichier."

    assert "img" in any_tags, "Il faut au moins une image dans le projet."
