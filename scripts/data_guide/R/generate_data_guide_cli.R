library(quarto)
library(synapser)
library(glue)

synLogin()
args <- commandArgs(trailingOnly = TRUE)
release <- args[1]
project_id <- args[2]
# release <- "14.6-consortium"
# project_id <- "syn3380222"

get_release_folder_synid <- function(database_synid_mappingid, release) {
  database_synid_mapping = synTableQuery(glue('select * from {synid}',
                                              synid = database_synid_mappingid))
  database_synid_mappingdf = synapser::as.data.frame(database_synid_mapping)
  release_folder_ind = database_synid_mappingdf$Database == "releaseFolder"
  release_folder_fileview_synid = database_synid_mappingdf$Id[release_folder_ind]

  choose_from_release = synTableQuery(glue("select distinct(name) as releases from {synid} where ",
                                           "name not like 'Release%' and name <> 'case_lists'",
                                           synid = release_folder_fileview_synid))
  releases = synapser::as.data.frame(choose_from_release)
  if (release == "TEST.consortium") {
    release = "TESTING"
  } else if (release == "TEST.public") {
    release = "TESTpublic"
  }
  if (!any(releases$releases %in% release)) {
    stop(glue("Must choose correct release: {releases}",
              releases = paste0(releases$releases, collapse = ", ")))
  }

  release_folder = synTableQuery(glue("select id from {synid} where name = '{release}'",
                                      synid = release_folder_fileview_synid,
                                      release = release),
                                 includeRowIdAndRowVersion = F)
  release_folder$asDataFrame()$id
}

quarto::quarto_render("data_guide.qmd",
                      execute_params = list("release" = release,
                                            "project_id" = project_id))

project_ent = synGet(project_id)

database_synid_mappingid = project_ent$annotations$dbMapping

release_folder_synid <- get_release_folder_synid(database_synid_mappingid, release)
data_guide_ent = File("data_guide.pdf", parentId=release_folder_synid)
synStore(data_guide_ent, executed="https://github.com/Sage-Bionetworks-Workflows/nf-genie")
