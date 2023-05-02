"""Generate the code reference pages."""

from pathlib import Path

import mkdocs_gen_files

import os

nav = mkdocs_gen_files.Nav()

cwd = Path(os.getcwd())

# with mkdocs_gen_files.open("reference/index.md", "w") as f:
#     print("hei hei", file=f)

for path in sorted(Path("..", "corpustools").rglob("*.py")):
    module_path = path.relative_to("..").with_suffix("")
    doc_path = path.relative_to("..", "corpustools").with_suffix(".md")
    full_doc_path = Path("reference", doc_path)

    parts = tuple(module_path.parts)

    # print(f"{parts=}")
    # continue

    if parts[-1] == "__init__":
        parts = parts[:-1]
        doc_path = doc_path.with_name("index.md")
        full_doc_path = full_doc_path.with_name("index.md")
    elif parts[-1] == "__main__":
        continue

    # if len(parts) == 0:
    #     print("WTF", list(module_path.parts))
    #     continue
    nav[parts] = doc_path.as_posix()

    with mkdocs_gen_files.open(full_doc_path, "w") as fd:
        identifier = ".".join(parts)
        print("::: " + identifier, file=fd)

    mkdocs_gen_files.set_edit_path(full_doc_path, Path("..") / path)

with mkdocs_gen_files.open("reference/SUMMARY.md", "w") as nav_file:
    nav_file.writelines(nav.build_literate_nav())
