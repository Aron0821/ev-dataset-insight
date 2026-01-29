from src.scripts.extract import extract
from src.scripts.transform import transform
from src.scripts.load import load

def display_ev_analysis():
    print("\n")
    print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
    print("▓                                                 ▓")
    print("▓                  EV  ANALYSIS                   ▓")
    print("▓                                                 ▓")
    print("▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓")
    print("\n")

def main():
    try:
        process = int(
            input(
                "Choose ETL process id:\n 1.Extraction 2. Transformation 3. Load 4. All\n"
            )
        )

        if process == 1:
            extract()
        elif process == 2:
            transform()
        elif process == 3:
            load()
        elif process == 4:
            extract()
            transform()
            load()
        else:
            print("[-] Enter between 1,2,3,4!")

    except Exception:
        print("[-] Enter valid integer between 1,2,3,4! ")


if __name__ == "__main__":
    display_ev_analysis()
    main()
