from unittest.mock import Mock, patch

from app.services.ingestion.rrb_adapter import RRBAdapter, RRB_CEN_URL


def test_fetch_page_uses_official_regional_rrb_endpoint():
    response = Mock()
    response.text = "<html></html>"
    response.raise_for_status.return_value = None

    with patch("app.services.ingestion.rrb_adapter.httpx.get", return_value=response) as get:
        html = RRBAdapter()._fetch_page()

    assert html == "<html></html>"
    assert get.call_args.args[0] == RRB_CEN_URL
    assert RRB_CEN_URL == "https://rrb.indianrailways.gov.in/bhubaneswar/"


def test_parse_page_resolves_relative_notification_links_to_regional_page():
    html = """
    <table>
      <tr>
        <td>14-07-2026</td>
        <td>CEN 03/2026</td>
        <td><a href="notifications/cen-03-2026.pdf">Section Controller Recruitment</a></td>
        <td>Section Controller</td>
      </tr>
    </table>
    """

    jobs = RRBAdapter()._parse_page(html)

    assert len(jobs) == 1
    assert jobs[0].external_id == "CEN 03/2026"
    assert jobs[0].notification_url == (
        "https://rrb.indianrailways.gov.in/bhubaneswar/notifications/cen-03-2026.pdf"
    )
