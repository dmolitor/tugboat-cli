library(ggplot2)
library(scales)
library(tibble)

dat <- as_tibble(read.csv("predictions.csv"))

r2 <- 1 - sum(dat$residual^2) / sum((dat$actual - mean(dat$actual))^2)
r2_label <- sprintf("R² = %.3f", r2)

p_fit <- ggplot(dat, aes(x = actual, y = predicted)) +
  geom_point(alpha = 0.6, color = "#2c7bb6") +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", color = "#d7191c") +
  annotate(
    "text",
    x = -Inf,
    y = Inf,
    label = r2_label,
    hjust = -0.2,
    vjust = 1.5,
    size = 4
  ) +
  labs(
    title = "Predicted vs. Actual Disease Progression",
    x = "Actual", y = "Predicted"
  ) +
  theme_minimal()

p_resid <- ggplot(dat, aes(x = predicted, y = residual)) +
  geom_point(alpha = 0.6, color = "#2c7bb6") +
  geom_hline(yintercept = 0, linetype = "dashed", color = "#d7191c") +
  geom_smooth(method = "loess", se = FALSE, color = "#1a9641", linewidth = 0.8) +
  labs(
    title = "Residuals vs. Fitted",
    x = "Fitted value", y = "Residual"
  ) +
  theme_minimal()

ggsave("predicted_vs_actual.png", p_fit, width = 6, height = 5, dpi = 150)
ggsave("residuals.png", p_resid, width = 6, height = 5, dpi = 150)
