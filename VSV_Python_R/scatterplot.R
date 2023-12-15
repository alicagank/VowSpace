library(ggplot2)
library(scales)

data <- read.csv('user_dataset.csv')

if ("source" %in% colnames(data)) {
  my_plot <- ggplot(data = data) +
    geom_text(
      aes(x = F2, y = F1, label = vowel, color = language),
      position = position_nudge(x = -0.1)  # Adjust the x offset as needed
    ) +
    geom_polygon(
      aes(x = F2, y = F1, fill = language, color = language),
      alpha = 0.2,
    ) +
    scale_x_reverse() +
    scale_y_reverse() +
    labs(title = "Vowel Spaces", x = "F2") +
    guides(color = FALSE) +
    scale_fill_manual(values = c("seagreen1", "tomato2"), name = "Language") +
    scale_color_manual(values = c("seagreen1", "tomato2")) +
    theme_bw()
} else {
  my_plot <- ggplot(data = data) +
    geom_text(
      aes(x = F2, y = F1, label = vowel),
      color = "black",
      position = position_nudge(x = -0.1)  # Adjust the x offset as needed
    ) +
    geom_polygon(
      aes(x = F2, y = F1),
      alpha = 0.2,
      fill = "seagreen1",
      color = "black",
    ) +
    scale_x_reverse() +
    scale_y_reverse() +
    labs(title = "Vowel Space", x = "F2") +
    theme_bw()
}

# Save the plot as a 600x600 JPG file
ggsave(
  "vsv.jpg",
  plot = my_plot,
  device = "jpeg",
  width = 6,
  height = 6,
  units = "in",
  dpi = 300
)

