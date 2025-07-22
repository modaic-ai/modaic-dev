import asyncio
import logging
import signal
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import List, Callable
from src.db.pg import engine, SessionLocal
from sqlalchemy import text


class GracefulExit:
    """
    Manage graceful shutdown of background tasks and database connections
    """

    def __init__(self):
        self.background_tasks: List[asyncio.Task] = []
        self.shutdown_requested = False
        self.shutdown_complete = asyncio.Event()

    def register_background_task(self, task: asyncio.Task):
        """
        Register a background task for graceful shutdown tracking
        """
        self.background_tasks.append(task)

    async def wait_for_tasks(self, timeout: float = 30.0):
        """
        Wait for all background tasks to complete with a timeout
        """
        if not self.background_tasks:
            return

        try:
            await asyncio.wait_for(
                asyncio.gather(*self.background_tasks, return_exceptions=True),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            logging.warning("Some background tasks did not complete within the timeout")
        except Exception as e:
            logging.error(f"Error during task shutdown: {e}")


def create_sigterm_handler(
    graceful_exit: GracefulExit, cleanup_funcs: List[Callable] = None
):
    """
    Create a SIGTERM handler with comprehensive shutdown logic
    """

    def sigterm_handler(signum, frame):
        if not graceful_exit.shutdown_requested:
            graceful_exit.shutdown_requested = True
            logging.info("SIGTERM received. Initiating graceful shutdown...")

            # create an async task to handle shutdown
            async def shutdown():
                try:
                    # execute any additional cleanup functions
                    if cleanup_funcs:
                        for func in cleanup_funcs:
                            try:
                                func()
                            except Exception as e:
                                logging.error(f"Error in cleanup function: {e}")

                    # wait for background tasks to complete
                    await graceful_exit.wait_for_tasks()

                    # final logging
                    logging.info("Graceful shutdown completed")
                except Exception as e:
                    logging.error(f"Shutdown process error: {e}")
                finally:
                    graceful_exit.shutdown_complete.set()
                    sys.exit(0)

            # run the shutdown coroutine
            asyncio.create_task(shutdown())

    return sigterm_handler


def test_postgres_connection():
    """Test PostgreSQL connection"""
    try:
        db = SessionLocal()
        # simple query to test connection
        db.execute(text("SELECT 1"))
        db.close()
        return True
    except Exception as e:
        logging.error(f"PostgreSQL connection failed: {e}")
        return False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Enhanced lifespan context manager with robust SIGTERM handling
    """
    graceful_exit = GracefulExit()
    app.state.graceful_exit = graceful_exit

    def cleanup_databases():
        try:
            engine.dispose()
            logging.info("Disconnected from PostgreSQL")
        except Exception as e:
            logging.error(f"Error during PostgreSQL disconnection: {e}")

    signal.signal(
        signal.SIGTERM,
        create_sigterm_handler(graceful_exit, cleanup_funcs=[cleanup_databases]),
    )

    try:
        if test_postgres_connection():
            logging.info("SUCCESS: CONNECTED TO POSTGRESQL")
        else:
            raise Exception("Failed to connect to PostgreSQL")

        logging.info("SUCCESS: CONNECTED TO ALL DATABASES")
        yield

    except Exception as e:
        logging.error(f"ERROR: Failed to connect to databases: {str(e)}")
        cleanup_databases()  # cleanup on startup failure
        raise e

    finally:
        cleanup_databases()
