import os
import zipfile


def create_project_zip() -> str:
    output_zip = "generated_project.zip"
    source_dir = "generated"

    if not os.path.exists(source_dir):
        os.makedirs(source_dir, exist_ok=True)

    with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                filepath = os.path.join(root, file)
                arcname = os.path.relpath(filepath, source_dir)
                zipf.write(filepath, arcname)

    return output_zip