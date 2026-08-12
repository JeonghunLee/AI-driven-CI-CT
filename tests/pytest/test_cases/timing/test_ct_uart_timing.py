def test_ct_uart_timing(uart, saleae):
    uart.write("PING")
    assert uart.read() == "PING"

    metrics = saleae.capture_uart_metrics()
    assert metrics["error"] < 0.02
    assert metrics["jitter"] < 0.02
