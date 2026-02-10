from ninja import Schema


class LoginSchema(Schema):
    username: str
    password: str