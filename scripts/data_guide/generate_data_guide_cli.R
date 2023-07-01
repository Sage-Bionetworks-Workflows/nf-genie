library(quarto)
library(synapser)
synLogin()
args <- commandArgs(trailingOnly = TRUE)
release <- args[1]
project_id <- args[2]
# release <- "14.6-consortium"
# project_id <- "syn3380222"

quarto::quarto_render("data_guide.qmd",
                      execute_params = list("release" = release,
                                            "project_id" = project_id))
