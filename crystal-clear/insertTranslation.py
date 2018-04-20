import sqlite3


def main():
    PATH_TO_TRANSLATION = "./translated_Definitions.txt"

    conn = sqlite3.connect('sqlitedb.db')
    c = conn.cursor()

    with open(PATH_TO_TRANSLATION, "r") as ins:
        for line in ins:
            engW, spanW, defin, engP, spanP = line.split("$")
            if spanP[-1] == '\n':
                spanP = spanP[0:len(spanP) - 1]
            c.execute("select englishW from translation where (?) = englishW", (engW,))
            all_rows = c.fetchall()
            if all_rows == []:
                print(engW + " \n" + spanW + "\n" + defin + "\n" + engP + "\n" + spanP)
                c.execute(
                    "insert into translation (englishW, spanishW, definition, englishP, spanishP) values (?,?,?,?,?)",
                    (engW, spanW, defin, engP, spanP))
    conn.commit()
    conn.close()


if __name__ == '__main__':
    main()
