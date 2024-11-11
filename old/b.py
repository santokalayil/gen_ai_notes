from pathlib import Path
from enum import Enum
from typing import Any
import datetime
import instructor
import google.generativeai as genai
from pydantic import BaseModel
import PyPDF2


class Prompts:
    prompts_dir = Path("./prompts")
    
    @property
    def index_info(self) -> str:
        index_info_path = self.prompts_dir / "index_info.txt"
        return index_info_path.read_text()


class AI:
    def __init__(self,) -> None:
        self.client = self.get_model()
    
    def authenticate(self,) -> None:
        API_KEY = "YOUR_API_KEY"
        genai.configure(api_key=API_KEY)
        
    def get_model(self) -> instructor.AsyncInstructor:
        return instructor.from_gemini(
            client=genai.GenerativeModel(
                model_name="models/gemini-1.5-flash-latest",
            ),
            mode=instructor.Mode.GEMINI_JSON,
        )
        
    def ask(self, system_prompt: str, user_prompt: str, response_model: Any) -> Any:
        return self.client.messages.create(
            messages=[
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            response_model=response_model,
        )
        


class EventType(str, Enum):
    RECON = "Reconstition"
    REBAL = "Rebalancing"
    
class DateInfo(BaseModel):
    effective_date: str
    reference_date: str
    annoucement_date: str
    sharestrike_date: str | None
    
class SecurityType(str, Enum):
    COMMONSTOCK = "Common Stock"
    ADR = "ADR"
    

class IndexBaseInfo(BaseModel):
    ticker: str
    available_events: list[EventType]
    exchanges: list[str]
    # is_factset_index: bool
    dates_info: DateInfo
    qualification_filters: list[str]
    allowed_security_types: list[SecurityType]
    
    def to_dict(self) -> dict:
        return self.model_dump()

class PDFReader:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.reader = PyPDF2.PdfReader(self.path)
        self.pages = self.reader.pages
        self.n_pages = len(self.pages)
    
    def read(self) -> str:
        txts = []
        for n in range(self.n_pages):
            page = self.pages[n]
            txt = page.extract_text()
            txts.append(txt)
            # (temp_pages_dir / f"{idx+1}.txt").write_text(txt)

        full_text: str = "<pagebreak />".join(txts)
        return full_text
    

class Index():
    def __init__(self) -> None:
        self.ai = AI()
        self.methodology_doc: PDFReader
        self.info: IndexBaseInfo
        self._prompts = Prompts()
      
    def read_methodology(self, path: Path) -> IndexBaseInfo:
        self.methodology_doc = PDFReader(path)
        self.info = self.ai.ask(
            self._prompts.index_info, 
            self.methodology_doc.read(), 
            IndexBaseInfo
        )
        
    def calculate_dates(self) -> None:
        ...


class IndexDate(BaseModel):
    effective_date: datetime.date
    reference_date: datetime.date
    sharestrike_date: datetime.date | None
    annoucement_date: datetime.date
    
class IndexDates(BaseModel):
    past_dates: list[IndexDate]
    upcoming_dates: list[IndexDate]

  
idx = Index()
idx.read_methodology(path=Path("NYSE_FANGplus_Index_Methodology.pdf"))

date_identifier_sys_prompt = f"""
You are an expert who finds dates from date logic that is passed. 
The dates for index Rebalancing or Reconstitution are to be fetched for past 4 quarters/times
and the dates of two upcoming quarters/times as well. Today's date is {datetime.date.today()}

Please note:
1. Upcoming or past (for recon/rebalance) is identified based on effective date. 
    Eg: if today is Nov 2, and reference date is at Nov 30, and then if the effective date is in December consider the quarter as upcoming quarter rather than past quarter
2. If share strike date is empty, then pass NOT_FOUND
"""

date_identifier_usr_prompt = f"""
Effective Date Logic: {idx.info.dates_info.effective_date}
Reference Date Logic: {idx.info.dates_info.reference_date}
Share Strike Date Logic: {idx.info.dates_info.sharestrike_date}
Announcement Date Logic: {idx.info.dates_info.annoucement_date}
"""


index_dates: IndexDates = idx.ai.ask(
    system_prompt=date_identifier_sys_prompt,
    user_prompt=date_identifier_usr_prompt,
    response_model=IndexDates
)
# sorting
index_dates = IndexDates(
    past_dates=sorted(index_dates.past_dates, key=lambda x: x.effective_date),
    upcoming_dates=sorted(index_dates.upcoming_dates, key=lambda x: x.effective_date)
)
index_dates.past_dates
index_dates.upcoming_dates

# ai = AI()
# idx_info: IndexBaseInfo = ai.ask(prompts.index_info, full_text, IndexBaseInfo)
    
# class PDFDOC(BaseModel):
#     data: dict


# client = instructor.from_gemini(
#     client=genai.GenerativeModel(
#         model_name="models/gemini-1.5-flash-latest",
#     ),
#     mode=instructor.Mode.GEMINI_JSON,
# )

# note that client.chat.completions.create will also work
# # client.chat.com
# idx_info: IndexBaseInfo = client.messages.create(
#     messages=[
#         {
#             "role": "system",
#             "content": prompts.index_info
#         },
#         {
#             "role": "user",
#             "content": full_text,
#         }
#     ],
#     response_model=IndexBaseInfo,
# )
# idx_info

# idx_info.model_dump()


# idx_info.dates_info

# STEP 2. Find previous 


        

# assert isinstance(resp, Index)
# assert resp.name == "Jason"
# assert resp.age == 25

# extract pdf text
# extact base info of index (LLM)
# identify if it is FS/or ICE index (coding or classification from few shot)
# - give NYFSJPM - FS is there, so it is FactSet Index
# 



