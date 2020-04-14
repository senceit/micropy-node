from util import Logger


def test_logger_singleton():
    log1 = Logger.getLogger()
    log2 = Logger.getLogger()

    assert log1 == log2

    log1.warn("This is a warning")
    log1.info("This is some info")
    log1.severe("This is severe")
