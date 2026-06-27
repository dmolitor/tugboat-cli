library(ggplot2)
library(scales)
library(tibble)

dat <- tibble("x" = c(1, 2, 3), y = c(1, 4, 9))

ggplot(dat, aes(x = x, y = y)) + geom_point() + geom_line() + theme_minimal()