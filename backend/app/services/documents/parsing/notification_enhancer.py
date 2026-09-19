from __future__ import annotations
import re
from dataclasses import replace
from datetime import date, datetime
from app.services.documents.parsing.notification_parser import NotificationParser, ParsedField, ParsedNotification

class NotificationParserEnhancer:
    """Conservative post-parser enrichment for official notification wording variants."""
    def __init__(self, parser: NotificationParser | None = None): self.parser=parser or NotificationParser()
    def parse(self,text: str)->ParsedNotification:
        parsed=self.parser.parse(text)
        normalized=text.replace("\u2018","'").replace("\u2019","'")
        title=parsed.title; vacancy=parsed.vacancy_count; min_age=parsed.minimum_age; max_age=parsed.maximum_age; start=parsed.application_start; end=parsed.application_end; pay=parsed.pay_level; advertisement=parsed.advertisement_number; vacancy_number=parsed.vacancy_number
        m=re.search(r"\bAdvertisement\s*(?:No\.?|Number)\s*[:#-]?\s*(\d{1,3})\s*[-/]\s*(\d{4})\b",normalized,re.I)
        if not advertisement.value and m: advertisement=ParsedField(f"{m.group(1)}-{m.group(2)}",m.group(0),"high")
        m=re.search(r"\bVacancy\s+No\.?\s*[:#-]?\s*(\d{8,14})\b",normalized,re.I)
        if not vacancy_number.value and m: vacancy_number=ParsedField(m.group(1),m.group(0),"high")
        m=re.search(r"(?:\b\w[\w -]*\s+)?vacancies?\s+for\s+the\s+posts?\s+of\s+([^\n.]+)",normalized,re.I)
        if not m:
            m=re.search(r"\b(?:recruitment|applications?)\b.{0,120}?\bposts?\s+of\s+([^\n.]+)",normalized,re.I|re.S)
        if not m:
            m=re.search(r"\b\d{1,4}\s+posts?\s+of\s+([^\n.]+)",normalized,re.I)
        if not title.value and m: title=ParsedField(m.group(1).strip(),m.group(0),"high")
        m=re.search(r"\b(one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|one hundred)\s+vacancies?\s+for\s+the\s+posts?",normalized,re.I)
        if not vacancy.value:
            m_numeric=re.search(r"\b(\d{1,4})\s+posts?\s+of\b",normalized,re.I)
        else:
            m_numeric=None
        if not vacancy.value and m_numeric:
            vacancy=ParsedField(int(m_numeric.group(1)),m_numeric.group(0),"high")
        if not vacancy.value and m:
            words={"one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,"eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,"twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90,"one hundred":100}; vacancy=ParsedField(words[m.group(1).lower()],m.group(0),"high")
        m=re.search(r"\bage:\s*(\d{1,3})\s+years?\s+for\s+UR.*?\b(\d{1,3})\s+years?\s+for\s+SC/ST",normalized,re.I|re.S)
        if m:
            if not min_age.value: min_age=ParsedField(int(m.group(1)),m.group(0),"medium")
            if not max_age.value: max_age=ParsedField(int(m.group(2)),m.group(0),"medium")
        m=re.search(r"closing\s+date\s+for\s+submission\s+of\s+online\s+recruitment\s+application.*?\bon\s+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",normalized,re.I|re.S)
        if not end.value and m:
            try: end=ParsedField(datetime.strptime(m.group(1),"%d-%m-%Y").date(),m.group(0),"high")
            except ValueError: pass
        m=re.search(r"through\s+website\s+.*?from\s+(\d{1,2}[./-]\d{1,2}[./-]\d{2,4})",normalized,re.I|re.S)
        if not start.value and m:
            try: start=ParsedField(datetime.strptime(m.group(1),"%d-%m-%Y").date(),m.group(0),"high")
            except ValueError: pass
        m=re.search(r"\bLevel[- ]\s*(\d+)\s+in\s+the\s+Pay\s+Matrix",normalized,re.I)
        if not pay.value and m: pay=ParsedField(f"Level-{m.group(1)}",m.group(0),"high")
        return replace(parsed,title=title,vacancy_count=vacancy,minimum_age=min_age,maximum_age=max_age,application_start=start,application_end=end,pay_level=pay,advertisement_number=advertisement,vacancy_number=vacancy_number)
