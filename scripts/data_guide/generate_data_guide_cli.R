library(quarto)
library(synapser)
synLogin()
args <- commandArgs(trailingOnly = TRUE)
release <- args[1]
project_id <- args[2]

project_ent = synGet(project_id)

quarto::quarto_render("data_guide.qmd",
                      execute_params = list("release" = release,
                                            "db_mapping_synid" = project_ent$annotations$dbMapping))
