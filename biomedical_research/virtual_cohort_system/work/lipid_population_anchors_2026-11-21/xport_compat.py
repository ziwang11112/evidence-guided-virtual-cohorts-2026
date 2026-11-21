"""Read legacy variable labels, then invoke the unchanged frozen scientific evaluator."""
import argparse
from contextlib import contextmanager

import evaluate
import survey

original_reader = survey.XportReader


@contextmanager
def legacy_labels(path):
    with original_reader(path) as reader:
        for column in reader.fields:
            label = column["label"]
            try:
                label.decode("utf-8")
            except UnicodeDecodeError:
                column["label"] = label.decode("cp1252").encode("utf-8")
        yield reader


if __name__ == "__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("predictions_commit")
    survey.XportReader = legacy_labels
    evaluate.main(cli.parse_args().predictions_commit)
