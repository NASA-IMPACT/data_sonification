import pandas as pd


def read_data(
    csv_file_path: str,
    columns_to_drop: list = None,
    columns_to_include: list = None,
    index_col=None,
):
    """Funtion takes in various arguments to read the data.

    Args:
        csv_file_path (str): Path fo the file to be read.
        columns_to_drop (list, optional): List of column names to be droped. Defaults to None.
        columns_to_include (list, optional): List of column names to be included. Defaults to None.
        index_col ([type], optional): index of the columns. Defaults to None.

    Returns:
        [DatFrame]: [Returns the dataframe which was read from the given path.]
    """
    if not columns_to_drop:
        columns_to_drop = []
    if not columns_to_include:
        columns_to_include = []
    df = pd.read_csv(csv_file_path, index_col=index_col)
    return df


def customized_data(csv_file_path: str, is_global_warming=False):
    """Function customizes the data which was read from the given path.

    Args:
        csv_file_path (str): Path of the file to be read.
        is_global_warming (bool, optional): True if the dataset is global warming data. Defaults to False.

    Returns:
        [DataFrame]: Returns a processed dataframe.
    """
    df = read_data(csv_file_path=csv_file_path)
    df_origin = df.copy()
    if is_global_warming:
        try:
            df["date_time"] = pd.to_datetime(df["date_time"], format="%Y")
        except:
            pass

    df["date_time"] = pd.to_datetime(df["date_time"])
    df.sort_values(by=["date_time"], inplace=True)
    df.reset_index(inplace=True)
    df["time_elapsed_minutes"] = df["date_time"] - min(df["date_time"])
    df["time_years"] = df.date_time.dt.year
    df["time_elapsed_minutes"] = df["time_elapsed_minutes"].apply(
        lambda row: (row.days * 24 * 60) + (row.seconds // 60)
    )
    df.drop(["index"], axis=1, inplace=True)
    return df_origin,  df
