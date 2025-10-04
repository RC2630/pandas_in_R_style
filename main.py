from rshift_piping import Pipable as RshiftPipable
from dot_piping import Pipable as DotPipable
from pandas_R import *

def rshift_piping_demo() -> None:

    df = tibble(
        x = [1, 3, 2, 5, 4],
        y = [3, 0, -1, 4, 3],
        z = [2, 2, 5, 2, 1]
    ); print(df)

    df_filter = filter(df, "x % 2 == 1", "y > 0"); print(df_filter)
    df_filter_pipe = RshiftPipable(df) \
        >> (filter, ("x % 2 == 1", "y > 0")) \
        >> RshiftPipable.VALUE; print(df_filter_pipe)

    df_select = select(df, "z", "x"); print(df_select)
    df_select_pipe = RshiftPipable(df) \
        >> (select, ("z", "x")) \
        >> RshiftPipable.VALUE; print(df_select_pipe)

    df_mutate = mutate(df, a = "@x + 2", b = "@a * 2"); print(df_mutate)
    df_mutate_pipe = RshiftPipable(df) \
        >> (mutate, dict(a = "@x + 2", b = "@a * 2")) \
        >> RshiftPipable.VALUE; print(df_mutate_pipe)

    df_combined = select(
        filter(
            mutate(
                df, a = "5 * @x"
            ), "a > 12"
        ), "y", "a", "z"
    ); print(df_combined)

    df_combined_pipe = RshiftPipable(df) \
        >> (mutate, dict(a = "5 * @x")) \
        >> (filter, "a > 12") \
        >> (select, ("y", "a", "z")) \
        >> RshiftPipable.VALUE; print(df_combined_pipe)

# ------------------------------------------------------------------------------------

def dot_piping_demo() -> None:

    DotPipable.set_available_callables(eval(DotPipable.GET_AVAILABLE_CALLABLES))

    df = tibble(
        x = [1, 3, 2, 5, 4],
        y = [3, 0, -1, 4, 3],
        z = [2, 2, 5, 2, 1]
    ); print(df)

    df_filter = filter(df, "x % 2 == 1", "y > 0"); print(df_filter)
    df_filter_pipe = DotPipable(df, True).filter("x % 2 == 1", "y > 0"); print(df_filter_pipe)

    df_select = select(df, "z", "x"); print(df_select)
    df_select_pipe = DotPipable(df).select("z", "x"); print(df_select_pipe)

    df_mutate = mutate(df, a = "@x + 2", b = "@a * 2"); print(df_mutate)
    df_mutate_pipe = DotPipable(df).mutate(a = "@x + 2", b = "@a * 2"); print(df_mutate_pipe)

    df_combined = select(
        filter(
            mutate(
                df, a = "5 * @x"
            ), "a > 12"
        ), "y", "a", "z"
    ); print(df_combined)

    df_combined_pipe = (DotPipable(df, True) .
        mutate(a = "5 * @x") .
        filter("a > 12") .
        select("y", "a", "z"))
    print(df_combined_pipe)

# ------------------------------------------------------------------------------------

if __name__ == "__main__":
    pass