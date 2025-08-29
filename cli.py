import sys
from engine import load_and_process

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python cli.py <file_path>")
        sys.exit(1)
    path = sys.argv[1]
    df = load_and_process(path)
    df.to_csv("exports/processed_payroll.csv", index=False)
    print("✅ File processed. Saved to exports/processed_payroll.csv")
