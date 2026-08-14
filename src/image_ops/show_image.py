def show_image(window_name: object, in_img: object, convert: object = True, save_to_disk: object = False) -> object:
    """Show image in window, with option to save to disk"""
    global _save_counter

    if convert:
        # Convert to sRGB 8bit
        in_img = image_manipulation.convert_color(in_img, 'show')

    # Check if the image should be saved to disk
    if save_to_disk:
        _save_counter += 1
        # Construct the file path and save the image
        save_directory = os.path.join(settings.main_directory, settings.directories[3])
        if not os.path.exists(save_directory):
            os.makedirs(save_directory)

        # Add an index to the filename to make it unique
        file_name = f"{window_name.replace(' ', '_')}_{_save_counter}.png"
        file_path = os.path.join(save_directory, file_name)
        cv.imwrite(file_path, in_img[0])
        print(f"Image saved to: {file_path}")
    else:
        cv.imshow(window_name, in_img[0])
        cv.setWindowProperty(window_name, cv.WND_PROP_TOPMOST, 1)  # Set as top window