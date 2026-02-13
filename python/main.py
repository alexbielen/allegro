from allegro.numbers import fit, FitMode
from allegro.pitchclass import transpose, invert
from allegro.physical import stub


def main():
    print(stub())
    print(fit(FitMode.Wrap, 0, 12, 13))
    print(transpose(1, 0))
    print(invert(0))


if __name__ == "__main__":
    main()
