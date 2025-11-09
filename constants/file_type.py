from typing import Final, List

class FileTypeConstant:
    """File types."""
    CV: Final[str] = "cv"
    PDF: Final[str] = "pdf"
    DOCX: Final[str] = "docx"
    DOC: Final[str] = "doc"
    TXT: Final[str] = "txt"
    RTF: Final[str] = "rtf"
    HTML: Final[str] = "html"
    XML: Final[str] = "xml"
    JSON: Final[str] = "json"

    ALLOWED_EXTENSIONS: Final[List[str]] = [CV, PDF, DOCX, DOC, TXT, RTF, HTML, XML, JSON]