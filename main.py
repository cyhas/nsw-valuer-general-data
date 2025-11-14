from queries import avg_med_twelve_months, median_avg_growth_periods
import duckdb

def ascii_art():
    f = open("assets/ascii.txt", 'r')
    ascii = f.read()
    print(ascii)


def application():
    suburb = input("Enter suburb name: ").strip()
    query = avg_med_twelve_months.format(suburb=suburb)
    df = duckdb.query(query).to_df()
    print(df)

    query = median_avg_growth_periods.format(suburb=suburb)
    df = duckdb.query(query).to_df()
    print(df)


def main():
    ascii_art()
    application()

if __name__ == '__main__':
    main()