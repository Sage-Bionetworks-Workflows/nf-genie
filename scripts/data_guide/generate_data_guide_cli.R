library(quarto)
args <- commandArgs(trailingOnly = TRUE)
release <- args[1]
db_mapping_synid <- args[2]

quarto::quarto_render("data_guide.qmd",
                      execute_params = list("release" = release,
                                            "db_mapping_synid" = db_mapping_synid))
