library(broom)
library(dplyr)
library(forcats)
library(ggplot2)
library(patchwork)
library(purrr)
library(scales)
library(stringr)
library(tibble)
library(tidyr)

dat <- as_tibble(diamonds)

summary_tbl <- dat |>
  group_by(cut) |>
  summarise(
    median_price = median(price),
    q25 = quantile(price, 0.25),
    q75 = quantile(price, 0.75),
    .groups = "drop"
  ) |>
  mutate(cut = fct_reorder(cut, median_price))

p_bar <- ggplot(summary_tbl, aes(x = cut, y = median_price, ymin = q25, ymax = q75)) +
  geom_col(fill = "#2c7bb6", alpha = 0.85) +
  geom_errorbar(width = 0.3, color = "#444") +
  scale_y_continuous(labels = dollar) +
  labs(
    title = "Median Price by Cut",
    subtitle = "Error bars show IQR",
    x = "Cut", y = "Median Price"
  ) +
  theme_minimal()

set.seed(42)
p_scatter <- dat |>
  slice_sample(n = 5000) |>
  ggplot(aes(x = carat, y = price, color = color)) +
  geom_point(alpha = 0.4, size = 0.7) +
  scale_y_continuous(labels = dollar) +
  scale_color_brewer(palette = "YlOrRd") +
  labs(
    title = "Price vs. Carat by Color",
    x = "Carat", y = "Price", color = "Color"
  ) +
  theme_minimal()

ggsave("diamond_pricing.png", p_bar + p_scatter, width = 12, height = 5, dpi = 150)
