from pathlib import Path
from enum import Enum
from typing import Any
import datetime
import instructor
import vertexai  # type: ignore
from vertexai.generative_models import GenerativeModel, Part, SafetySetting  # type: ignore
from pydantic import BaseModel, Field
from instructor.client_vertexai import from_vertexai
from pydantic import BaseModel
import PyPDF2
import logging

logging.basicConfig(level=logging.DEBUG)

vertexai.init(project="sanai-441017", location="us-central1")


class AIAgent:
    def __init__(self, role: str) -> None:
        self.client = self.get_model(sys_prompt=role)
    
    def authenticate(self,) -> None:
        # API_KEY = "YOUR_API_KEY"
        # genai.configure(api_key=API_KEY)
        vertexai.init(project="sanai-441017", location="us-central1")
        
    def get_model(self, sys_prompt) -> instructor.AsyncInstructor:
        return from_vertexai(
            # gemini-1.5-pro-preview-0409
            # models/gemini-1.5-flash-latest
            client=GenerativeModel("gemini-1.5-pro-preview-0409", system_instruction=[sys_prompt]),
            # mode=instructor.Mode.VERTEXAI_TOOLS,  # instructor.Mode.VERTEXAI_JSON, VERTEXAI_TOOLS
            mode=instructor.Mode.VERTEXAI_TOOLS,
            generation_config = {
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            }
        )

        
    def ask(self, user_prompt: str, response_model: Any) -> Any:
        return self.client.messages.create(
            messages=[
                {
                    "role": "user",
                    "content": user_prompt,
                }
            ],
            response_model=response_model,
        )
        



class EventName(str, Enum):
    RECON = "Reconstition"
    REBAL = "Rebalancing"
    
class EventFrequency(str, Enum):  # need confidence interval here
    YEARLY = "Yearly"
    SEMIANNUALLY = "SemiAnnually",
    QUARTERLY = "Quarterly"

class EventType(BaseModel):
    name: EventName
    frequency: EventFrequency
    
class DateInfo(BaseModel):
    effective_date: str
    reference_date: str
    annoucement_date: str
    sharestrike_date: str = Field(default=None)
    
class SecurityType(str, Enum):
    """Enumeration of Security Types that are allowed"""
    COMMONSTOCK = "Common Stock"
    ADR = "ADR"
    

# class SecurityUniverseSelection(BaseModel):
#     exchange_based: bool = Field(default=False)
#     # exchanges: list[str] = Field(default=[])
#     country_based: bool = Field(default=False)
#     # countries: list[str] = Field(default=[])

class StartingUniverse(BaseModel):
    selected_from_countries: list[str]
    selected_from_exchanges: list[str]

# class Filters(str, Enum):
#     COUNTRY_FILTER = "Country Filter"
#     EXCHANGE_FILTER = "Exchange Filter"
#     NORTHBOUND_FILTER = "Northbound Filter"
#     RANKING_FILTER = "Ranking Filter"
    
    


class IndexBaseInfo(BaseModel):
    """Represents a structured response of an index methodology document.
    """
    # This model aggregates information about 
    ticker: str = Field("Ticker of the index (Often starts with `IC` or `NY`)")
    available_events: list[EventType]
    exchanges: list[str]
    starting_universe: StartingUniverse
    # is_factset_index: bool
    # initial_security_selection: SecurityUniverseSelection = Field(description="Initial list of securites are used to later filter and find final ones.")
    dates_info: DateInfo = Field(description="The logic of dates associated with index rebalancing or reconstitution of a term or quarter. It shoould never be a static date.")
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
    
class IndexDate(BaseModel):
    effective_date: datetime.date
    reference_date: datetime.date = Field(description="The date on which data is pulled.")
    sharestrike_date: datetime.date = Field(default=None)
    annoucement_date: datetime.date

class IndexDates(BaseModel):
    dates: list[IndexDate]

class AICrew:
    def __init__(self):
        self.methodology_reader: AIAgent
        self.date_analyser: AIAgent

this_year = datetime.date.today().year
# Please note: If share strike date is empty, then pass None

class Prompts:
    prompts_dir = Path("./prompts")
    
    def __init__(self) -> None:
        self.today = datetime.date.today()
        self.this_year = self.today.year
        
    
    @property
    def methodology_read_sys_prompt(self) -> str:
        index_info_path = self.prompts_dir / "methodology_read_sys_prompt.txt"
        return index_info_path.read_text()
    
    @property
    def date_analyser_sys_prompt(self) -> str:
        years_to_pick = f"{self.this_year-1}, {self.this_year}, and {self.this_year+1}"
        path = self.prompts_dir / "date_analyser_sys_prompt.template"
        return path.read_text().format(years=years_to_pick)

class Index():
    def __init__(self) -> None:
        self._prompts = Prompts()
        self.ai_crew = AICrew()
        self.ai_crew.methodology_reader = AIAgent(role=self._prompts.methodology_read_sys_prompt)
        self.ai_crew.date_analyser = AIAgent(role=self._prompts.date_analyser_sys_prompt)
        self.methodology_doc: PDFReader
        self.info: IndexBaseInfo
      
    def read_methodology(self, path: Path) -> IndexBaseInfo:
        self.methodology_doc = PDFReader(path)
        self.info = self.ai_crew.methodology_reader.ask(
            self.methodology_doc.read(), 
            IndexBaseInfo
        )
        
    def decide_dates(self) -> None:
        # You are an expert in date logic. Your task is to determine the following dates for index rebalancing or reconstitution for each quarter of the years 2023, 2024, and 2025:
        date_identifier_usr_prompt = f""" 
        * **Effective Date:** {self.info.dates_info.effective_date}.
        * **Reference Date:** {self.info.dates_info.reference_date}.
        * **Share Strike Date:** {self.info.dates_info.sharestrike_date}.
        * **Announcement Date:** {self.info.dates_info.annoucement_date}.
        """
        # ISSUE FOUND SHARE STRIKE DATE IS NOT PICKED CORRECTLY: Few Shot prompting to be used to fine tune
        # MAKE SURE: if Nth preceeding days is mentioned. Calculate them by counting down from mentioned date.
        index_dates: IndexDates = self.ai_crew.date_analyser.ask(
            user_prompt=date_identifier_usr_prompt,
            response_model=IndexDates
        )
        self.date_manager = index_dates
        # check for holidays in db and adjust the dates accordingly
        return

  
idx = Index()
# idx.read_methodology(path="NYSE_FactSet_Global_Cyber_Security_Index_Methodology.pdf")
idx.read_methodology(path=Path("NYSE_FANGplus_Index_Methodology.pdf"))
idx.decide_dates()




