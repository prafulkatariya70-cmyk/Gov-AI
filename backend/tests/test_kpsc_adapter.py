from datetime import date

from app.services.ingestion.kpsc_adapter import KPSCAdapter


def test_kpsc_extract_notification_links_filters_non_recruitment():
    html = """
    <html>
      <body>
        <a href="./pdf/GP_2026.pdf">
          GP 2026-27 Final Notification
        </a>
        <a href="./pdf/SAAD_RPC_2026.pdf">
          SAAD RPC Notification dt 27-08-2026
        </a>
        <a href="./pdf/SAAD_CORRIGENDUM_2026.pdf">
          Corrigendum Notification
        </a>
        <a href="./pdf/DEPT_EXAM_2026.pdf">
          Departmental Examination 2026
        </a>
        <a href="./pdf/RESULT_2026.pdf">
          Result Notification
        </a>
      </body>
    </html>
    """

    links = KPSCAdapter()._extract_notification_links(html)

    assert len(links) == 2
    assert links[0][0].endswith("/pdf/GP_2026.pdf")
    assert links[1][0].endswith("/pdf/SAAD_RPC_2026.pdf")


def test_kpsc_extract_application_window():
    text = (
        "Online applications are invited from 28-08-2026 "
        "to 26-09-2026 through the Commission website."
    )

    start, end = KPSCAdapter()._extract_application_window(text)

    assert start == date(2026, 8, 28)
    assert end == date(2026, 9, 26)


def test_kpsc_extract_notification_number():
    text = (
        "Notification No. KPSCKA/EXA2/PRSL/10/2026-"
        "EXAM2/251 dated 27-08-2026"
    )

    number = KPSCAdapter()._extract_notification_number(text)

    assert number == (
        "KPSCKA/EXA2/PRSL/10/2026-EXAM2/251"
    )


def test_kpsc_url_id_is_deterministic():
    url = (
        "https://kpsc.kar.nic.in/pdf/"
        "SAAD_RPC_Notification_2026.pdf"
    )

    assert (
        KPSCAdapter()._build_url_id(url)
        == "kpsc-saad-rpc-notification-2026"
    )


def test_kpsc_fetch_notification_page_streams_response(monkeypatch):
    adapter = KPSCAdapter()
    calls = {}

    class FakeResponse:
        encoding = "utf-8"

        def raise_for_status(self):
            pass

        def iter_content(self, chunk_size):
            calls["chunk_size"] = chunk_size
            yield b"<html>"
            yield b" KPSC notifications </html>"

        def close(self):
            calls["closed"] = True

    def fake_get(*args, **kwargs):
        calls["args"] = args
        calls["kwargs"] = kwargs
        return FakeResponse()

    monkeypatch.setattr(
        "app.services.ingestion.kpsc_adapter.requests.get",
        fake_get,
    )

    html = adapter._fetch_notification_page()

    assert html == "<html> KPSC notifications </html>"
    assert calls["kwargs"]["stream"] is True
    assert calls["kwargs"]["timeout"] == (15.0, 20.0)
    assert calls["chunk_size"] == 16384
    assert calls["closed"] is True
