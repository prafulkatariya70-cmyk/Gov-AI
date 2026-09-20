from datetime import date

from bs4 import BeautifulSoup

from app.services.ingestion.karnataka_teacher_adapter import (
    KarnatakaTeacherAdapter,
)


def test_karnataka_teacher_parse_official_event():
    html = """
    <html>
      <body>
        <h1>PST/PE-Grade-II/GPT/AM/CST/PE-Grade-I Teachers Recruitment</h1>
        <table id="ContentPlaceHolder1_grd">
          <tr>
            <th>Event</th>
            <th>Start</th>
            <th>End</th>
          </tr>
          <tr>
            <td>Applicant Registration</td>
            <td>18-08-2026 17:00</td>
            <td>25-09-2026 23:59</td>
          </tr>
        </table>
      </body>
    </html>
    """

    job = KarnatakaTeacherAdapter()._parse_page(html)

    assert job is not None
    assert job.organization_name == "Government of Karnataka"
    assert job.title == (
        "PST/PE-Grade-II/GPT/AM/CST/PE-Grade-I "
        "Teachers Recruitment"
    )
    assert job.application_start == date(2026, 8, 18)
    assert job.application_end == date(2026, 9, 25)
    assert job.official_url.endswith("/final.aspx")
    assert job.notification_url is None
    assert job.source_name == "KARNATAKA_TEACHER"
    assert job.external_id == "karnataka-gpsthrnhk-recruitment"
    assert job.opportunity_type == "PUBLIC_RECRUITMENT"


def test_karnataka_teacher_rejects_missing_registration_window():
    html = """
    <html>
      <body>
        <h1>Teachers Recruitment</h1>
        <table id="ContentPlaceHolder1_grd">
          <tr>
            <td>Other Event</td>
            <td>18-08-2026 17:00</td>
            <td>25-09-2026 23:59</td>
          </tr>
        </table>
      </body>
    </html>
    """

    assert KarnatakaTeacherAdapter()._parse_page(html) is None


def test_karnataka_teacher_extracts_cycle_into_external_id():
    soup = BeautifulSoup(
        "<html><body>GSTR-2026 Teachers Recruitment</body></html>",
        "html.parser",
    )

    assert (
        KarnatakaTeacherAdapter()._extract_cycle(soup)
        == "GSTR-2026"
    )
    assert (
        KarnatakaTeacherAdapter()._build_external_id("GSTR-2026")
        == "karnataka-gpsthrnhk-gstr-2026"
    )


def test_karnataka_teacher_external_id_is_stable_without_cycle():
    assert (
        KarnatakaTeacherAdapter()._build_external_id(None)
        == "karnataka-gpsthrnhk-recruitment"
    )


def test_karnataka_teacher_datetime_parser_rejects_invalid_value():
    assert (
        KarnatakaTeacherAdapter()._parse_datetime(
            "2026-08-18 17:00"
        )
        is None
    )
