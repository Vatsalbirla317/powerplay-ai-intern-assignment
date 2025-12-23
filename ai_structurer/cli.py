"""CLI entrypoint for running the processing pipeline."""
from argparse import ArgumentParser
from .runner import process_all_inputs, write_outputs


def main():
    p = ArgumentParser()
    p.add_argument("--input", "-i", required=True, help="Path to input text file")
    p.add_argument("--output", "-o", default="outputs.json", help="Path to output JSON")
    p.add_argument("--model", "-m", default="llama3-70b-8192", help="Groq model id")
    args = p.parse_args()

    records = process_all_inputs(args.input, model=args.model)
    write_outputs(records, args.output)


if __name__ == "__main__":
    main()