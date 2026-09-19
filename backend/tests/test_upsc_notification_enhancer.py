from datetime import date
from app.services.documents.parsing.notification_enhancer import NotificationParserEnhancer

REAL_UPSC_EXCERPT="""SPECIAL ADVERTISEMENT NO. 52/2026
UNION PUBLIC SERVICE COMMISSION
1. (Vacancy No. 26085201722) Eighty vacancies for the post of Assistant Provident Fund Commissioner in Employees' Provident Fund Organisation, Ministry of Labour & Employment.
PAY SCALE: Level- 10 in the Pay Matrix as per 7th CPC.
AGE: 35 years for UR/EWS, 38 years for OBC and 40 years for SC/ST.
EDUCATIONAL
Degree of a recognised University or Equivalent.
ONLINE RECRUITMENT APPLICATIONS ARE INVITED FOR DIRECT RECRUITMENT BY SELECTION THROUGH WEBSITE https://upsconline.nic.in/ora/ TO THE ABOVE POSTS FROM 22-08-2026.
CLOSING DATE FOR SUBMISSION OF ONLINE RECRUITMENT APPLICATION THROUGH WEBSITE IS 1800 HRS ON 11-09-2026.
"""

def test_real_upsc_wording_is_enriched():
    parsed=NotificationParserEnhancer().parse(REAL_UPSC_EXCERPT)
    assert parsed.organization_name.value == "Union Public Service Commission"
    assert parsed.title.value == "Assistant Provident Fund Commissioner in Employees' Provident Fund Organisation, Ministry of Labour & Employment"
    assert parsed.vacancy_count.value == 80
    assert parsed.minimum_age.value == 35
    assert parsed.maximum_age.value == 40
    assert parsed.pay_level.value == "Level-10"
    assert parsed.application_start.value == date(2026,8,22)
    assert parsed.application_end.value == date(2026,9,11)
