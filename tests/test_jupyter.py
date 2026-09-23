from unittest.mock import MagicMock, patch

from error_translator.jupyter import custom_exc, load_ipython_extension


def test_load_ipython_extension():
    mock_ipython = MagicMock()
    load_ipython_extension(mock_ipython)
    mock_ipython.set_custom_exc.assert_called_once_with((Exception,), custom_exc)


@patch("error_translator.jupyter.translate_error")
@patch("error_translator.jupyter.AutoFormattedTB")
def test_custom_exc(mock_auto_tb, mock_translate, capsys):
    mock_shell = MagicMock()
    mock_tb = MagicMock()
    mock_evalue = Exception("Test error")

    mock_tb_instance = MagicMock()
    mock_auto_tb.return_value = mock_tb_instance
    mock_tb_instance.text.return_value = "raw traceback text"

    mock_translate.return_value = {"explanation": "Test explanation", "fix": "Test fix"}

    custom_exc(mock_shell, Exception, mock_evalue, mock_tb)

    mock_auto_tb.assert_called_once_with(mode="Plain", theme_name="NoColor")
    mock_tb_instance.text.assert_called_once_with(Exception, mock_evalue, mock_tb)
    mock_translate.assert_called_once_with("raw traceback text")

    captured = capsys.readouterr()
    assert "Error: Test explanation" in captured.out
    assert "Fix: Test fix" in captured.out


def test_custom_exc_survives_real_exception():
    from IPython.testing.globalipapp import get_ipython

    from error_translator.jupyter import custom_exc, load_ipython_extension

    ip = get_ipython()
    load_ipython_extension(ip)
    ip.run_cell("1/0")
    # IPython unregisters a handler that raised; assert ours is still active.
    assert ip.CustomTB is custom_exc or (
        hasattr(ip.CustomTB, "__closure__")
        and ip.CustomTB.__closure__ is not None
        and ip.CustomTB.__closure__[0].cell_contents is custom_exc
    )
    assert ip.custom_exceptions == (Exception,)
