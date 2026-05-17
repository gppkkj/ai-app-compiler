import shutil


def create_project_zip():

    shutil.make_archive(
        "generated_project",
        "zip",
        "generated"
    )

    return "generated_project.zip"