import pandas as pd


def queryTable(conn, tablename, colname, value, *colnames):
    """
    This function queries a table using `colname = value` as a filter.
    All columns in colnames are returned. If no colnames are specified, `select *` is performed

    :param conn: the connection with the database to be used to execute/fetch the query
    :param tablename: the tablename to query
    :param colname: the column to filter by
    :param value: the value to filter by
    :param colnames: the columns to fetch in the result
    """

    if not colnames: colnames = "*"
    else: colnames = ', '.join(colnames)

    df = pd.read_sql(f"SELECT {colnames} FROM {tablename} WHERE {colname}='{value}'", conn)
    return df

def queryTableNew(conn, tablename, colname1, value1, colname2, value2, *colnames):
    """
    This function queries a table using `colname = value` as a filter.
    All columns in colnames are returned. If no colnames are specified, `select *` is performed

    :param conn: the connection with the database to be used to execute/fetch the query
    :param tablename: the tablename to query
    :param colname: the column to filter by
    :param value: the value to filter by
    :param colnames: the columns to fetch in the result
    """

    if not colnames: colnames = "*"
    else: colnames = ', '.join(colnames)

    df = pd.read_sql(f"SELECT {colnames} FROM {tablename} WHERE {colname1}='{value1}' AND {colname2}= '{value2}'", conn)
    return df


def currencyFormatter(n):
    """
    Format a number as it if were currency. Force two decimal places of precision

    :param n: a number to format
    """

    s = format(round(n, 2), ',')  # formatted with ','s as the 100s separator
    if '.' not in s: s += '.'
    tail = len(s.rsplit('.',1)[-1])
    s += '0'*(2-tail)  # rpad decimal precision to 2 places
    return s


def cumsumByGroup(df):
    """
    Given a dataframe, group the dateaframe by AccounNumber. Sort each group by date, multiply the Amount by -1 for CR/DR and perform a cumsum

    :param df: a pandas dataframe containing transaction information across multiple accounts for one customer
    """

    df.sort_values(by=['AccountNumber', 'Date'], inplace=True, ignore_index=True)  # we can sort by date here, just the one time, rather than having to sort each group individually

    # get a signed amount by CR/DR
    df['NetAmount'] = df.Amount
    df.loc[df.CRDR=='DR', 'NetAmount'] = df[df.CRDR=='DR']['NetAmount']*-1
    df['AvailableBalance'] = None  # new column for the cumsum
    for accountNum in df.AccountNumber.unique():  # cumsum for each account number
        df.loc[df.AccountNumber==accountNum, 'AvailableBalance'] = df[df.AccountNumber==accountNum].NetAmount.cumsum()

    df.sort_values(by=['Date'], inplace=True, ignore_index=True)  # sort again by date, so that all transactions are stratified by date
    df.fillna(value='', inplace=True)  # so that None's don't show up in the st.write(df)
    return df
