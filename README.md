# `pandas` in R style

This little project aims to showcase how you can emulate the "look and feel" of R code (specifically `tidyverse` code) in Python (`pandas`). It provides functions like `tibble()`, `filter()`, `select()`, and `mutate()` which behave like their `tidyverse` counterparts but act on `pd.DataFrame`s (`pandas`).

The project also defines 2 distinct pipe operators, namely `>>` and `.`. Both pipe operators emulate the behaviour of the pipe operators in R (i.e. `%>%` in `tidyverse` and `|>` in base-R). The former operator (`>>`) is a bit more flexible but has uglier syntax, while the latter operator (`.`) has some usage limitations but has almost exactly R-like syntax. Using the pipe operators (especially `.`), you will be able to write Python code that looks deceptively similar to the R (`tidyverse`) code that performs the same operations.

Please enjoy my little project, and have a lot of fun with it!