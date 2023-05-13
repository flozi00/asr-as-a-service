import os
import random
import time
from functools import lru_cache
from typing import Optional

import fsspec
from sqlmodel import Field, Session, SQLModel, create_engine, select

from aaas.statics import CACHE_SIZE, INPROGRESS, TODO, TASK_MAPPING

db_backend = os.getenv("DBBACKEND", "sqlite:///database.db")
ftp_backend = os.getenv("FTPBACKEND")
try:
    ftp_user = ftp_backend.split("@")[0]
    ftp_pass = ftp_backend.split("@")[1]
    ftp_server = ftp_backend.split("@")[2]
except Exception:
    ftp_user, ftp_pass, ftp_server = None, None, None


class QueueData(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    metas: str
    transcript: str = Field(max_length=4096)
    model_config: str
    hash: str = Field(unique=True)


engine = create_engine(db_backend, pool_recycle=3600, pool_pre_ping=True)
SQLModel.metadata.create_all(engine)


def add_to_queue(audio_batch, hashes, times_list):
    # Create a session to the database
    with Session(engine) as session:
        # Loop over all audio files in the batch
        for x in range(len(audio_batch)):
            # Get the audio data
            audio_data = audio_batch[x]
            hs = hashes[x]
            # Get the timestamps for the current audio file
            time_dict = times_list[x]
            # in case its asr with timestamps
            for task in list(TASK_MAPPING.keys()):
                if (
                    TASK_MAPPING[task][0] in time_dict
                    and TASK_MAPPING[task][1] in time_dict
                ):
                    timesstamps = f"{time_dict[TASK_MAPPING[task][0]]},{time_dict[TASK_MAPPING[task][1]]},{task}"

            # Get the entry from the database. If there is no entry, it returns None
            entry = get_transkript(hs)
            # If there is no entry in the database
            if entry is None:
                # Create a new entry
                entry = QueueData(
                    metas=timesstamps,
                    transcript=TODO,
                    model_config="large",
                    hash=hs,
                )
                # Add the audio data to the database
                set_data_to_hash(hs, audio_data)
                # Add the new entry to the session
                session.add(entry)
                # Commit the changes to the database
                session.commit()


def get_transkript(hs: str) -> QueueData:
    """Get a transkript from the database by its hash
    Args:
        hs (str): The hash of the transkript

    Returns:
        QueueData: The transkript from the database in a QueueData object
    """
    with Session(engine) as session:
        statement = select(QueueData).where(QueueData.hash == hs)
        transkript = session.exec(statement).first()

    return transkript


def get_transkript_batch(hs: str) -> list:
    """Get a transkript from the database by its hash in a batch

    Args:
        hs (str): The hashes of the transkripts separated by a comma

    Returns:
        _type_: The transkripts from the database in a QueueData object in a list
    """
    with Session(engine) as session:
        statement = select(QueueData).where(QueueData.hash.in_(hs.split(",")))
        transkript = session.exec(statement).all()

    return transkript


def get_tasks_queue() -> QueueData:
    """Get a random item from the queue

    Returns:
        QueueData: A random item from the queue
    """
    with Session(engine) as session:

        def get_queue():
            statement = select(QueueData).where(QueueData.transcript == TODO)
            todos = session.exec(statement).all()
            return todos

        todos = get_queue()

        # Check if there are any items in the queue
        if len(todos) == 0:
            # Get all items that are in progress
            statement = select(QueueData).where(QueueData.transcript == INPROGRESS)
            todos = session.exec(statement).all()
            # Check if any items are in progress
            if len(todos) != 0:
                sample = random.choice(todos)
            else:
                todos = []

        if len(todos) != 0:
            sample = todos[0]
        else:
            sample = False

    print("open todos ", len(todos))
    return sample


def set_transkript(hs: str, transcription: str, from_queue: bool = False):
    """Set the transcription of an audio file

    Args:
        hs (str): The hash of the audio file
        transcription (str): The transcription of the audio file
    """
    with Session(engine) as session:
        statement = select(QueueData).where(QueueData.hash == hs)
        transkript = session.exec(statement).first()
        if from_queue is True and "***" not in transkript.transcript:
            pass
        else:
            if transkript is not None:
                if transcription != transkript.transcript:
                    transkript.transcript = transcription
                    session.commit()
                    session.refresh(transkript)


def set_in_progress(hs: str):
    """Set the transcription of an audio file to "INPROGRESS"

    Args:
        hs (str): The hash of the audio file
    """
    with Session(engine) as session:
        statement = select(QueueData).where(QueueData.hash == hs)
        transkript = session.exec(statement).first()
        if transkript is not None:
            transkript.transcript = INPROGRESS
            session.commit()
            session.refresh(transkript)


@lru_cache(maxsize=CACHE_SIZE)
def get_data_from_hash(hash: str) -> bytes:
    """Get the bytes of a file from the path which is the hash of the file

    Args:
        hash (str): hash of the file to be retrieved

    Returns:
        bytes: bytes of the file to be retrieved
    """
    if ftp_backend is not None:
        fs = fsspec.filesystem(
            "ftp",
            host=ftp_server,
            username=ftp_user,
            password=ftp_pass,
            port=21,
            block_size=2**20,
        )
    else:
        fs = fsspec.filesystem("file")
    with fs.open(f"data/{hash}", "rb") as f:
        bytes_data = f.read()

    return bytes_data


def set_data_to_hash(hs: str, bytes_data: bytes):
    """Store the bytes of a file to the path which is the hash of the file

    Args:
        data (str): hash of the file to be stored
        bytes_data (bytes): bytes of the file to be stored
    """
    if ftp_backend is not None:
        fs = fsspec.filesystem(
            "ftp",
            host=ftp_server,
            username=ftp_user,
            password=ftp_pass,
            port=21,
            block_size=2**20,
        )
    else:
        fs = fsspec.filesystem("file")
    try:
        with fs.open(f"data/{hs}", "wb") as f:
            f.write(bytes_data)
    except Exception as e:
        print(e)
        time.sleep(1)
        set_data_to_hash(hs, bytes_data)


def remove_data_from_hash(hs: str):
    if ftp_backend is not None:
        fs = fsspec.filesystem(
            "ftp",
            host=ftp_server,
            username=ftp_user,
            password=ftp_pass,
            port=21,
            block_size=2**20,
        )
    else:
        fs = fsspec.filesystem("file")

    try:
        fs.rm(f"data/{hs}")
    except Exception as e:
        print(e)
