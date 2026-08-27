def format_cube_comments(gray, colour_space, bit_depth, exif_metadata, statistics, sample_data):
    """ Format calibration gray values, colour space, bit depth, exit metadata, statistics and sample data into .cube comments. """
    comments = []

    # Include image format data
    comments.append('(x, y, z): (L*, a*, b*)')
    comments.append(f'gray;{str(gray)}')
    comments.append([f'ColorSpace;{colour_space}', f'BitDepth;{bit_depth}'])

    # Include image metadata
    metadata_list = []
    for key in exif_metadata.get_exif_data().keys():
        metadata_list.append(key + ';' + str(exif_metadata.get_exif_data()[key]))
    comments[2] = str(tuple(metadata_list))

    # Include calibration accuracy information
    calibration_stats = []
    ref_data_types = ('avg_ciede2000', 'min_ciede2000', 'max_ciede', 'avg_dL', 'avg_da', 'avg_db')
    for i in range(6):
        calibration_stats.append(ref_data_types[i] + ';' + str(statistics[ref_data_types[i]]))
    comments.append(str(tuple(calibration_stats)))

    # Include color sample information (indexing is 1-based for the sample data)
    sample_texts = []
    sample_data_types = ['ciede2000', 'dL', 'da', 'db']
    for l_y in sample_data[1].keys():
        for l_x in sample_data.keys():
            sample_text = f'({l_x}, {l_y})'
            for i in range(4):
                sample_text += ';' + sample_data_types[i] + ';' + str(sample_data[l_x][l_y][sample_data_types[i]])
            sample_texts.append(sample_text)
    comments.append(str(tuple(sample_texts)))

    return comments