def test_ct_uart_timing(uart, saleae):
    uart.write("PING")
    assert uart.read() == "PING"

    metrics = saleae.capture_uart_metrics()
    assert metrics["measured_baudrate"] == saleae.measured_baudrate
    assert metrics["jitter"] == saleae.jitter
    assert metrics["error"] == abs(saleae.measured_baudrate - 921600) / 921600
    assert metrics["error"] < 0.02
    assert metrics["jitter"] < 0.02
