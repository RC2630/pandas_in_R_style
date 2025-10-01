from pandas import DataFrame as DF
from typing import Any

class Internal:

    @staticmethod
    def replace_variable_references(s: str, df_name: str, column_names: list[str]) -> str:
        result: str = s
        sorted_column_names: list[str] = sorted(column_names, key = lambda colname: -len(colname))
        for colname in sorted_column_names:
            prefixed_colname: str = f"@{colname}"
            replace_expr: str = f"{df_name}['{colname}']"
            result = result.replace(prefixed_colname, replace_expr)
        return result

# ------------------------------------------------------------------------------------

def tibble(**kwargs: list[Any]) -> DF:
    return DF(kwargs)

def filter(df: DF, *conditions: str) -> DF:
    safe_conditions: list[str] = [f"({condition})" for condition in conditions]
    return df.query(" and ".join(safe_conditions))

def select(df: DF, *columns: str) -> DF:
    columns_list: list[str] = list(columns)
    return df.loc[:, columns_list]

def mutate(df: DF, **columns_and_values: str) -> DF:
    new_df: DF = df.copy()
    for column, value in columns_and_values.items():
        processed_value: str = Internal.replace_variable_references(
            value, "new_df", list(new_df.columns)
        )
        new_df[column] = eval(processed_value)
    return new_df