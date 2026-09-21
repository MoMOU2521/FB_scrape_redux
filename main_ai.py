# main_ai.py
import sys

# from ai.runner import run_gate1, run_extraction, run_pipeline

# from ai.runner.run_extraction import run_extraction
from ai.runner.run_pipeline import run_pipeline

# from ai.runner.run_gate1 import run_gate1


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py [gate1|extraction|pipeline|transliterate]")
        sys.exit(1)

    # if sys.argv[1] == "gate1":
    #     run_gate1()
    # elif sys.argv[1] == "extraction":
    #     run_extraction()
    elif sys.argv[1] == "pipeline":
        run_pipeline()
    # elif sys.argv[1] == "transliterate":
    #     run_transliterate()
    else:
        print("Invalid. Use 'gate1', 'extraction', 'pipeline', or 'transliterate'")


if __name__ == "__main__":
    main()
