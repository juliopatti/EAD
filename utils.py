from urllib.robotparser import RobotFileParser

def pode_rastrear(url: str, user_agent: str, robots_url: str) -> bool:
    """
    Verifica no robots.txt se o user-agent tem permissão para acessar a URL dada.
    """
    rp = RobotFileParser()
    rp.set_url(robots_url)
    rp.read()
    return rp.can_fetch(user_agent, url)