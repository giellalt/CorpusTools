# -*- coding:utf-8 -*-
import argparse
import multiprocessing
import os
import re

from lxml import etree

from corpustools import argparse_version, corpuspath, modes, util

LANGS_RE = re.compile("/(\w+)2(\w+)/")


def append_files(folder_paths):
    return (
        os.path.join(root, file)
        for folder_path in folder_paths
        for root, _, files in os.walk(folder_path)
        for file in files
        if file.endswith(".tmx")
    )


def process_in_parallel(files_list):
    """Process file in parallel."""

    pool_size = multiprocessing.cpu_count() * 2
    pool = multiprocessing.Pool(processes=pool_size)
    pool.map(process_file, files_list)
    pool.close()  # no more tasks
    pool.join()  # wrap up current tasks
    return


def handle_header(header, file_name):
    c = corpuspath.CorpusPath(file_name)
    c.pathcomponents.genre
    genre = etree.Element("genre")
    genre.text = c.pathcomponents.genre
    header.insert(1, genre)


def make_analysis_element(tuv, pipeline, lang):
    seg = tuv.find("seg")
    out = pipeline.run(seg.text.encode("utf8"))

    analysis = etree.Element("analysis")
    analysis.text = (
        "\n".join(
            [
                make_formatted_line(lang, current_cohort)
                for current_cohort in [cohort for cohort in out.split('\n"<') if cohort]
            ]
        )
        + "\n"
    )

    return analysis


def process_file(tmx_file):
    print("... processing", str(tmx_file))
    langs = LANGS_RE.search(tmx_file).groups()

    tree = etree.parse(tmx_file)
    f_root = tree.getroot()
    handle_header(f_root.find(".//header"), tmx_file)
    for lang in langs:
        add_analysis_elements(tree, lang)
    write_file(tmx_file, tree)


def make_pipeline(lang):
    try:
        pipeline = modes.Pipeline("hfst", lang)
        pipeline.sanity_check()
    except util.ArgumentError:
        pipeline = modes.Pipeline("hfst_no_korp", lang)
        pipeline.sanity_check()
    finally:
        return pipeline


def add_analysis_elements(tree, lang):
    pipeline = make_pipeline(lang)

    for tuv in tree.xpath(
        './/tuv[@xml:lang="' + lang + '"]',
        namespaces={"xml": "http://www.w3.org/XML/1998/namespace"},
    ):
        tuv.insert(1, make_analysis_element(tuv, pipeline, lang))


def write_file(tmx_file, tree):
    korp_tmx_file = tmx_file.replace("/tmx", "/korp_tmx")
    with util.ignored(OSError):
        os.makedirs(os.path.dirname(korp_tmx_file))

    print("DONE. Wrote", korp_tmx_file, "\n\n")
    with open(korp_tmx_file, "wb") as done_stream:
        done_stream.write(etree.tostring(tree, xml_declaration=True, encoding="utf-8"))


def make_formatted_line(lang, current_cohort):
    wform, lemma, analysis, pos = make_line_parts(lang, current_cohort)
    return wform + "\t" + lemma + "\t" + pos + "\t" + analysis


def make_line_parts(lang, current_cohort):
    (wform, *cc_list) = current_cohort.split("\n\t")

    wform = make_wordform(wform)
    l_a = sorted(cc_list)[0]
    lemma = make_lemma(l_a)
    analysis = make_analysis(lang, l_a)
    pos = analysis.partition(".")[0]

    return wform, lemma, analysis, pos


def make_analysis(lang, l_a):
    analysis = l_a.partition('" ')[2].partition("@")[0]

    if "?" in analysis:
        return "___"

    for (unwanted, replacement) in [
        ("Err/Orth", ""),
        (" <" + lang + ">", ""),
        (" <vdic>", ""),
        (" Sem/Date", ""),
        (" Sem/Org", ""),
        (" Sem/Sur", ""),
        (" Sem/Fem", ""),
        (" Sem/Mal", ""),
        (" Sem/Plc", ""),
        (" Sem/Obj", ""),
        (" Sem/Adr", ""),
        ("Sem/Adr ", ""),
        (" Sem/Year", ""),
        (" IV", ""),
        (" TV", ""),
        ("v1 ", ""),
        ("v2 ", ""),
        ("Hom1 ", ""),
        ("Hom2 ", ""),
    ]:
        analysis = analysis.replace(unwanted, replacement)
    if analysis.startswith("Arab Num"):
        analysis = analysis.replace("Arab Num", "Num Arab")
    analysis = analysis.strip()
    analysis = analysis.replace("  ", " ")
    analysis = analysis.replace(" ", ".")

    return analysis


def make_lemma(l_a):
    lemma = l_a.partition('" ')[0].strip()
    lemma = lemma.replace("#", "")
    lemma = lemma.replace(" ", "_")
    if lemma.startswith('"'):
        lemma = lemma[1:]

    return lemma


def make_wordform(wform):
    wform = wform.strip()
    if wform.startswith('"<'):
        wform = wform[2:]
    if wform.endswith('>"'):
        wform = wform[:-2]
    wform = wform.replace(" ", "_")

    return wform


def parse_options():
    parser = argparse.ArgumentParser(
        parents=[argparse_version.parser],
        description="Prepare tmx files for use in Korp.",
    )

    parser.add_argument("in_dirs", nargs="+", help="the tmx directories")

    return parser.parse_args()


def main():
    process_in_parallel(append_files(parse_options().in_dirs))
