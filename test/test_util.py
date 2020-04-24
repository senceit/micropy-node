from util import Logger, StringBuilder


def test_string_builder():
    sb = StringBuilder()
    string = sb.add("hello").space().add("world").newline().build()

    assert string == "hello world\r\n"

    sb = StringBuilder()
    string = sb.add("hello").space().add("world").newline().newline().build()

    assert string == "hello world\r\n\r\n"


def test_logger_singleton():
    log1 = Logger.getLogger()
    log2 = Logger.getLogger()

    assert log1 == log2

    log1.warn("This is a warning")
    log1.info("This is some info")
    log1.severe("This is severe")
