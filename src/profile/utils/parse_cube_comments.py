import ast

def parse_cube_comments(comments: list[str]):
    """ Obtain calibration gray values, colour space, bit depth, exit metadata, statistics and sample data from .cube comments. """
    # Read profile reference gray LAB
    gray = ast.literal_eval(comments[1].split(';')[1])

    # Third line contains colour space, bit depth and EXIF metadata
    color_space, bit_depth = ast.literal_eval(comments[2])[:2]
    metadata_dict = {}
    for md in ast.literal_eval(comments[2]):
        metadata_dict[md.split(';')[0]] = md.split(';')[1]
    exif_metadata = ExifMetaData.from_data(color_space, bit_depth, metadata_dict)

    # Fourth line contains some sample statistics of the calibration
    statistics = {}
    for field in ast.literal_eval(comments[3]):
        statistics[field.split(';')[0]] = field.split(';')[1]

    # Fifth line contains the colour coordinates of the sample data
    sample_data = {}
    for entry in ast.literal_eval(comments[4]):
        parts = entry.split(';')
        grid_point = ast.literal_eval(parts[0])
        sample_data[grid_point] = {
            parts[i]: float(parts[i + 1]) for i in range(1, len(parts), 2)
        }

    return {'gray': gray, 'color_space': color_space, 'bit_depth': bit_depth, 'exit_metadata': exif_metadata, 'statistics': statistics, 'sample_data': sample_data}
