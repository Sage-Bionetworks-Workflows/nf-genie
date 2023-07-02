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

project_ent = synGet(project_id)

database_synid_mappingid = project_ent$annotations$dbMapping

release_folder_synid <- get_release_folder_synid(database_synid_mappingid, release)
data_guide_ent = File("data_guide.pdf", parentId=release_folder_synid)
synStore(data_guide_ent, executed="https://github.com/Sage-Bionetworks-Workflows/nf-genie")
