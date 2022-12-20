from .gh import GH

def Generate(access_token:str, limit:int, force_regenerate:bool):
    gh = GH(access_token = access_token)
    gh.verify()