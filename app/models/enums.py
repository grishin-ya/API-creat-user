import enum


class OrgRole(str, enum.Enum):
    hr = "hr"
    mentor = "mentor"
    lead = "lead"


class UserType(str, enum.Enum):
    organization = "organization"
    intern = "intern"


class InternshipStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"


class EnglishLevel(str, enum.Enum):
    beginner = "Beginner / Elementary"
    pre_intermediate = "Pre-Intermediate"
    intermediate = "Intermediate"
    upper_intermediate = "Upper-Intermediate / Advanced"