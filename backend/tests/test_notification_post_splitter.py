from app.services.documents.parsing.notification_post_splitter import NotificationPostSplitter


MULTI_POST = """
ADVERTISEMENT NO. 11/2026
UNION PUBLIC SERVICE COMMISSION

(Vacancy No. 26091106212) 140 posts of Assistant Public Prosecutor in Directorate of Prosecution.
PAY LEVEL-10 in the Pay Matrix.

(Vacancy No. 26091106213) 20 posts of another government post.
PAY LEVEL-10 in the Pay Matrix.

(Vacancy No. 26091106214) 52 posts of a third government post.
PAY LEVEL-8 in the Pay Matrix.
"""


def test_splitter_creates_one_block_per_explicit_vacancy_boundary():
    blocks = NotificationPostSplitter().split(MULTI_POST)

    assert len(blocks) == 3
    assert [block.vacancy_number for block in blocks] == [
        "26091106212",
        "26091106213",
        "26091106214",
    ]
    assert all(block.confidence == "high" for block in blocks)


def test_splitter_preserves_single_post_without_inventing_boundaries():
    text = """
    ADVERTISEMENT NO. 52/2026
    UNION PUBLIC SERVICE COMMISSION
    (Vacancy No. 26085201722) Eighty vacancies for the post of Assistant Provident Fund Commissioner.
    """
    blocks = NotificationPostSplitter().split(text)

    assert len(blocks) == 1
    assert blocks[0].vacancy_number == "26085201722"
    assert blocks[0].confidence == "medium"


def test_splitter_parses_each_post_independently():
    parsed = NotificationPostSplitter().parse_blocks(MULTI_POST)

    assert len(parsed) == 3
    assert parsed[0].vacancy_number.value == "26091106212"
    assert parsed[1].vacancy_number.value == "26091106213"
    assert parsed[2].vacancy_number.value == "26091106214"
