"""Teste adicional: o CLI processa todas as linhas do arquivo, sem limite fixo."""

from helpers import run_cli


def test_all_rows_are_processed_beyond_200(tmp_path):
    """Arquivos com mais de 200 reservas não podem ser truncados na leitura."""
    total_rows = 300
    report = run_cli(
        tmp_path,
        [{"reservation_id": f"R-{index}", "amount": "100.00"} for index in range(1, total_rows + 1)],
    )
    summary = report["summary"]
    assert summary["total_reservations"] == total_rows
    assert summary["confirmed_reservations"] == total_rows
    assert summary["total_room_nights"] == total_rows
    assert summary["total_amount_brl"] == "30000.00"
