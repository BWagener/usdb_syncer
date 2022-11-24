"""Functionality related to notes.txt file parsing."""

import os
import re

from usdb_syncer.download_options import TxtOptions
from usdb_syncer.logger import SongLogger
from usdb_syncer.meta_tags.deserializer import MetaTags


def parse_notes(notes: str) -> tuple[dict[str, str], list[str]]:
    """Split notes string into interable header and body.

    Parameters:
        notes: note file string

    Returns:
        header and body of note file
    """
    header: dict[str, str] = {}
    body: list[str] = []

    for line in notes.split("\n"):
        if line.startswith("#"):
            key, value = line.split(":", 1)
            # #AUTHOR should be #CREATOR
            if key == "#AUTHOR":
                key = "#CREATOR"
            # some quick fixes to improve song search in other databases
            if key in ["#ARTIST", "#TITLE", "#EDITION", "#GENRE"]:
                value = value.replace("´", "'")
                value = value.replace("`", "'")
                value = value.replace(" ft. ", " feat. ")
                value = value.replace(" ft ", " feat. ")
                value = value.replace(" feat ", " feat. ")
            header[key] = value.strip()
        else:
            body.append(line.replace("\r", "") + "\n")
    return header, body


def is_duet(header: dict[str, str], meta_tags: MetaTags) -> bool:
    """Check if song is duet.

    Parameters:
        header: song meta data
        resource_params: additional resource parameters from video tag

    Returns:
        True if song is duet
    """
    title = header["#TITLE"].lower()
    edition = header.get("#EDITION")
    edition = edition.lower() if edition else ""
    duet = "duet" in title or "duet" in edition or meta_tags.is_duet()
    return duet


def generate_filename(header: dict[str, str]) -> str:
    """Create file name from song meta data.

    Parameters:
        header: song meta data

    Returns:
        file name
    """
    artist = header["#ARTIST"]
    title = header["#TITLE"]
    # replace special characters
    replacements = [(r"\?|:|\"", ""), ("<", "("), (">", ")"), (r"\/|\\|\||\*", "-")]
    for replacement in replacements:
        artist = re.sub(replacement[0], replacement[1], artist).strip()
        title = re.sub(replacement[0], replacement[1], title).strip()
    return f"{artist} - {title}"


def dump_notes(
    header: dict[str, str],
    body: list[str],
    pathname: str,
    txt_options: TxtOptions,
    logger: SongLogger,
) -> str:
    """Write notes to file.

    Parameters:
        header: song meta data
        body: song notes
        encoding: file encoding
        newline: newline character

    Returns:
        file name
    """
    filename = f"{generate_filename(header)}.txt"
    logger.debug(f"writing text file with encoding {txt_options.encoding.value}")
    with open(
        os.path.join(pathname, filename),
        "w",
        encoding=txt_options.encoding.value,
        newline=txt_options.newline.value,
    ) as notes_file:
        tags = [
            "#TITLE",
            "#ARTIST",
            "#LANGUAGE",
            "#EDITION",
            "#GENRE",
            "#YEAR",
            "#CREATOR",
            "#MP3",
            "#COVER",
            "#BACKGROUND",
            "#VIDEO",
            "#VIDEOGAP",
            "#START",
            "#END",
            "#PREVIEWSTART",
            "#BPM",
            "#GAP",
            "#RELATIVE",
            "#P1",
            "#P2",
            "#MEDLEYSTARTBEAT",
            "#MEDLEYENDBEAT",
        ]
        for tag in tags:
            if value := header.get(tag):
                notes_file.write(tag + ":" + value + "\n")
        for line in body:
            notes_file.write(line)
    return filename
