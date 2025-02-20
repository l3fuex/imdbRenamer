import argparse
import logging

logging.basicConfig(
    level=logging.DEBUG, format="%(levelname)-8s %(funcName)s:%(lineno)d - %(message)s"
#    level=logging.INFO, format="%(levelname)-8s %(message)s"
)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "file",
        nargs="*",
        help="Path to file which should be renamed",
    )
    parser.add_argument(
        "-s",
        "--simulate",
        help="No renaming",
        action="store_true",
    )
    parser.add_argument(
        "-o",
        "--offset",
        help="Offset value",
        type=int,
        default=0,
    )
    args = parser.parse_args()

    episode = "3"

    print(args.file)
    print(args.simulate)
    episode = int(episode) + args.offset
    print(episode)

if __name__ == "__main__":
    main()
