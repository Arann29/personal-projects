from dataclasses import dataclass


@dataclass
class Rule:
    pattern: str
    category: str


RULES = [
    Rule("uber|taxi|bus|metro|gas", "Transport"),
    Rule("super|maxi|market|grocery|billa|spar", "Groceries"),
    Rule("netflix|spotify|prime|subscription", "Subscriptions"),
    Rule("restaurant|cafe|coffee|burger|pizza", "Dining"),
    Rule("pharmacy|doctor|hospital", "Health"),
]
