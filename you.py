from datetime import date
import mysql.connector as msql

pas = input("password: ")

try:
    cn = msql.connect(host='localhost', user='root', passwd=pas, database='daily')
    cur = cn.cursor()
except msql.Error as e:
    print(f"couldn't connect: {e}")
    exit()

def get_date_input():
    return input("date (YYYY-MM-DD): ").strip()

def print_entry(row):
    star = "⭐" if row[2] == 1 else "  "
    print(f"  {star} {row[0]}  —  {row[1]}")

def no_entry():
    print("  nothing found for that date.")

def new_entry():
    today = date.today()
    text = input("what happened today? (max 100 chars): ").strip()[:100]

    starred = input("star this day? (y/n): ").strip().lower()
    if starred not in ('y', 'n'):
        print("  just y or n please")
        return
    star = 1 if starred == 'y' else 0

    cur.execute(
        "INSERT INTO daily_journal (`date`, entry, star_the_day) VALUES (%s, %s, %s)",
        (today, text, star)
    )
    cn.commit()
    print("  saved!")

def read_all():
    cur.execute("SELECT * FROM daily_journal ORDER BY date DESC")
    rows = cur.fetchall()

    if not rows:
        print("  diary is empty.")
        return

    print("\n── all entries")
    for row in rows:
        print_entry(row)
    print()

def read_by_date():
    d = get_date_input()
    cur.execute("SELECT * FROM daily_journal WHERE `date` = %s", (d,))
    row = cur.fetchone()

    if row:
        print()
        print_entry(row)
    else:
        no_entry()

def read_starred():
    cur.execute("SELECT * FROM daily_journal WHERE star_the_day = 1 ORDER BY date DESC")
    rows = cur.fetchall()

    if not rows:
        print("  no starred days yet.")
        return

    print("\n── starred")
    for row in rows:
        print_entry(row)
    print()

def search():
    kw = input("search for: ").strip()
    cur.execute("SELECT * FROM daily_journal WHERE entry LIKE %s ORDER BY date DESC", (f"%{kw}%",))
    rows = cur.fetchall()

    if not rows:
        print(f"  nothing found for '{kw}'")
        return

    print(f"\n── results for '{kw}'")
    for row in rows:
        print_entry(row)
    print()

def update_entry():
    d = get_date_input()
    cur.execute("SELECT * FROM daily_journal WHERE `date` = %s", (d,))
    row = cur.fetchone()

    if not row:
        no_entry()
        return

    print(f"  current: {row[1]}")
    new_text = input("new entry: ").strip()[:100]

    starred = input("star this day? (y/n): ").strip().lower()
    if starred not in ('y', 'n'):
        print("  just y or n please")
        return
    star = 1 if starred == 'y' else 0

    cur.execute(
        "UPDATE daily_journal SET entry = %s, star_the_day = %s WHERE `date` = %s",
        (new_text, star, d)
    )
    cn.commit()
    print("  updated!")

def delete_entry():
    d = get_date_input()
    cur.execute("SELECT * FROM daily_journal WHERE `date` = %s", (d,))
    row = cur.fetchone()

    if not row:
        no_entry()
        return

    print(f"  going to delete: {row[1]}")
    sure = input("are you sure? (yes to confirm): ").strip().lower()
    if sure != 'yes':
        print("  cancelled.")
        return

    cur.execute("DELETE FROM daily_journal WHERE `date` = %s", (d,))
    cn.commit()
    print("  deleted.")

def delete_all():
    sure = input("delete EVERYTHING? this can't be undone. (yes to confirm): ").strip().lower()
    if sure != 'yes':
        print("  phew, cancelled.")
        return

    cur.execute("DELETE FROM daily_journal")
    cn.commit()
    print("  all gone.")

actions = {
    1: new_entry,
    2: read_all,
    3: read_by_date,
    4: read_starred,
    5: search,
    6: update_entry,
    7: delete_entry,
    8: delete_all,
}

menu = """
my diary

1. new entry
2. read all
3. find by date
4. starred days
5. search
6. edit an entry
7. delete an entry
8. delete everything
9. quit
"""

# keep running until user types 9
while True:
    print(menu)

    try:
        choice = int(input("pick a number: "))
    except ValueError:
        print("  that's not a number")
        continue

    if choice == 9:
        print("  bye!")
        break

    action = actions.get(choice)
    if action:
        action()
    else:
        print("  not a valid option")

cur.close()
cn.close()