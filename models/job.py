import math


class Job:

    def __init__(
        self,
        title,
        company,
        description,
        url,
        source,
        status="new",
        score=0,
        recommended=False,
        matched_positive=None,
        matched_negative=None,
        ai_summary=None
    ):

        self.title = title
        self.company = company
        self.description = description
        self.url = url
        self.source = source

        self.status = status
        self.score = score
        self.recommended = recommended

        self.matched_positive = matched_positive or []
        self.matched_negative = matched_negative or []

        self.ai_summary = ai_summary

    @staticmethod
    def _sanitize(value):

        if value is None:
            return None

        if isinstance(value, float):
            if math.isnan(value) or math.isinf(value):
                return None
            return value

        if isinstance(value, (int, bool)):
            return value

        return str(value).strip()

    def to_dict(self):

        return {
            "title": self._sanitize(self.title),
            "company": self._sanitize(self.company),
            "description": self._sanitize(self.description),
            "url": self._sanitize(self.url),
            "source": self._sanitize(self.source),

            # pipeline fields
            "status": self.status,
            "score": self.score,
            "recommended": self.recommended,
            "matched_positive": self.matched_positive,
            "matched_negative": self.matched_negative,
            "ai_summary": self.ai_summary,
        }