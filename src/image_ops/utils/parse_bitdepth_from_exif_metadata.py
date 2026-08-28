def parse_bitdepth_from_exif_metadata(value: str) -> int:
    """Parse an EXIF BitsPerSample string into a single bit-depth value.

    EXIF/TIFF stores BitsPerSample as one value per channel (e.g. "8 8 8"
    for RGB, "8" for grayscale). This assumes all channels share the same
    bit depth, which holds for standard camera captures but is not
    guaranteed by the TIFF spec.

    Args:
        value: The raw exiftool string, e.g. "8 8 8" or "16".

    Returns:
        The shared bit depth as an int.

    Raises:
        ValueError: If the string is empty/malformed, or if the
            per-channel values are not all identical.
    """
    parts = value.split()
    if not parts:
        raise ValueError(f"BitsPerSample value is empty or malformed: {value!r}")

    try:
        bits = [int(p) for p in parts]
    except ValueError as e:
        raise ValueError(f"BitsPerSample contains non-integer values: {value!r}") from e

    if len(set(bits)) != 1:
        raise ValueError(
            f"BitsPerSample channels are not identical, cannot collapse to a "
            f"single value: {bits}"
        )

    return bits[0]