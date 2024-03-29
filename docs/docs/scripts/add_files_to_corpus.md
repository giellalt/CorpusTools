# add_files_to_corpus

`add_files_to_corpus = corpustools.adder:main"`

The complete help text from the program is as follows:

```sh
usage: add_files_to_corpus [-h] [--version] [--name NAME] [-p PARALLEL_FILE]
                           [-l LANG] [-d DIRECTORY]
                           origs [origs ...]

Add file(s) to a corpus directory. The filenames are converted to ascii only
names. Metadata files containing the original name, the main language, the
genre and possibly parallel files are also made. The files are added to the
working copy.

positional arguments:
  origs                 The original files, urls or directories where the
                        original files reside (not the corpus repository)

options:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  --name NAME           Specify the name of the file in the corpus. Especially
                        files fetched from the net often have names that are
                        not human friendly. Use this option to guard against
                        that.

parallel:
  -p PARALLEL_FILE, --parallel PARALLEL_FILE
                        Path to an existing file in the corpus that will be
                        parallel to the orig that is about to be added
  -l LANG, --lang LANG  Language of the file to be added

no_parallel:
  -d DIRECTORY, --directory DIRECTORY
                        The directory where the origs should be placed
```

## Examples

Download and add parallel files from the net to the corpus:

`cd $GTFREE`

### Adding the first file

The command

```sh
add_files_to_corpus -d corpus-sme-orig/admin/sd/other_files http://www.samediggi.no/content/download/5407/50892/version/2/file/Sametingets+%C3%A5rsmelding+2013+-+nordsamisk.pdf
```

Gives the message:

```sh
Added corpus-sme-orig/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_nordsamisk.pdf
```

### Adding the parallel file

```sh
add_files_to_corpus -p corpus-sme-orig/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_nordsamisk.pdf -l nob  http://www.samediggi.no/content/download/5406/50888/version/2/file/Sametingets+%C3%A5rsmelding+2013+-+norsk.pdf
```

Gives the message:

```sh
Added corpus-nob-orig/admin/sd/other_files/sametingets_ay-rsmelding_2013_-_norsk.pdf
```

After this is done, you will have to commit the files to the working copy, like
this:

```sh
cd corpus-sme-orig
git commit
cd ../corpus-nob-orig
git commit
```
