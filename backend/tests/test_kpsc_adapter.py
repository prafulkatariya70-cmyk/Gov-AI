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
