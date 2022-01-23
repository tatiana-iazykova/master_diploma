import argparse


def get_argparse() -> argparse.ArgumentParser:
    """
    Create ArgumentParser.

    :return: parser
    :rtype: argparse.ArgumentParser
    """

    # parse arguments and load configuration file
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--label_frequency_file",
        type=str,
        help="path to label frequency file",
    )
    parser.add_argument(
        "--path_to_df",
        type=str,
        help="path to original dataframe",
    )
    parser.add_argument(
        "--path_to_mapping",
        type=str,
        help="path to mapping",
    )

    parser.add_argument(
        "--output_dir",
        type=str,
        help="path to saving directory",
    )

    return parser
