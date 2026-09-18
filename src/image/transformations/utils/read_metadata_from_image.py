import exiftool

def read_metadata_from_image(image_location: str) -> dict:
    # Read metadata from image using exiftool
    with exiftool.ExifToolHelper() as et:
        metadata = et.get_metadata(image_location)

    # Validate metadata content based on structure
    if len(metadata) == 0:
        raise ValueError(f"No metadata found in image: {image_location}")
    elif len(metadata) > 1:
        raise ValueError(f"Multiple metadata entries found in image: {image_location}")

    # Return the metadata dictionary
    return dict(metadata[0])