# -*- coding:utf-8 -*-
import argparse
import multiprocessing
import os
import re

from corpustools import analyser, argparse_version, corpuspath, korp_mono, util
from lxml import etree

LANGS_RE = re.compile("/(\w+)2(\w+)/")


def process_in_parallel(files_list):
    """Process file in parallel."""

    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(process_file, files_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def process_serially(files_list):
    for file_ in files_list:
        print(f"Converting: {file_}")
        process_file(file_)


def handle_header(header, genre_name):
    genre = etree.Element("genre")
    genre.text = genre_name
    header.insert(1, genre)


def make_analysis_element(analysis, lang):
    analysis_element = etree.Element("analysis")
    analysis_element.text = (
        "\n".join(korp_mono.make_sentences(korp_mono.valid_sentences(analysis), lang))
        + "\n"
    )

    return analysis_element


def process_file(tmx_file):
    print("... processing", str(tmx_file))
    langs = LANGS_RE.search(tmx_file).groups()

    path1 = corpuspath.CorpusPath(tmx_file)
    path2 = corpuspath.CorpusPath(path1.parallel(langs[1]))

    tree = etree.parse(tmx_file)
    f_root = tree.getroot()
    handle_header(f_root.find(".//header"), path1.pathcomponents.genre)
    for path in [path1, path2]:
        add_analysis_elements(tree, path)
    write_file(tmx_file, tree)


def make_analyses(lang, modename, text):
    analysis = []
    for line in analyser.do_dependency_analysis(
        text.encode("utf8"), modename, lang
    ).split("\n"):
        if "¶" in line:
            if analysis:
                yield "\n".join(analysis)
                analysis = []
        else:
            analysis.append(line)

    if analysis:
        yield "\n".join(analysis)


def add_analysis_elements(tree, path):
    modename = analyser.get_modename(path)
    lang = path.pathcomponents.lang
    tuv_elements = tree.xpath(
        './/tuv[@xml:lang="' + lang + '"]',
        namespaces={"xml": "http://www.w3.org/XML/1998/namespace"},
    )

    analyses = make_analyses(
        lang, modename, text="¶ ".join([tuv.find("seg").text for tuv in tuv_elements])
    )

    for (tuv, analysis) in zip(tuv_elements, analyses):
        try:
            tuv.append(make_analysis_element(analysis, lang))
        except IndexError:
            util.print_frame(lang)
            util.print_frame(tuv.find("seg").text)
            util.print_frame(analysis)


def write_file(tmx_file, tree):
    korp_tmx_file = tmx_file.replace("/tmx", "/korp_tmx")
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(korp_tmx_file))

    print("DONE. Wrote", korp_tmx_file, "\n\n")
    with open(korp_tmx_file, "wb") as done_stream:
        done_stream.write(etree.tostring(tree, xml_declaration=True, encoding="utf-8"))


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Prepare tmx files for use in Korp.",
    )

    parser.add_argument(
        "--serial",
        action="store_true",
        help="When this argument is used files will be converted one by one.",
    )
    parser.add_argument(
        "tmx_entities", nargs="+", help="tmx files or directories where tmx files live"
    )

    return parser.parse_args()


def main():
    args = parse_options()
    if args.serial:
        process_serially(util.collect_files(args.tmx_entities, suffix=".tmx"))
    else:
        process_in_parallel(util.collect_files(args.tmx_entities, suffix=".tmx"))
